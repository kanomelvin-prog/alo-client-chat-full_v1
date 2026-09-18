# S7 client fixes session report v1.0

Brief #3-client v1.0 (R-C fixes that do not depend on the database). Branch `auto/s7-client-fixes`, created from `main` at `64acefc` before any file was touched. Session ran 2026-09-18 (Claude Code, effort max, bypass permissions, unattended). Nothing was pushed to `main`. `index.html`, `styles.css` and `dev.css` are untouched (so no `?v=` bump); every change is in `dev.html`, plus this report. Line numbers below are `dev.html` on this branch (4,671 lines) unless marked `main:` (the R-C report cites `main@64acefc`).

## 0. Session log and deviations

1. **Model.** This session ran on Claude Opus 5 (`claude-opus-5`). The brief's run settings name Fable 5.1 and say to switch with `/model` after launch; a session cannot switch its own model, so this is recorded rather than acted on.
2. **Read order followed:** `CLAUDE.md`; `docs/reports/S4A-min_session_report_v1_0.md`; `git show auto/r-c-review:docs/reports/R-C_client_security_review_v1_0.md` (in full); `dev.html` in full (all 4,308 lines on `main`) before the first edit.
3. **`escHtml()` does not exist in this file.** The brief's fix E names it as existing; the HTML escaper here is `esc()` (line 536, `textContent` then `innerHTML`), which is what the R-C report's fix text uses too. `esc()` was used; no sanitizer library was added.
4. **Fix A says "see fix I for the mid-conversation case".** The mid-conversation wording lives in fix J (R-C-15), so it was read as J.
5. **"All ten self-checks listed in the report"** (verification item 6): the brief does not enumerate them. Fixes A-J are exactly ten, so this report defines one self-check per fix (section 4); K (the scan) ran before every commit.
6. **Third-party code was read, not guessed** (the brief requires this for B and F): Botpress webchat `v3.3/inject.js` and `v3.3/webchat.js`, and `@supabase/supabase-js@2.39.0/dist/umd/supabase.min.js`, fetched from the public CDNs into the session scratchpad (anonymous GET, no credentials). No call was made to the live Supabase API or to Botpress Cloud: every harness run answered all requests locally.
7. **Both client repos are public** (R-C section 0). This report names test inputs by what they do; the one literal string it quotes is the brief's own inert test value for fix D.

## 1. Summary

| Fix | Finding(s) | What changed | Commit | Harness |
|---|---|---|---|---|
| A | R-C-04 (S1) | a private session writes nothing; a reload ends it and starts a fresh, normal conversation | `d5dcc4f` | `private_whole`, `private_reload` |
| B | R-C-01 (S1), R-C-22 ride-along | Log Out ends the webchat, removes every Botpress storage key, blanks the Botpress user data, clears the two message queues and nulls every identity global before the reload; a stored Botpress user is reused only by its owner | `cc2ce69`, `52e40a0` | `logout`, `account_switch_token` |
| C | R-C-17 (S3, ride-along) | the two sign-out paths that did not reload now run the same cleanup and reload: single path | `cc2ce69`, `52e40a0` | `signout_broadcast`, `silent_session_loss`, `getuser_network_fail` |
| D | R-C-03 (S1) | the name editor sets the name as a property, never in `value="..."` | `f5e40be` | `xss_name` |
| E | R-C-09 (S2) | homework title/type/goal and the therapist's name are escaped at every `innerHTML` sink R-C lists | `f5e40be` | `xss_therapist` |
| F | R-C-06 (S1) | `detectSessionInUrl: false`; the `?t=` exchange already used `verifyOtp` explicitly | `5497ab6` | `token_exchange`, `foreign_fragment`, `foreign_query` |
| G | R-C-02 (S1) | the gate holds when any active link is unconsented; an `?invite=` claim while connected lands on it | `fe69b83` | `multilink_*`, `invite_while_connected` |
| H | R-C-11 (S2) | no invite code is stored before a sign-in attempt; only the account's own `user_metadata` code is claimed, then cleared; legacy local codes are dropped unread | `fe69b83` | `pending_invite_residue`, `login_wrong_password_invite`, `metadata_invite_claim` |
| I | R-C-07 (S2) | private mode turns on only after Botpress confirms (awaited, retried once, checked); constant failure copy | `d5dcc4f` | `private_flag_fails`, `private_flag_retry_ok` |
| J | R-C-13, -14, -15, -16 (S2) | claims corrected (section 3); "Guests start fresh every visit" made true by B's owner rule | `d5dcc4f`, `482ed96`, `cc2ce69` | `copy_render`, `private_midconv`, `memory_off_private`, `guest_fresh_visit` |
| K | hygiene | `python3 scripts/scan-invisible.py dev.html dev.css`: CLEAN, exit 0, before each of the 7 code commits and this report's | - | - |

Harness totals: the final build passes 26 of 26 scenarios; `main` fails the 19 that encode a finding and passes the 7 controls (section 5).

## 2. Fix by fix: before and after

### A - Private sessions persist nothing (R-C-04)

| Where | Before (`main`) | After |
|---|---|---|
| `ensureConversation()` (2367) | no private check: the first message of a private conversation inserted a listed `conversations` row with `is_private: true` (`main:4040-4045`, `2171`) | first statement is `if (isPrivateSession) return null;`; it also clears `_aloConvFresh` when it creates or resumes a row |
| message handler, call sites (4400, 4417) | always called `ensureConversation()`/`saveMessage()` | `if (!isPrivateSession) (async function() {...})();` and the retry's call site checks `!isPrivateSession` too. `saveMessage()` keeps its own check (2432) |
| message handler, dropped formats (4372) | the raw message object went to `alo_dropped_messages`, private or not | not written during a private session |
| `showMessageModal()` (1926) | a message to the therapist was POSTed to `client_messages` during a private session | refused at open and again at send with one constant line (section 3) |
| reload during a private session | the flag was page memory only; Botpress restored the same conversation and the `alo_conv_<id>` mapping resumed the private row, so the rest of the conversation was saved (`main:2137-2141`) | a private session sets `alo_private_active` (`ALO_PRIVATE_ACTIVE_KEY`, 1353). A page that loads with it set clears the Botpress storage before `botpress.init()` (`_aloPrepareBotpressStorage()`, 1395), so the reload ends the private session and starts a fresh Botpress user and a normal conversation; nothing of the private one is resumed or listed |
| `startNewPrivateConversation()` (3336) | restarted first, then flipped the flag (a greeting in between would be saved) | tells Botpress first (fix I), sets the flag and the marker, then restarts via `startNewConversation(true, { keepPrivate: true })`, so nothing of the new conversation is ever written |
| `endPrivateSession()` (3291) | un-awaited `updateUser`, unhandled rejection on failure | clears the flag, scope and marker; the `'false'` update is caught and logged |

Memory-summary trigger: the client has none. Summaries are built by the bot from `conversations` rows (`turn_count >= 4`, not private) and their `conversation_messages` (R-C section 2, Init_State 225, 262-266); both are now never written during a private session.

### B - Sign-out clears the bot identity (R-C-01; R-C-22 ride-along)

Key names were confirmed from the v3.3 bundles, not guessed. The webchat runs in a same-origin `about:blank` iframe and writes to this site's storage:

| Storage | Key | Holds | Source |
|---|---|---|---|
| localStorage | `bp-webchat-<webchat clientId>` | zustand `persist` store: `{user: {userId, userToken}, conversationId}`; restored at init (user and conversation) | webchat.js ``Is.getInstance(`bp-webchat-${be.clientId}`, storageLocation)``; storage is `sessionStorage` only if `storageLocation` says so (not set here) |
| localStorage | `botpress-message-history` | the user's own last ~100 sent messages, plaintext, for the composer's up-arrow recall | webchat.js store `Hk`, persisted with no storage option (zustand default: localStorage). Not listed in R-C |
| localStorage | `webchat-sound-<id>` | sound preference | webchat.js `Rs.getInstance` |
| sessionStorage | `bp-unread-message-count`, `bp-proactive-message-state`, `bp-composer-file-store` | unread count, proactive-message state, composer files | inject.js / webchat.js |

No IndexedDB and no cookies in either bundle. The store's own `clearAll()` exists but nothing calls it, so there is no SDK call that clears the identity.

| Where | Before | After |
|---|---|---|
| `handleLogout()` (1242) | `signOut()`, nulled `clientId`/`therapistLink`/`chatSettings`/`currentHomeworkId`, reloaded; Botpress untouched | `signOut()`, then `await _aloSignOutCleanupAndReload()` (1265). The SIGNED_OUT listener starts the same run; both wait on one promise |
| `_aloEndBotpressIdentity()` (1280, new) | - | 1) best effort, 2 s cap: `updateUser` blanks `clientId`, `sessionNonce`, `homeworkActive`, sets `privateSession: 'false'` on the Botpress side; 2) `botpressReady = false` (so the `webchat:closed` listener does not reopen), `botpress.close()`, `botpress.unmount('webchat')` (removes the iframe, so its in-memory store cannot write the key back; `components.webchat` confirmed in inject.js); 3) removes every key above from both storages; 4) removes `alo_bp_owner` |
| `_aloClearAccountState()` (1309, new) | - | nulls `clientId`, `therapistLink`, `sessionNonce`, `connectedTherapistName` (therapist name), `memoryGlobalEnabled`, `currentHomeworkId`, and via `resetPersistenceState()` `currentSupabaseConvId`; resets `chatSettings`, `activeHomework`, `isPrivateSession`, `authBridgeSent`, the in-flight create promise; removes `alo_unsent_messages`, `alo_dropped_messages` (R-C-22), the legacy `alo_pending_invite`, `alo_private_active` and every `alo_conv_*` mapping |
| reload | always, at the end | always, in a `finally` (`52e40a0`), so the page never stays up half-cleared |
| before `botpress.init()` (4189) | the stored user was always restored | `_aloPrepareBotpressStorage()` (1395): the stored Botpress user is reused only by the owner recorded in `alo_bp_owner`, which is `u:<Supabase user id>` for a signed-in page or `g:<tab visit id>` for a guest (`alo_guest_visit`, sessionStorage). Anything else, or a set private marker, clears the Botpress storage first. `_aloClaimBotpressOwner()` (2193, 2277) re-labels a guest webchat that signs in without a reload |

The owner rule is what makes "after reload a guest gets a fresh Botpress user with no `clientId` data" hold even if something re-wrote the key during unload (Log Out removes `alo_bp_owner`, so the next init cannot match). It also closes a path in the same class that R-C did not list: on `main`, a `?t=` switch from test client X to test client Y in the same browser restored X's Botpress user and X's last conversation and then re-labelled it Y (harness `account_switch_token`). One-time effect of deploying it: a browser with no `alo_bp_owner` yet gets a fresh Botpress user on its first load (the in-window conversation is not restored; Supabase history is unaffected).

### C - The sign-out path that does not reload (R-C-17)

Two non-reload sign-out paths existed after B:

1. The SIGNED_OUT listener (4551). In supabase-js 2.39.0 SIGNED_OUT is emitted only by `signOut()` and received from other tabs over the `BroadcastChannel` named after the storage key (read in the UMD). On `main` it re-skinned the header and left every global, the open chat and the Botpress identity. It now calls `_aloSignOutCleanupAndReload()`.
2. `loadConnectedState()` finding no user under a page that had an identity (2176). supabase-js 2.39.0 removes a session whose refresh fails **without** emitting SIGNED_OUT (`_callRefreshToken` / `_recoverAndRefresh`), so R-C-17's "refresh failure emits SIGNED_OUT" does not hold for this version; the page instead stays stale until something re-reads the user. If `clientId` is set and `getSession()` also has nothing, the same cleanup runs. If a session is still stored, `getUser()` failed for another reason (network), which is not a sign-out, and the old behaviour stays (no reload, so no loop while offline; harness `getuser_network_fail`).

After B and C there is a **single path**: `handleLogout()` (1252), the SIGNED_OUT listener (4555) and the no-user branch (2179) all call `_aloSignOutCleanupAndReload()`, and its reload (1273) is the only sign-out reload in the file.

### D - Display name into an attribute (R-C-03)

`showNameEditModal()` (989): before, `value="${currentName}"` (`main:974`), where `currentName` is the badge's `textContent` (decoded again) and can come from the therapist's invite label. After, the input is rendered with no `value` attribute and `modal.querySelector('#nameEditInput').value = currentName` sets it as a property once `createModal()` has returned (1030).

Every other `value="${` and `${...}` inside an attribute (section 4, self-check D): `resetEmailInput` (1809) and `renameInput` (2881) already use `escAttr()` in a double-quoted attribute, which is correct and left as is; `id="${modalId}"` / `aria-labelledby` (created from `Date.now()`) carry no input. The string-concatenated attributes carry database ids, constants or `escAttr(thread.title)`. The one misuse in the same class is `main:1566` (`escAttr()` inside a JavaScript string inside `onclick`, R-C-30, S4, the user's own email): it is not a `${...}` interpolation and R-C-30 is S4, so it was left (section 7).

### E - Therapist-supplied strings into `innerHTML` (R-C-09)

| Sink | Before | After |
|---|---|---|
| homework card "From" (1104) | `'From ' + therapistName` | `esc(therapistName)` |
| homework title (1105) | raw | `esc(hw.title \|\| 'Practice exercise')` |
| homework type tag (1110) | raw | `esc(hw.homework_type)` |
| homework goal (1111) | raw | `esc(hw.goal \|\| '')` |
| Message Therapist modal title and body (1935) | `connectedTherapistName` into `createModal()` title (`<h2>`) and body | escaped once into `therapistName` before both uses |
| share confirm (3945) | into `showConfirm()`'s `<p>${message}</p>` | escaped first |

The badge (897) and the journal "Shared with" badge already escaped; the homework tip uses `textContent`. Therapist text that relied on HTML formatting would now show literally (none is expected; these are plain-text fields).

### F - `detectSessionInUrl` (R-C-06)

How the `?t=` exchange (D29-03) consumes its result: `_aloExchangeClientToken()` POSTs the token to `exchange-client-token`, takes `token_hash` from the response and calls `supabase.auth.verifyOtp({ token_hash, type: 'magiclink' })` itself. It never relied on URL detection. In the 2.39.0 UMD, `verifyOtp` POSTs `/verify`, removes the current session (for this type), saves the new one and emits SIGNED_IN; `_removeSession()` emits nothing, so fix C's SIGNED_OUT reload cannot fire mid-exchange.

So, per the brief, only the flag changed: `detectSessionInUrl: false` (464), with the two comments that described URL detection corrected (the createClient comment, and the D29-03 block that said the setting "does not interact"). In the UMD, `_initialize()` reads a session from the URL only if `_isPKCEFlow()` (a `code` parameter **and** a stored code verifier, which the default implicit flow never writes) or `detectSessionInUrl && _isImplicitGrantFlow()`. With the flag off, a fragment or query carrying another account's tokens is ignored, and so is an `error_description` (R-C-27, S4, closed as a side effect).

Consequence to know about: email-confirmation and password-reset links land with tokens in the fragment, and they **no longer sign the user in by themselves**. The reset link already could not reach "Set New Password" (R-C-20); it now lands signed out, and the `PASSWORD_RECOVERY` branch is unreachable. See section 7.

### G - Consent gate on every link (R-C-02)

`loadConnectedState()` (2265): before, `const link = links[0]; if (aloConsentRequired(link))` over an unordered query. After, `if (links.some(aloConsentRequired))` holds the screens (same guard against re-opening mid-screens), and `links[0]` is taken only past the gate. The `?invite=` claim while already connected goes `showConnectModal()` -> `handleConnectSubmit()` -> `loadConnectedState()`, so the newly active, unconsented row now lands on the gate (harness: gate shown, no second `session_metadata`). Completing consent from the gate with two links unlocks (the existing write PATCHes every row of the client and re-reads every active row). The onboarding predicate `aloConsentRequired()` itself is unchanged.

### H - A stored invite code does not outlive the attempt (R-C-11)

| Where | Before | After |
|---|---|---|
| login modal `onConfirm` | `localStorage.setItem('alo_pending_invite', code)` **before** the sign-in attempt; it survived a wrong password, an abandoned modal and Log Out | nothing is stored. The attempt uses the code in memory (`handleConnectSubmit(inviteCode)` right after a successful sign-in, as before). A signup that needs email confirmation already carries it in `user_metadata`, which belongs to that account |
| `loadConnectedState()` no-link branch (2220) | `user_metadata.invite_code \|\| localStorage.getItem('alo_pending_invite')`: the next account on the browser claimed someone else's code (and, if its own name was unset, took the invitee's name; R-C-11) | only `user.user_metadata?.invite_code` (bound to the user id). `invite_code` is cleared in a `finally` after the attempt, success or failure, and a failed clear is logged instead of turning a successful claim into the "Could not connect" state |
| page load (4166) | - | any `alo_pending_invite` an older build left is removed unread (a leftover code is itself claimable by whoever reads it) |
| Log Out | kept | removed (B) |

### I - Private mode only once the bot confirms (R-C-07)

| Where | Before | After |
|---|---|---|
| `startPrivateSession()` (3268) | set the flag, banner, toast and tip, then fired `updateUser` without awaiting | `_aloSetBotPrivateFlag('true')` (3224): requires an initialized webchat (`botpressReady` and `window.botpress.initialized`; before init the SDK's `updateUser` only merges locally), awaits `updateUser` with an 8 s cap, **retries once**, and checks the returned user. Only then does `_aloEnterPrivate()` (3253) flip `isPrivateSession`, set the marker and show banner, toast and tip |
| failure | the private UI was shown; an `unhandledrejection` was the only trace | no banner, no flag, the constant **"Couldn't start a private session — nothing was changed. Try again."**, and a best-effort `privateSession: 'false'` in case a timed-out attempt landed after all (`_aloUndoBotPrivateFlag`, 3242) |
| double tap | - | ignored while a start is in flight (`_aloPrivateStarting`) |

What "confirmed" means: after init, the SDK's `updateUser` merges the new data into its copy of the user, awaits the Chat API's `PUT /users/me`, and sets `window.botpress.user` to the user the API returned (webchat.js). The check requires the promise to resolve and, when that returned user carries a `data` object, requires `data.privateSession` to equal the new value. The webchat reads the returned user through `.data`, but the bundle does not show the response shape outright, so a user without `data` is accepted on the resolved round trip alone rather than failing private mode closed for everyone (section 6). Worst case on a dead network: about 16 s (two 8 s attempts) before the failure line.

### J - Copy corrections (R-C-13, R-C-14, R-C-15, R-C-16)

Section 3 lists every changed sentence. How each finding was closed:

- **R-C-13:** one phrasing on every surface: the therapist can see when the client uses Alo (the `session_metadata` row each linked load writes) and when they view or complete homework (`viewed_at` is written as soon as a card renders, `completed_at` on "Mark complete"), never what they say. Crisis alerts, messages and shared entries are named where the list is meant to be complete (About).
- **R-C-14:** the memory-off hint now says history is still saved. Private sessions are still offered only while memory is on: the brief scopes J to copy, so R-C-14's behavioural half is left for triage (section 7).
- **R-C-15:** private mode can still start mid-conversation. Making the earlier turns not persist would mean deleting already-saved `conversation_messages`/`conversations` rows from the client. Their client DELETE policies and cascade are unverified (R-C section 7, items 1-2) and delete-policy work is Migration v1.5 (excluded with R-C-05). A private start that depended on an unverifiable delete would fail open, so it does not fit inside fix A. Instead the copy says "this conversation" only when nothing of the conversation was saved before private mode began (`_aloConvFresh`: set on a fresh Botpress user or a restart, cleared the moment a row is created or resumed; unknown counts as not fresh). Otherwise the banner, toast, tip, new-conversation confirm and menu item say "from this point on".
- **R-C-16:** "Guests start fresh every visit." was made true instead of removed: B's owner rule gives each guest visit (one tab session) its own Botpress user, so a returning guest, or the next guest on a shared device, no longer gets the previous conversation or its up-arrow history. A reload in the same tab (for example the theme toggle, which reloads) keeps the guest's conversation.

## 3. Copy: before / after

| Where | Before | After |
|---|---|---|
| Onboarding screen 2 "What's yours" (1432) | ... you choose that, one thing at a time. Nothing is shared unless you share it. | ... you choose that, one thing at a time. Beyond what you share, your therapist can see when you use Alo and when you view or complete homework they assign — never what you say to Alo. |
| Consent screen 4 (1530) | Your conversations are yours — nothing is shared unless you choose to. | Your conversations are yours: your therapist sees what you choose to share, when you use Alo, and when you view or complete homework they assign, never what you say. (rest of the paragraph unchanged; checkbox text unchanged) |
| Login modal, muted line (1687) | Your conversations stay private. Signing in does not share anything. | Your conversations stay private. If you're connected to a therapist, they can see when you use Alo and when you view or complete homework they assign — never what you say. |
| About > Your privacy, p2 (215) | ... they can see general patterns across your sessions and whether you've completed any reflections they've assigned. That's it. They aren't notified in real time ... | ... they can see general patterns across your sessions, when you use Alo, and when you view or complete reflections they've assigned. They also see messages you send them, journal entries you choose to share, and, if Alo notices you might be in trouble, that something happened — never what you said. They aren't notified in real time ... |
| Privacy modal > Who sees your data (4520) | Your therapist sees homework status, messages you send them, and any journal entries you explicitly share | Your therapist sees when you use Alo, when you view or complete homework, messages you send them, and any journal entries you explicitly share |
| Homework tip, shown once (1123) | <name> assigned this. Mark it done when you're ready — they'll see that, not what you wrote. | <name> assigned this. Mark it done when you're ready — they'll see when you've viewed it and when you mark it done, not what you wrote. |
| Memory-off hint, both private entry points | Memory is already off — nothing is being remembered | Memory is off, but your conversations are still saved to your history. |
| Menu item (161, 3325) | Make this conversation private | Go private from this point on |
| Private banner, mid-conversation (3134) | Private session — Alo won't remember this conversation | Private from this point on — Alo won't remember what you say next |
| Private toast, mid-conversation | Private session — this conversation won't be remembered | Private from this point on — what you say next won't be remembered |
| Private tip, mid-conversation (shown once) | Nothing from this conversation goes into your history or memory. | From this point on, nothing goes into your history or memory. |
| New-conversation confirm, mid-conversation private | This private conversation is not kept in your history. | Anything from before you went private stays in your history; nothing after that is kept. |
| Private start failure (new, fix I; the brief's constant) | (private UI shown regardless) | Couldn't start a private session — nothing was changed. Try again. |
| Message Therapist during a private session (new, fix A) | (message sent to `client_messages`) | Messages to your therapist can't be sent during a private session. |

Unchanged on purpose, now true: the whole-conversation private banner, toast, tip and confirm (used only when nothing of the conversation was saved); About "start a private session (nothing from it goes into your history or memory)"; About "Guests start fresh every visit." (made true by B, not reworded). The About/Privacy "forget" and "clear" claims are R-C-05 (excluded) and were not touched.

## 4. The ten self-checks (one per fix), with results

| # | Check | Result |
|---|---|---|
| A | `ensureConversation()`'s first statement is the private guard; the message handler's two call sites are guarded; `client_messages` refused while private; harness: zero `conversations`/`conversation_messages`/`client_messages` writes in a private session, and a reload mid-private gives a new Botpress user and conversation with no row for the private one | 2370 `if (isPrivateSession) return null;`; 4400 and 4417 guarded; 1930 and 1952; `private_whole` and `private_reload` PASS |
| B | `handleLogout()` awaits the shared cleanup before any reload; after reload a guest has a fresh Botpress user with no `clientId`, and no identity call is made | 1252; `logout` PASS: fresh user, empty data; at unload `clientId`, `therapistLink`, `currentSupabaseConvId`, `memoryGlobalEnabled`, therapist name all `null`; no `bp-*`, `botpress-message-history`, `alo_unsent_messages`, `alo_dropped_messages`, `alo_conv_*` key left; log shows `updateUser` (blank), `close`, `unmount('webchat')` in that order |
| C | every sign-out entry calls the one cleanup; its reload is the only sign-out reload | callers 1252, 2179, 4555; the reloads at 593 (theme), 2361/4219/4444 (retry buttons) and 3444 (restart failure) are not sign-out paths. **Single path.** `signout_broadcast`, `silent_session_loss` PASS; `getuser_network_fail` PASS (no reload) |
| D | no `value="${` without `escAttr()`; the name is set as a property; harness with the brief's `" onfocus="alert(1)` as the name | only 1809 and 2881 remain, both `escAttr()`; 1030; `xss_name` PASS: no handler ran, the value is the literal string, no `onfocus` attribute |
| E | the seven R-C-09 sinks use `esc()` | 1104, 1105, 1110, 1111, 1935 (title and body), 3945; `xss_therapist` PASS: no handler at load, in Message Therapist or in the share confirm; 0 `<img>` rendered |
| F | `detectSessionInUrl: false`; `?t=` still signs in; foreign tokens ignored | 464; `token_exchange`, `foreign_fragment`, `foreign_query` PASS (real supabase-js 2.39.0) |
| G | the gate predicate runs over every active link | 2265 `links.some(aloConsentRequired)`; no single-row call left; `multilink_consented_first`, `multilink_unconsented_first`, `invite_while_connected`, `multilink_consent_complete` PASS |
| H | nothing writes or reads `alo_pending_invite` except removals | 1325 (Log Out), 4166 (page load); `pending_invite_residue`, `login_wrong_password_invite`, `metadata_invite_claim` PASS |
| I | `isPrivateSession = true` only after `_aloSetBotPrivateFlag()` resolved true; two attempts | 3254 (`_aloEnterPrivate`, called only after confirmation) and 3354 (after confirmation, before the restart); loop at 3227 `attempt <= 2`; `private_flag_fails` PASS (2 attempts, no banner, constant copy, flag reset, no unhandled rejection), `private_flag_retry_ok` PASS |
| J | none of the old false sentences remain; the new ones render | `grep -c` = 0 for "Nothing is shared unless you share it", "nothing is shared unless you choose to", "Signing in does not share anything", "That's it.", "nothing is being remembered", "Make this conversation private", "they'll see that, not what you wrote", "Your therapist sees homework status"; `copy_render`, `private_midconv`, `memory_off_private`, `guest_fresh_visit` PASS |

K: `python3 scripts/scan-invisible.py dev.html dev.css` printed `CLEAN` for both files with exit 0 before every commit, and again for this report. `node --check` passes on both inline scripts after every commit. `git diff main --stat`: `dev.html` only (plus this report).

## 5. Harness results

**Method** (the S4A-min / R-C pattern). Headless Google Chrome 153, local `python3 -m http.server`, a fresh profile per run, 26 scenarios run on the final branch `dev.html` and on `main`'s `dev.html`. The harness copy of each keeps the page's own CSP and replaces only the two CDN script tags:
- Botpress inject.js is replaced by a stand-in modelled on the v3.3 bundles: the same store key and format, restore-at-init of user and conversation, the composer recall list, pre-init `updateUser` that only merges locally, post-init `updateUser` that resolves after a (local) server update and sets `window.botpress.user`, `close`, `unmount`, and server-side user data that survives reloads.
- supabase-js is the **real 2.39.0 UMD** served locally, with `window.fetch` answered by a local PostgREST/GoTrue/edge-function emulation that logs every request.

Multi-phase scenarios reload the app inside a same-origin orchestrator iframe (390x844, or 375x844 for screenshots), so `localStorage` and `sessionStorage` persist across phases. No request left the machine; no real credentials were used.

| Scenario | What it does | Final branch | `main` |
|---|---|---|---|
| `private_whole` | new private conversation, two exchanges, then Message Therapist | PASS: 0 writes; therapist message refused | FAIL: `POST conversations {is_private: true}` and `POST client_messages` |
| `private_reload` | private conversation, then reload, then chat | PASS: fresh Botpress user and conversation; new messages go to a new normal row; nothing for the private one; history lists 1 conversation | FAIL: same user and conversation restored; messages written into the private row; it lists with 2 turns |
| `private_midconv` | two saved turns, go private, chat, open "New conversation" | PASS: "from this point on" banner/toast; no writes after; scoped confirm | FAIL: "won't remember this conversation" while the row holds 4 turns, not private |
| `private_flag_fails` | `updateUser` rejects twice | PASS: 2 attempts; no banner; constant copy; flag reset; no unhandled rejection | FAIL: private UI shown after 1 attempt; unhandled rejection |
| `private_flag_retry_ok` | rejects once, then succeeds | PASS | PASS (control: `main` shows private without waiting) |
| `memory_off_private` | memory off, both private entry points | PASS: new hint | FAIL: "nothing is being remembered" |
| `logout` | connected client chats, local queues seeded, Log Out | PASS: see self-check B | FAIL: same Botpress user restored with `clientId`; queues, mappings and recall list left |
| `signout_broadcast` | sign-out arrives from another tab (library broadcast path) | PASS: same cleanup, reload, fresh user | FAIL: no reload; `clientId`/`therapistLink` and the Botpress identity kept |
| `silent_session_loss` | session removed without SIGNED_OUT, then a user re-read | PASS: same cleanup, reload | FAIL: guest header over the identified chat |
| `getuser_network_fail` | `GET /auth/v1/user` fails while the session is stored | PASS: no reload, session kept | PASS (control) |
| `signed_in_reload_reuse` | connected client reloads | PASS: same Botpress user and conversation, saving resumes in the same row | PASS (control: B does not wipe on ordinary reloads) |
| `xss_name` | the brief's `" onfocus="alert(1)` as the client's name, open the editor | PASS | FAIL: `onfocus` attribute injected, handler ran |
| `xss_therapist` | event-handler markup in the therapist name and homework title/goal/type | PASS | FAIL: handlers ran at load (4), in Message Therapist (2), in the share confirm (1) |
| `token_exchange` | `?t=` with a stubbed edge response | PASS: signed in as the test client via one `/verify` | PASS (control) |
| `foreign_fragment` | stored session V, link with another account's tokens in the fragment | PASS: still V; foreign token never used | FAIL: session replaced; the bot was sent the other account's id |
| `foreign_query` | the same tokens in the query string | PASS | FAIL |
| `multilink_consented_first` | two active links, the consented one returned first | PASS: gated, no Botpress init | FAIL: not gated |
| `multilink_unconsented_first` | the unconsented one first | PASS | PASS (control) |
| `multilink_consent_complete` | consent from the gate with two links | PASS: unlocks | PASS (control) |
| `invite_while_connected` | connected client opens `?invite=` for a second therapist and links | PASS: gate shown after the claim | FAIL: second link active, unconsented, not gated |
| `pending_invite_residue` | leftover `alo_pending_invite`, another account signs in | PASS: no lookup, no claim, key removed | FAIL: the other person's code is looked up and claimed for the signed-in account |
| `login_wrong_password_invite` | sign-in with an invite code and a wrong password | PASS: nothing stored | FAIL: code left in storage |
| `metadata_invite_claim` | account whose own signup stored `invite_code` | PASS: claimed, then cleared | PASS (control) |
| `guest_fresh_visit` | a previous guest's store and recall list present; new tab; then same-tab reload | PASS: fresh user and no recall list; the reload keeps the new guest's conversation | FAIL: previous guest's user and typed text restored |
| `account_switch_token` | store belongs to test client X; `?t=` for Y | PASS: fresh Botpress user for Y | FAIL: Y inherits X's Botpress user and conversation |
| `copy_render` | renders the section-3 strings | PASS | FAIL (old copy) |

Totals: final branch 26/26 PASS, 0 page errors or unhandled rejections; `main` 19 FAIL / 7 PASS (the 7 controls pass on both).

Phone widths (`CLAUDE.md`: 375 and 390): no CSS changed, but four strings got longer, so they were screenshotted in the harness (headless Chrome, dark theme). All fit with no horizontal scroll and every control in view:
- the "from this point on" banner at 375 px wraps to two lines, like the privacy bar under it;
- consent screen 4 at 375 px;
- the login modal at 375 px;
- onboarding screen 2 at 390 px.

## 6. Not verifiable without live credentials or a device

1. **Live Botpress (fix I, fix B).** The Chat API user returned by `updateUser`: the check tolerates a user without `data` (section 2, I). Also: how long the round trip takes on mobile; and that the live webchat accepts `close()` then `unmount('webchat')` at Log Out (read from inject.js, run only against the stand-in). Bot-side: that the bot reads `privateSession` at turn 1 of the new conversation (R-C-07 read it from the Sep 8 export), and whether it sends a greeting at conversation start (the private-start order is safe either way).
2. **Email links after fix F.** Whether confirmation emails are in use on this project (self-signup state is unknown, R-C section 7). If they are, a confirmation link now lands signed out and the user signs in with their password; the reset link lands signed out (it could not set a password before either, R-C-20).
3. **The deployed `exchange-client-token`** (stubbed here) and a real `?t=` link from the dashboard.
4. **Supabase RLS** for every write this session touched: unchanged by this session, and not re-verified.
5. **Devices.** iOS Safari and installed-PWA behaviour of `sessionStorage` (the guest "visit" boundary) and of reloads during a private session; phone rendering on real hardware (the screenshots are headless Chrome).

## 7. Declined as out of scope, and observations

Declined (the brief's scope list or its "not in scope" rule):
- **R-C-05** (delete policy), **R-C-10** (bot nonce read), **R-C-12** (guest crisis writes), the **Path R** claim switch: excluded by the brief; not touched.
- **R-C-14, behavioural half:** private sessions still require memory on. J is copy-only; allowing private with memory off (the R-C fix) is a small change if wanted.
- **R-C-20:** "Set New Password" is still unreachable; after F the reset link does not even sign in. The safe fix is Auth-side (email templates carrying `{{ .TokenHash }}` to a page that calls `verifyOtp`, or PKCE), which is an Auth change needing approval and a test plan.
- **R-C-30** (S4, `escAttr()` inside a JavaScript string in `onclick`, `main:1566`, the user's own email): it is in fix D's class but is not a `${...}` interpolation, and S4 is out of scope.
- **R-C-22 beyond the ride-along:** normal (non-private) sessions still write message content to `alo_unsent_messages` / `alo_dropped_messages` when persistence fails or a format is unknown; only Log Out clears them.
- R-C-08, R-C-18, R-C-19, R-C-21, R-C-23 to R-C-26, R-C-28, R-C-29, R-C-31, R-C-32: not touched. R-C-27 (sign-out via `error_description`) is closed as a side effect of F.

Observations, not changed:
- **Botpress composer recall list during a live private session.** The SDK adds each sent message to `botpress-message-history` (in memory and localStorage) as it is typed; the page cannot clear it while the webchat runs. It is cleared at every point the page controls: Log Out, a reload during a private session, and the start of each guest visit.
- **Two tabs and a private session.** A second tab loaded while the first is private consumes the `alo_private_active` marker. If the private tab keeps chatting and is then reloaded, its conversation can resume, and turns after that reload are saved. The private session's own turns are still never written.
- **Consent completion with two links re-stamps the earlier link's `consent_acknowledged_at`** (the existing PATCH covers every row of the client; seen in `multilink_consent_complete`).
- **A private session still writes activity:** when the tab becomes visible again supabase-js emits SIGNED_IN, and `loadConnectedState()` writes a `session_metadata` row and re-sends identity (merging, so `privateSession` is kept). This is not in fix A's list; it is disclosed by the new "when you use Alo" copy.
- **Signed-in accounts with no link** still send no identity until "New conversation" (R-C-21), unchanged.

## 8. Kano's check on alowen.ai/dev.html (after merge to a dev deploy)

1. Signed in as a linked client: menu > "Start new private conversation", send two messages, open the sidebar: no new entry. Reload: banner gone, a fresh conversation; send one message; the sidebar shows it as a normal conversation, and still nothing from the private one.
2. With Wi-Fi off, menu > "Go private from this point on": after a few seconds, "Couldn't start a private session — nothing was changed. Try again." and no banner.
3. Log Out, then in DevTools > Application > Local Storage: no `bp-webchat-*` or `botpress-message-history`, no `alo_unsent_messages` or `alo_dropped_messages`. The guest chat is empty, and up-arrow in the composer recalls nothing.
4. Tap your name in the header: the editor shows it; nothing else happens.
5. If email confirmation is on: sign up a throwaway address and follow the link. Expect to land signed out (F); sign in with the password.
