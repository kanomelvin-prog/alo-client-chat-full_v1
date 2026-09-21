# S7c identity and private session report v1.0

Brief #3-client-c v1.0 (identity handshake, private-session semantics, copy). Branch `auto/s7-client-identity`, created from `main` at `a535f1e` before any file was touched. Session ran 2026-09-20 (Claude Code, Fable 5.1, effort max). Nothing was pushed to `main`. `index.html` and `styles.css` are untouched. The change is in `dev.html` and `dev.css` (so `dev.css?v=15` became `?v=16`), plus this report. Code commit: `b9bed6b`. Line numbers below are `dev.html` on this branch (5,137 lines) unless marked `main:`.

## 0. Session log and deviations

1. **Launch.** The launch instruction arrived as pasted text with nothing typed beside it, so it was confirmed with Kano before anything ran. That is the only stop; the rest ran unattended.
2. **Read order followed:** `CLAUDE.md`; `docs/reports/S7_client_fixes_session_report_v1_0.md`; `docs/reports/S7b_path_r_session_report_v1_0.md`; `dev.html` in full (all 4,803 lines on `main`) before the first edit; then the parts of `dev.css` the banner and the About modal use.
3. **Third-party code was read, not guessed.** Botpress webchat `v3.3/inject.js` and `v3.3/webchat.js`, and `@supabase/supabase-js@2.39.0` UMD, fetched from their public CDNs into the session scratchpad (anonymous GET). What they show decides most of the design, so it is set out in section 2. No call was made to the live Supabase API or to Botpress Cloud: every harness run answered all requests locally, with outside hosts blocked at the browser.
4. **"The message composer" is Botpress's, not the page's.** Task B reads as if the page owned a composer it could disable. It does not: the composer is inside the webchat, and the webchat has no setting for it (its own disabled state follows its connection and nothing else). The webchat does run in a same-origin `about:blank` iframe, so the page holds the composer there. How, and how it fails, is in section 2 (B). This is the one part of the change that reaches into third-party DOM, so it was also run against the real v3.3 bundles (section 5).
5. **`sendIdentityToBot(reason, opts)` takes an optional second argument.** A private start or end has to send the *new* `privateSession` value while the page is still in the old state (D and E both say the page follows only after the bot confirms). So those two callers pass `{ privateSession: true | false }`. Every other send carries the value the bot last confirmed, which is `isPrivateSession` at every moment except inside those two transitions. Section 2 (A) says why it is not simply `isPrivateSession`.
6. **E, the order inside `endPrivateSession()`.** The brief says: send `'false'` and verify, then `await startNewConversation(true)`, and clear the local private state only after the bot confirms. Done in that order, with one refinement: the page keeps treating what arrives as private until the restart has *completed*, and clears its state then. Clearing it between the confirmation and the restart would let a reply that is still on its way for the private conversation be written to history (harness `private_end_late_reply`: `main` saves it). For the same reason `endPrivateSession()` calls the restart routine directly (`_aloRestartConversation()`, the body `startNewConversation()` also ends in) rather than `startNewConversation(true)`, which would otherwise call back into `endPrivateSession()`.
7. **Two reasons on the connected path, `startup` and `refresh`.** supabase-js re-emits `SIGNED_IN` whenever the tab comes back, and each one re-runs `loadConnectedState()` with a new nonce (S7 report, section 7). Only the first handshake of a page load holds the composer and can toast. Later ones refresh the identity under a composer that stays usable: disabling it mid-conversation would drop focus and close the phone keyboard on someone who is typing.
8. **`getUser()` has the same 8 s cap as `updateUser()`.** Without one, a read that never answers would hold the composer for good. Worst case on a network that hangs rather than fails: about 32 s (two attempts, two calls each) before the composer is released with the toast. A network that fails outright gets there in well under a second.
9. **The read-back compares `clientId` as well** as `sessionNonce` and `privateSession`. Same request, so it costs nothing.
10. **An identical object is not sent twice.** If the bot has already confirmed exactly the object about to be sent, the function logs `[Alo] Identity already verified with Botpress (reason)` and returns `true` without a request. That is what keeps the replaced bridge fallback (next point) from doubling every handshake.
11. **Copy that the brief did not supply** (section 4): the failure line for a private session that could not be ended, and the menu item that used to read "Go private from this point on". Both need Kano's eye.
12. **`dev.css` changed**, for F, G and H (section 2). The brief allowed it "only if a fix needs it"; each rule is tied to one of those three.
13. **F: the dead X could not be reproduced.** Section 3 says exactly what was tried, what was found instead, and what was changed.
14. **This repo is public.** The report describes what the page and the published SDK bundles do. It says nothing about the database beyond what the page's own source shows.

## 1. Summary

| Task | What changed | Where | Harness |
|---|---|---|---|
| A | One identity function, `sendIdentityToBot()`: the complete five-key object every time, awaited (8 s), read back with `getUser()`, one retry, the two log lines. Replaces the un-awaited `updateUser` in `loadConnectedState()` and the `clientId`-only fallback in `sendAuthBridge()`; `_aloSetBotPrivateFlag()` is gone (generalised into it). Nothing is sent to the SDK before `webchat:initialized`, and nothing sends `userKey` | 2562-2670 | `startup_*`, `concurrent_entries`, `refresh_*`, `homework_identity` |
| B | On the connected path the composer is disabled with placeholder "Connecting…" from its first paint until the startup handshake settles. On failure it is released with the brief's constant toast. Guest and signed-in-without-a-link pages are untouched | 2480-2489, 2672-2697, 2700-2810 | `startup_verified`, `startup_fails_twice`, `startup_hangs`, `signin_without_reload`, `guest_unaffected`, `nolink_unaffected` |
| C | At page load `isPrivateSession`, the bot-side value and `alo_private_active` are all cleared, and the startup send says `privateSession: 'false'` | 1412-1421, 4609 | `reload_private_marker`, `stuck_private_no_marker`, `private_reload` |
| D | Private ON always starts a new conversation, the bot confirmed first. The mid-thread banner, toast, tip, confirm text and menu label are gone | 3712-3738 | `private_start`, `menu_private_toggle`, `new_private_while_private`, `private_start_fails` |
| E | Private OFF: `'false'` sent and verified, then a new normal conversation, then "Private session ended — starting fresh." Local private state is cleared only after that. One path for the X, the menu, the popover and "New conversation" | 3746-3770, 3846-3868 | `private_end_x`, `private_end_fails`, `private_end_late_reply`, `new_conversation_while_private` |
| F | Banner lifted above the webchat overlay; X is 44x44; see section 3 | `dev.css` 2224-2295 | `f_banner_x`, `f_banner_x_nobar`, `f_banner_x_overlay` |
| G | Banner copy, in the markup and in `ALO_PRIVATE_BANNER_TEXT` | 317, 3697 | `private_start` |
| H | "What gets saved" table, three rows, directly under "How memory works" | 234-271, `dev.css` 2968-3006 | `about_table` |
| I | The auth bridge goes out after init and after the handshake. `_aloInitBotpress()` returns a promise | 544-552, 2944-2989, 4632-4635, 4667, 4689, 4806, 4916 | `bridge_order`, `fast_supabase_cold_webchat` |
| J | `python3 scripts/scan-invisible.py dev.html dev.css`: `CLEAN`, exit 0, before the code commit and before this report's | - | - |

Harness totals (section 5): the branch passes 38 of 38 scenarios in every configuration it was run in, the real Botpress v3.3 bundles included. `main` fails the 28 that encode a finding and passes the 10 controls, on the stand-in and on the real bundles alike.

## 2. Task by task: before and after

### What the SDK actually does (this decides A, B and I)

Read from the v3.3 bundles:

| Fact | Consequence |
|---|---|
| Before `webchat:initialized`, `updateUser()` only merges into a local copy of the user (`this.user = merge(this.user, patch)`). `getUser()`, `sendEvent()`, `sendMessage()`, `config()` and `restartConversation()` throw "Botpress webchat is not initialized" | Nothing sent before init can be verified |
| `webchat.js` snapshots `{configuration, user}` when it is evaluated and init PUTs that snapshot's user data. A pre-init `updateUser()` that comes after the snapshot is not in it | The identity can miss init's PUT |
| When init creates a new Botpress user it then sets `window.botpress.user` to the created user, discarding the local copy | With a new Botpress user the pre-init identity is thrown away |
| If the snapshot's user has a `userKey`, init uses it as the Botpress user's own key | `main`'s bridge fallback sent `userKey: clientId`. If that ran before the webchat script was evaluated, init tried a Supabase user id as a Botpress key and the webchat never initialised |
| After init, `updateUser(patch)` merges the patch into its copy, PUTs the whole `data` object to `/users/me` and keeps the returned user; `getUser()` GETs `/users/me` | Verify with `getUser()`, as the brief says |
| Botpress keeps user data across reloads | A key that is left out keeps its last value, which is how `privateSession: 'true'` outlived its session |
| `sendEvent`, `sendMessage` and `restartConversation` become real only when the conversation client has connected, which is *later* than `webchat:initialized`. `webchat:ready` is emitted then | The bridge has to wait for more than init (I) |
| The composer is `div.bpComposerContainer > div.bpComposerInputContainer > textarea.bpComposerInput[aria-label="Message Input"]`; its `disabled` prop is `disableComposer \|\| isReadOnly \|\| !connected`, and `disableComposer` is wired to the connection state only. The iframe has no `src` | No setting disables the composer; its DOM is reachable from the page (B) |

Both of `main`'s failure modes were reproduced against the real bundles (section 5): with Supabase answering faster than the webchat script loads, the webchat never initialises (`fast_supabase_cold_webchat`); with a newly created Botpress user, the bot sees neither `clientId` nor `sessionNonce` on the first message, and the first update that reaches it carries `clientId` alone (`startup_new_bp_user`). The second is the Sep 20 "signed-in user treated as guest".

### A - One identity function

| | Before (`main`) | After |
|---|---|---|
| Startup send (`main:2455`) | `window.botpress.updateUser({ data: { sessionNonce, clientId, homeworkActive, timeZone } })`: not awaited, no `privateSession`, usually before init, then logged as "sent" | `sendIdentityToBot('startup')` from `_aloRunIdentityHandshake()` (2672), which first awaits `_aloInitBotpress()` |
| Bridge fallback (`main:2637`) | `updateUser({ userKey: clientId, data: { clientId } })`, un-awaited, on every attempt | `sendIdentityToBot('auth-bridge')`, once per bridge (2989); normally answered from point 0.10 without a request |
| Private flag | `_aloSetBotPrivateFlag()`: one field, checked against `window.botpress.user`, and a missing `data` accepted | the same function with `{ privateSession: true \| false }`; a missing `data` is a mismatch (Kano confirmed live on Sep 20 that `getUser` reads the data back) |
| The object | four keys at startup, one at a private change, one in the fallback | always `clientId`, `sessionNonce`, `privateSession`, `homeworkActive`, `timeZone` (`_aloBuildIdentityData()`, 2597), rebuilt on each attempt |
| Verification | none at startup | `getUser()`, comparing `clientId`, `sessionNonce` and `privateSession`; one retry on a mismatch, an error or a timeout |
| Logs | "Identity + homework sent to Botpress via updateUser" whether or not anything arrived | `[Alo] Identity verified with Botpress (reason)` only after the read-back matches, or `[Alo] Identity NOT verified after 2 attempts (reason)`. The nonce is never logged |

Three things the function does that the brief does not spell out, each closing a race the harness shows on `main`:

- **Sends run one at a time** (`_aloIdentityQueue`). Two `loadConnectedState()` calls at once are normal here (the `SIGNED_IN` listener and the explicit call after sign-in). Un-serialised, each would re-send its own nonce when it read back the other's.
- **The page's nonce changes only once its row is written** (2522-2533). `main` assigned `sessionNonce` before the `session_metadata` write, so with two entries in flight the first could send the second's nonce before that row existed (`concurrent_entries`, `main` column). A7/C1's write-before-confirm now holds for concurrent entries too.
- **`privateSession` is the value the bot last confirmed** (`_aloBotPrivate`), changed only inside the function, on a verified send. It equals `isPrivateSession` except inside a private start or end. If it were read from `isPrivateSession`, an identity refresh landing while a private session is ending (bot already `'false'`, page still guarding its writes, see 0.6) would put `'true'` back, and the page would then leave private mode with the bot still in it, which is the Sep 20 stuck state by another route (`refresh_during_private`).

After a private start or end that could not be verified, the function is called once more without the override (`private-start-undo`, `private-end-undo`), so that an attempt which timed out here but landed there is taken back (`private_start_lands_but_times_out`).

Left alone on purpose: `_aloEndBotpressIdentity()` (1332), S7's blanking of the Botpress user at Log Out. It is not identity delivery, it is time-boxed at 2 s, and the webchat is torn down straight after.

### B - The composer waits for the handshake

`loadConnectedState()`, past the consent gate: `_aloHoldComposer()` (2757), then `_aloInitBotpress()`, then the reads it always made, then the `session_metadata` write, then `_aloRunIdentityHandshake()`. The handshake runs *behind* `loadConnectedState()` rather than being awaited by it, because the sign-in and connect modals stay open until that function returns (`signin_without_reload` checks the modal is not kept open).

The hold (2700-2810): while held, every message box in the webchat's document gets `disabled` and the placeholder "Connecting…", and `.bpComposerContainer` gets `pointer-events: none`, which also covers the send and voice buttons. A `MutationObserver` on that document re-applies it, because the webchat re-renders, flips `disabled` itself when its conversation connects, and can re-mount the box. It writes only when a value differs, so it settles. The `webchat:initialized` handler attaches it *before* `window.botpress.open()` (4684-4685), so the box is never usable ahead of the hold. Release puts back the webchat's own placeholder and the `disabled` state the webchat last asked for.

It fails open, never closed: no iframe, a changed DOM or an exception leaves the composer as the webchat made it. It is released when the handshake settles either way, when a `loadConnectedState()` that armed it fails before reaching its handshake (2553), and by a 45 s timer whatever happens.

On failure: composer enabled, and the brief's constant, **"Alo may not recognize you on the first message. If it doesn't, reload the page."**, once. A failed `session_metadata` write is reported the same way. The handshake still runs then (it states `privateSession` and carries any nonce the page already holds), but with no row for the bot to check the nonce against it is not called verified.

### C - Startup is explicit about private

`_aloClearPrivateStateOnLoad()` (1412) runs at the top of `DOMContentLoaded` (4609): `isPrivateSession = false`, `_aloBotPrivate = false`, and `alo_private_active` is read into `_aloPrivateReload` and removed. On `main` the marker was removed only inside `_aloPrepareBotpressStorage()`, that is, only if the chat initialised. What the marker *said* still does S7's job: a page reloaded mid-private starts a fresh Botpress user, so the private conversation is never resumed into history (`private_reload`, `reload_private_marker`). The startup send then carries `'false'`, which un-sticks the Sep 20 state for the case the marker does not cover: same Botpress user, `'true'` left behind, no marker (`stuck_private_no_marker`: on `main` the bot's first turn still sees `'true'`).

### D - Private ON = new conversation

`startPrivateSession()` (3712): bot confirms `'true'`; `isPrivateSession = true` and the marker, *before* the restart so nothing of the new conversation is ever written, a greeting included; `await startNewConversation(true, { keepPrivate: true })`, now unconditional; then banner, toast, tip. `startNewPrivateConversation()` (3794) is now the memory-off check plus that same function. While already private it starts the next private conversation, and the bot already holds `'true'`, so that is just the restart.

Removed: `_aloPrivateScope`, `_aloConvFresh`, `_aloEnterPrivate()`, and every "from this point on" string (section 4). On failure: no banner, no flag, no restart, the existing constant line.

### E - Private OFF = new conversation

`endPrivateSession()` (3746) is now `async`: `sendIdentityToBot('private-end', { privateSession: false })`; if it is not confirmed, nothing changes (still private, banner up, new constant failure line, no restart); then the restart; then `isPrivateSession = false`, marker removed, UI updated, toast. `startNewConversation()` (3846) during a private session shows its confirm and then *is* `endPrivateSession()`: one path.

One small consequence: "Bring this to Alo" (4419) now stops if `startNewConversation(true)` returns `false`. Otherwise a private session that could not be ended would have the journal entry sent into it 1.5 s later.

### G, H - Copy

Section 4. H is a two-column table (mode, what it saves) so that it fits a 375 px sheet, with `<th scope="row">` for each mode. The About modal had no table styles, so `dev.css` gained one small block, custom properties only. The sentence that platform-side deletion is not yet in place is unchanged.

### I - Auth bridge ordering

| | Before | After |
|---|---|---|
| Call site | inside `loadConnectedState()`, straight after the un-awaited `updateUser`, normally before init | at the end of `_aloRunIdentityHandshake()` (2695): after `_aloInitBotpress()` has resolved and after the identity has settled, verified or not |
| Guard in `sendAuthBridge()` | `typeof window.botpress.sendEvent !== 'function'`, which is never true (the stub is a function), so the bridge fired into the stub and threw | `window.botpress.initialized === true` and `webchat:ready` seen. If `webchat:ready` never comes it is tried anyway after ~10 s and the existing 1 s retry takes over |
| `sendEvent()` rejecting | after init it is `async`; a rejection was unhandled | handled: same warning, same retry |
| `_aloInitBotpress()` | returned nothing | returns a promise: `true` at `webchat:initialized`, `false` if `init()` threw. The SDK sets `initialized` right after that event returns, and whoever awaits the promise continues after that |

The bridge is not removed. `bridge_order` asserts `initialized < identity verified < bridge`, one bridge, no "not initialized" warning, and that the bot already held the nonce when the bridge arrived.

## 3. F - the banner's X: root cause

**I could not reproduce a dead X, and I am not going to name a cause I did not observe.**

What was tried, all on `main@a535f1e` in headless Chrome, with every tap hit-tested (`elementFromPoint` at the button's centre, then a click on whatever is there, which is what a finger does): 375, 390, 500 and 1280 px; privacy bar showing and dismissed; the one-time private tip showing and already seen; private mode started from the menu and from the eye icon's popover; against the Botpress stand-in and against the real v3.3 bundles. In every case the tap landed on `button.private-session-end`, `endPrivateSession()` ran, the banner hid and "Private session ended" showed (`f_banner_x` and `f_banner_x_nobar` pass on `main`). There is one `#privateSessionBanner` in the file, one `endPrivateSession`, nothing on the button's scope chain that shadows it, and no `pointer-events` rule on the banner. Of the brief's three candidates, a second banner and an unreached handler are ruled out for this file. The third, z-index, is where the evidence points, and it is below.

What I did find:

1. **The banner was the one bar above the chat that was not lifted over the webchat overlay.** `.bpWebchat` is `position: fixed; z-index: 10`, laid over `.chat-container` by JavaScript that re-measures on resize events. The homework bar has `position: relative; z-index: 20` and the old private button had `z-index: 11 /* above .bpWebchat (z:10) */`: someone met this overlap before. The banner had neither, so anywhere the overlay and the banner overlap, the overlay takes the tap. In Chrome the overlay is re-measured correctly when the banner appears, so they do not overlap. `f_banner_x_overlay` forces the overlap: on `main` the tap goes into the webchat and the X is dead; on the branch the X wins. Whether the live page gets into that state I could not establish. The plausible routes are engine-specific (an iOS Safari fixed-position iframe keeping a stale hit region after being moved by a style change), and none can be tested here.
2. **The X was 30x30 px with a 12 px glyph** at phone widths (the generic phone-width button rule overrode its padding and font size), against this repo's 44x44 rule.
3. **On `main` the X visibly did very little even when it worked.** It flipped the page's flag and fired `privateSession: 'false'` without waiting; the conversation carried on in the same thread. The bot loads memory on the first turn that carries a verified identity, so a thread that began private stays without memory after the X. From the user's side: tap X, Alo behaves exactly as before. That is a candidate for what "does nothing" looked like, and E changes it: the X now ends the conversation, starts a fresh one and says so.
4. Separate, but it produces the same symptom one header up: the one-time tips (`.alo-contextual-tip`: fixed, full width, `z-index: 8000`, top of the screen, up to 8 s) lie over the header, and a tap that lands on one only dismisses it. Right after a first-ever private start, the first tap on the menu button does nothing. It does not reach the X at 375 to 500 px (the tip ends about where the banner begins). Not changed (section 7).

What was changed for F (`dev.css`): the banner is `position: relative; z-index: 20` with an opaque background (the tint laid over the page background, so nothing beneath can show through); the X is 44x44 with a 20 px glyph, scoped by id so it outranks the phone-width button rule without `!important`.

**What would settle it:** Kano's check 4 in section 8. If the X is still dead on a device after this change, one line in the console while it is dead names the element taking the tap: `document.elementFromPoint(x, y)` at the X's position.

## 4. Copy: before / after

| Where | Before | After | Source |
|---|---|---|---|
| Private banner (317, 3697) | Private session — Alo won't remember this conversation | Private session — nothing here is saved or remembered. If you're in danger, Alo still sends your therapist a safety alert, never your words. | brief G, verbatim |
| Private banner, mid-conversation | Private from this point on — Alo won't remember what you say next | (removed) | brief D |
| Private toast, mid-conversation | Private from this point on — what you say next won't be remembered | (removed) | brief D |
| Private tip, mid-conversation | From this point on, nothing goes into your history or memory. | (removed) | follows from D |
| New-conversation confirm, mid-conversation private | Anything from before you went private stays in your history; nothing after that is kept. | (removed; the whole-conversation line is the only one) | follows from D |
| Menu item (161, 3787) | Go private from this point on | **Start private session** | **mine**: the old label is false now. It matches the popover's existing "Start private session" |
| Private session ended | Private session ended | Private session ended — starting fresh. | brief E, verbatim |
| Identity not verified (2591) | (nothing; silent) | Alo may not recognize you on the first message. If it doesn't, reload the page. | brief B, verbatim |
| Private session could not be ended (3690) | (could not happen: the page ended it without asking the bot) | **Couldn't end the private session — nothing was changed. Try again.** | **mine**: mirrors the approved start-failure constant |
| Composer while held | Type your message... | Connecting… | brief B |
| About, "What gets saved" (236) | (absent) | **Normal:** Conversation history saved to your account (you can delete it) · Brief summaries so Alo remembers context · Journal saves when you ask · Safety alerts to your therapist, never your words. **Memory off:** History still saved · No summaries carried forward · Journal saves when you ask · Safety alerts still. **Private session:** Nothing saved — no history, no memory, no journal · Safety alerts still. | brief H, its wording kept |

Unchanged on purpose: the whole-conversation private toast and tip; the start-failure line; the memory-off hint; "Messages to your therapist can't be sent during a private session."

Two things for Kano to weigh. The banner and the table say "your therapist" to accounts that have none (a signed-in account with no link can start a private session); the brief gives one constant string, so it is used as given. And the menu now has "Start private session" and "Start new private conversation", which do the same thing when no private session is on (section 7).

The banner's text colour changed with its copy. `--accent` on the banner's tint is 2.38:1 in the light theme. It was already short of AA for the old one-liner; for a sentence about danger at 12 px it is not acceptable. The text and the X now use `--text-primary` (10.3:1 light, 11.1:1 dark). The eye icon keeps `--accent`.

## 5. Harness results

**Method** (the S4A-min / R-C / S7 pattern, rebuilt this session). Headless Google Chrome 153, a local `python3 -m http.server`, a fresh profile per run, every outside host blocked at the resolver. The harness copy of `dev.html` keeps the page's own CSP and replaces only the two CDN script tags. supabase-js is the **real 2.39.0 UMD**, served locally, with `window.fetch` answered by a local GoTrue/PostgREST emulation that logs every request. A driver works the real UI with hit-tested taps and samples the composer every 5 ms, as a person would meet it: not disabled, visible, on top, taps accepted.

Botpress, two ways:

- **Stand-in**, modelled on the v3.3 bundles point by point: pre-init stubs that throw or merge locally, the evaluation-time snapshot, the `userKey` branch, the restored and created user paths, `updateUser` and `getUser` against an emulated `/users/me` that keeps data across reloads, `sendEvent` and `restartConversation` real only after connect, the same composer DOM, and a bot that records what user data it saw on each turn. `updateUser` and `getUser` can be made to fail, hang, land-but-hang, or return a stale or data-less user, per call.
- **The real v3.3 `inject.js` and `webchat.js`**, served locally and unmodified apart from the three script URLs, with only the Chat API answered locally (`/users`, `/users/me`, `/conversations`, the event stream, `/messages`, `/events`), under the same failure hooks. This exercises the real React composer, the real `updateUser` / `getUser` wrappers, the real init order and the real `restartConversation`.

Emulated Supabase latency is 60 ms a request by default, so the seven sequential reads take longer than the webchat's init, as on the live site. The branch was also run at 0 ms, where they finish before the webchat script is evaluated.

**The brief's ten verification items:**

| # | Item | Scenario(s) | Result |
|---|---|---|---|
| 1 | Composer disabled until the stubbed `getUser` returns the nonce, then enabled; the object sent has all five keys with `privateSession: 'false'` | `startup_verified`, `startup_new_bp_user` | PASS. No sample shows a usable composer before the verifying `getUser`; "Connecting…" is seen while held; the placeholder is restored after; one `verified (startup)` line; the first message, sent at the first instant the composer accepts it, reaches a bot that holds the nonce. `main`: never held, no read-back, and the first turn sees neither `clientId` nor nonce |
| 2 | A stale nonce once → one retry → verified | `startup_stale_once` | PASS: two `updateUser`, two `getUser`, "read-back did not match (attempt 1, startup)", then verified; no toast |
| 3 | Failure on both attempts → composer enabled + toast; nothing else broken | `startup_fails_twice`, `startup_getuser_fails_twice`, `startup_nodata`, `startup_hangs` | PASS, all four: the NOT-verified line, the constant toast exactly once, composer usable, a message sent and saved to history, bridge still sent, no page error. `startup_hangs` releases at about 32 s |
| 4 | Start private → `'true'` sent and verified → new conversation → banner is the new copy | `private_start` | PASS: `updateUser('true')` < `getUser('true')` < `restartConversation`. The private turn reaches a bot holding `'true'` and the nonce; greeting, message and reply write no row |
| 5 | End via the X → `'false'` sent and verified → new normal conversation → toast | `private_end_x` | PASS: the tap lands on a 44x44 X; `updateUser('false')` < `getUser('false')` < restart; toast; banner gone, marker cleared; the next message is saved as a normal conversation and nothing of the private one is |
| 6 | Reload with `alo_private_active` set → cleared; startup says `'false'` | `reload_private_marker`, `stuck_private_no_marker`, `private_reload` | PASS |
| 7 | No "Private from this point on" string remains | `grep -ci` | 0, and 0 for "from this point on" in any case |
| 8 | The About modal contains the three-row table | `about_table` | PASS at 375, 390 and 500 px: directly under "How memory works", row heads Normal / Memory off / Private session, the deletion sentence kept, no sideways overflow |
| 9 | `sendAuthBridge` not called before init on the connected path | `bridge_order`, `fast_supabase_cold_webchat` | PASS. `main`: 1 `sendEvent` and 2 `updateUser` reach the SDK before init at 15 ms latency; at 0 ms the webchat never initialises |
| 10 | `scan-invisible.py` CLEAN | - | CLEAN, exit 0 |

**All scenarios.** Four columns: `main` and the branch, each on the stand-in and on the real bundles.

| Scenario | What it does | `main` | `main`, real SDK | Branch | Branch, real SDK |
|---|---|---|---|---|---|
| `startup_verified` | 15 ms latency, restored Botpress user; message sent at the first chance | FAIL | FAIL | PASS | PASS |
| `startup_new_bp_user` | same, no stored Botpress user | FAIL: the bot sees no identity on turn 1 | FAIL (same) | PASS | PASS |
| `startup_stale_once` | `getUser` stale once | FAIL | FAIL | PASS | PASS |
| `startup_fails_twice` | `updateUser` rejects twice | FAIL: silent, plus two unhandled rejections | FAIL | PASS | PASS |
| `startup_getuser_fails_twice` | `getUser` rejects twice | FAIL | FAIL | PASS | PASS |
| `startup_nodata` | `getUser` returns a user with no `data` | FAIL | FAIL | PASS: not verified, toast | PASS |
| `startup_hangs` | `updateUser` never answers, twice | FAIL | FAIL | PASS | PASS |
| `startup_update_timeout_once` | first `updateUser` hangs, the retry answers | FAIL | FAIL | PASS: verified at about 8 s, no toast | PASS |
| `startup_metadata_write_fails` | the `session_metadata` write fails | FAIL: silent, and keeps a nonce that was never written | FAIL | PASS: `'false'` still stated, toast, no unwritten nonce kept | PASS |
| `startup_profile_read_throws` | a profile read fails mid-load | PASS (control) | PASS | PASS: the composer is not left held | PASS |
| `private_start` | item 4 | FAIL | FAIL | PASS | PASS |
| `private_end_x` | item 5 | FAIL | FAIL | PASS | PASS |
| `reload_private_marker` | marker set, stored user holds `'true'` | FAIL | FAIL | PASS | PASS |
| `stuck_private_no_marker` | the Sep 20 state: `'true'` left behind, no marker | FAIL: the bot's first turn sees `'true'` | FAIL | PASS | PASS |
| `about_table` | item 8 | FAIL | FAIL | PASS | PASS |
| `bridge_order` | item 9 | FAIL | FAIL | PASS | PASS |
| `f_banner_x` | the X, natural layout | PASS (control) | PASS | PASS | PASS |
| `f_banner_x_nobar` | same, privacy bar dismissed | PASS (control) | PASS | PASS | PASS |
| `f_banner_x_overlay` | the overlay forced over the banner | FAIL: the tap goes into the webchat | FAIL | PASS | PASS |
| `fast_supabase_cold_webchat` | 0 ms latency | FAIL: `userKey` reaches init; the webchat never initialises | FAIL (same) | PASS | PASS |
| `private_start_fails` | `'true'` cannot be sent | PASS (control) | PASS | PASS: no restart either | PASS |
| `private_start_lands_but_times_out` | `'true'` lands but never answers | FAIL | FAIL | PASS: taken back, the bot ends on `'false'` | PASS |
| `private_end_fails` | `'false'` cannot be sent | FAIL: the page leaves private mode regardless | FAIL | PASS: still private, banner up, no restart; a second try works | PASS |
| `private_end_late_reply` | X tapped while a reply to a private message is on its way | FAIL: the reply is saved to history | FAIL (same) | PASS | PASS |
| `private_reload` | reload mid-private (S7 regression) | FAIL (startup does not say `'false'`) | FAIL | PASS | PASS |
| `refresh_reentry` | `loadConnectedState()` again mid-conversation | FAIL (four keys) | FAIL | PASS: composer usable throughout, no toast | PASS |
| `refresh_during_private` | refresh while private; then end and refresh at once | PASS (control) | PASS | PASS | PASS |
| `concurrent_entries` | two entries at once | FAIL: a nonce sent before its row was written | FAIL | PASS | PASS |
| `guest_unaffected` | guest page | PASS (control) | PASS | PASS: never held, no identity calls | PASS |
| `nolink_unaffected` | signed in, no link | PASS (control) | PASS | PASS | PASS |
| `new_conversation_while_private` | "New conversation" during a private session | FAIL | FAIL | PASS: one path | PASS |
| `new_private_while_private` | "Start new private conversation" while private | PASS (control) | PASS | PASS | PASS |
| `menu_private_toggle` | menu on, menu off | FAIL (label; no restarts) | FAIL | PASS | PASS |
| `memory_off_private` | memory off, both entry points | PASS (control) | PASS | PASS | PASS |
| `homework_identity` | active homework | FAIL (four keys, unverified) | FAIL | PASS | PASS |
| `logout` | Log Out (S7 regression) | PASS (control) | PASS | PASS | PASS |
| `gate_with_consent` | unconsented link, consent, then chat | FAIL | FAIL | PASS: nothing behind the gate; held then verified after it | PASS |
| `signin_without_reload` | a guest page signs in through the modal | FAIL | FAIL | PASS: the running composer is held then released; the modal is not kept open | PASS |

Totals: branch 38/38 on the stand-in at 60 ms, 38/38 at 0 ms, 38/38 on the real bundles, with 0 page errors or unhandled rejections; `main` 10/38 on both. The 10 are the controls. So that the `main` column is not over-read: every `main` run past the `startup_*` block carries the absence of the five-key object and the read-back as well as its own finding.

Phone widths (`CLAUDE.md`: 375 and 390): `startup_verified`, `private_start`, `private_end_x`, `about_table`, `f_banner_x_nobar`, `f_banner_x_overlay` and a banner-geometry check were run in a 375 px and a 390 px frame on both Botpress configurations: 28 of 28 pass. Screenshots in both themes: the banner wraps to three lines at 375 px with the X whole and at the right; the table fits at 375 px; nothing scrolls sideways. The held composer was also screenshotted on the real webchat, where it shows "Connecting…" in the webchat's own disabled style.

Harness artefacts, fixed in the harness and not in the page: `--dump-dom` produces no frames, so CSS animations never advance and a bottom sheet stays off-screen (motion is switched off in the harness copy); headless Chrome fires `beforeinstallprompt`, and the Android install banner then sits over a guest's composer (seeded as dismissed); `new Response('', { status: 204 })` throws in Chrome (the emulator now sends a null body).

## 6. Not verifiable without live credentials or a device

1. **Live Botpress Cloud.** That `GET /users/me` returns `data` with the keys as sent (Kano's Sep 20 check says so); how long `updateUser` plus `getUser` take on mobile data, which is how long "Connecting…" shows on every connected load; and that the bot reads the five keys as the brief's section 1 describes. The Chat API was emulated in both tiers.
2. **The composer hold on real devices.** Verified against the real v3.3 DOM in Chrome. iOS Safari's handling of a `disabled` textarea inside the iframe, VoiceOver's reading of it, and Firefox (where the SDK rewrites the iframe document; the watch re-attaches at `webchat:initialized` for that reason) were not run. If Botpress changes the composer's class names under the same `/v3.3/` URL, the hold quietly stops applying and behaviour is `main`'s; nothing breaks.
3. **F on a device.** Section 3.
4. **A greeting at conversation start.** Whether the live bot sends one is still unknown. Both orders are safe: a private conversation's greeting is never written, and a normal conversation's is.
5. **Supabase RLS** for the `session_metadata` write and every read this path makes: unchanged by this session, and not re-verified.

## 7. Declined, and observations

Declined (out of scope by the brief): the parked branch; the consent flow; anything in the bot; S3/S4 UX polish.

Observations, not changed:

- **After a restart, the auth bridge is bound to the conversation just left.** On the real SDK, `sendEvent()` keeps the previous conversation's id until the webchat's next render, and the page calls it straight after `restartConversation()` resolves. In `private_end_x` on the real bundles the three bridge events carry `bpconv_1`, `bpconv_1`, `bpconv_2`, while the page was in `bpconv_1`, `bpconv_2`, `bpconv_3`. `main` does the same, so this is not new, but D and E now put a restart behind every private toggle. I left it alone deliberately. Identity rides on user data, which the bot reads on every turn, so nothing depends on the bridge reaching the new conversation; and changing which conversation the bot's trigger fires in is a bot-facing behaviour change I cannot check live, days before a demo. The fix is small if wanted: after the restart, wait until `window.botpress.sendEvent` is a different function before sending.
- **Signed-in accounts with no link** still send no identity at startup (R-C-21, unchanged), so C's `'false'` reaches them only at their next private toggle or new conversation. To the bot they are guests either way. Their private start and end now send the full object with an empty nonce.
- **Two menu items now do the same thing** when no private session is on: "Start private session" and "Start new private conversation". While private they differ (end, versus the next private conversation). Hiding the second until a private session is on would be the smallest tidy-up.
- **One-time tips cover the header and swallow the first tap** (section 3, point 4).
- **The Android install banner sits over the composer** until it is dismissed (seen in the harness on a guest page).
- **The webchat's own header has Restart and Close buttons** that bypass the page's paths. Not examined.
- **Two tabs and a private session** (S7 observation): unchanged. A second tab still consumes the marker, now at load rather than at chat init.
- **The Log Out blanking** (`_aloEndBotpressIdentity`) still writes its own four-key object. It is the last write before the webchat is removed.
- `"padding: 8px 12px;"` is a tracked 103 KB file in the repo root: an old copy of `dev.html`, from the accidental rename in `b459461`. It is public with the rest of the repo. Not touched.

## 8. Kano's check on alowen.ai/dev.html (after merge)

1. **Startup.** Signed in as a linked client, DevTools console open, reload. Expect: the composer reads "Connecting…" for a moment, then "Type your message..."; one `[Alo] Identity verified with Botpress (startup)`; then `[Alo] Auth bridge sent to Botpress`; and **no** "Botpress webchat is not initialized". Type a first message as fast as you can: Alo should know you.
2. **The Sep 20 account.** Load the account that was stuck in private. Expect Alo to have memory again on the first message. In the console, `(await window.botpress.getUser()).data.privateSession` is `"false"`.
3. **Private on.** Menu > Start private session. Expect a *new* conversation, the new banner copy, and the toast. Send a message, open the sidebar: no new entry.
4. **The X.** Tap the banner's X on a phone. Expect a new conversation and "Private session ended — starting fresh." The sidebar then lists this conversation once you send a message, and nothing from the private one. If the X is still dead, note the device and browser, and in a desktop console run `document.elementFromPoint(x, y)` at the X's position while it is dead.
5. **Failure.** Block `webchat.botpress.cloud` in DevTools (Network > Block request domain) *after* the chat has loaded, then start a private session: after a few seconds, "Couldn't start a private session — nothing was changed. Try again.", no banner, the same conversation. To see the startup toast, hold Supabase's and the webchat's first responses with throttling: the composer must still open, with the toast.
6. **About > What gets saved** on a phone: three rows, nothing cut off.
7. **Copy for your review:** the menu item "Start private session", and the line "Couldn't end the private session — nothing was changed. Try again."
