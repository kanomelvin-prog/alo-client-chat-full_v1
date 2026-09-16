# S4A-min session report v1.0

Brief 1a-min, Client App, Gate A subset (v1.1). Branch `auto/s4a-min`, created from `main` at `1eadd8c`. Session ran 2026-09-15 evening (Claude Code, Fable 5.1, effort max, unattended). Nothing was pushed to `main`; the parked branch `auto/s4a-consent-gate` was read from (`git show`) and never modified.

## 1. Path used

**Path P.** The direct PATCH claim in `handleConnectSubmit()` is unchanged. Item F (`redeem_invite_code` RPC) was not touched, as the brief specifies for Path P.

## 2. Every changed function, before and after

All changes are in `dev.html` (plus `CLAUDE.md` for E1). `dev.css` is untouched, so the cache buster stays at `?v=15`. `index.html` and `styles.css` are untouched.

### A - fail-closed consent gate (commit `5938c40`)

| Function | Before | After |
|---|---|---|
| `aloConsentRequired(link)` (new, line 1951) | did not exist; consent was never read on entry | the one predicate: `true` when `link && link.client_id && !link.consent_acknowledged_at`. No duplicates anywhere |
| `loadConnectedState()` (line 1962) | fetched the active link with `select=*`, set `therapistLink`/`clientId`, then unlocked everything (connected UI, memory, homework, session_metadata, Botpress identity) | fetch selects `id,therapist_id,client_id,display_name,status,consent_acknowledged_at` explicitly (line 1976). Right after the row is found, the gate (line 2034): an unconsented row opens the existing screens in gate mode and **returns** before `therapistLink`/`clientId` are set and before any unlock. Only past the gate does `_aloInitBotpress()` run (line 2047). A guard stops two near-simultaneous entries from resetting a client mid-screens. A read failure now shows the load-error state instead of a silent spinner (Botpress is no longer running underneath) |
| `loadConnectedState()` pending-invite branch | `await handleConnectSubmit(...)` and return, whatever happened; an invalid stored code left the page in the initial (guest-looking) header with no chat | `handleConnectSubmit()` now returns whether the row was claimed; if not, the link is re-read from the server (`await loadConnectedState()`, line 2016) so an active row goes through the gate and no row shows the signed-in UI. `_aloPendingInviteHandled` makes the re-entry skip the invite branch, so it cannot loop |
| `_aloOnboardingComplete()` (line 1371) | closed the overlay immediately, fired the PATCH without awaiting, and on failure wrote `alo_consent_acknowledged_fallback` to localStorage and `console.warn`ed | disables "Start talking to Alo" while in flight; `await`s the PATCH on `/rest/v1/therapist_clients?client_id=eq.<uid>`; then re-reads the client's active rows and treats the write as succeeded only if the server now returns a non-null `consent_acknowledged_at` (a PATCH that RLS filters to zero rows is still a 204). On success: close the overlay, `await loadConnectedState()`. On any failure: overlay stays on screen 4, button re-enabled, the constant copy is shown in `#aloOnboardingError`: "Something didn't go through. Nothing was changed. Try again in a moment." No localStorage, no `console.warn` fallback, never the raw error |
| `_aloRenderOnboardingScreen()` gate screen 4 | no error slot | adds `<p id="aloOnboardingError" role="alert">` (hidden until needed; inline `var(--danger)`, the same pattern the login modal's error uses, so no dev.css change) |
| `handleConnectSubmit()` (line 1442) | claim then `await loadConnectedState()`; returned nothing | claim unchanged; still enters through `loadConnectedState()`, which is where the gate lives (there is no ungated variant); returns `true` when the row was claimed, `false` otherwise |
| `showLoginModal()` onConfirm | after sign-in, opened the screens itself for a brand-new invite signup (`isNewInviteSignup`) | that trigger is removed; the gate opens the screens for any active, unconsented row on every path |
| `showLoggedInNoConnection()` (line 814) | assumed Botpress was already running | calls `_aloInitBotpress()` first: a signed-in account with no active link has nothing to consent to |
| `resetToGuestUI()` (line 1021) | same assumption | calls `_aloInitBotpress()`: guest chat is still on this build |
| DOMContentLoaded (line 3830) | `window.botpress.init()` ran for everyone before the session was checked; the 15 s "Still loading" timeout started at page load | the original block (init, the three `window.botpress.on` listeners, the timeout) is wrapped, unchanged, in `_aloInitBotpress`, guarded by `_aloBotpressInitStarted`. `window.botpress.init(` has exactly one call site (line 3838). The tail calls it for a guest page and for a failed `?t=` exchange (no session); a successful exchange hands off to the SIGNED_IN listener's `loadConnectedState()` as before |
| `_aloShowLoadError()` (new, line 2123) | n/a | the chat area's failure state with a reload button, used when the link read fails before the gate is known |
| script-level | `botpressReady` only | adds `_aloBotpressInitStarted`, a fail-closed `_aloInitBotpress` placeholder (logs, never inits), `_aloPendingInviteHandled`, `ALO_CONSENT_WRITE_FAILURE_MESSAGE` |

Where each `loadConnectedState()` call site enters, and the gate that precedes any unlock (self-check 2 in section 4).

### B - memory display default ON, card becomes disclosure (commit `f5e6cca`)

| Function / element | Before | After |
|---|---|---|
| `memoryGlobalEnabled` initial (line 480) | `false` ("opt-in: default OFF") | `true` |
| `loadMemorySettings()` (line 2812) | no `client_settings` row -> `false`; read error -> `false` | no row -> `true`; read error -> `true` (show the default rather than under-disclose). A row with `memory_enabled = false` still displays OFF |
| `checkMemoryOnboarding()` (line 3041) | returned early when memory was on ("already opted in"); card was an ask | returns early when memory is **off**; shows the disclosure on the 2nd visit while memory is on, then the existing 2-dismiss pattern |
| `enableMemoryFromOnboard()` | wired to the card's Enable button | removed; nothing else referenced it |
| `#memoryOnboardCard` | "Want Alo to remember context?" / "Alo can use short summaries..." / Enable + Not now | "Alo remembers context" / "Alo keeps brief summaries of past conversations so you don't have to re-explain. Your therapist can't see any of this. You can turn this off any time in Settings." / one "Got it" -> `dismissMemoryOnboard()` |

Note for the evening check: the card follows the existing pattern, so on a fresh account it appears on the **second** page load (the first marks `alo_memory_onboard_ask`). Reload once. "Settings" is the brief's verbatim copy; the toggle lives in the menu's Memory section and the eye-icon popover.

### C - A-23 About-modal correction (commit `e254966`)

The parked commit `b21a08a` was read with `git show`. Its "How memory works" hunk names a conversation-history switch ("When conversation history is on... When it's off, nothing is kept... Memory needs history on") that does not exist on this build, so applying it would have introduced untrue claims. Per the brief's fallback, the paragraph was written by hand with the corrected meaning (memory is brief summaries; history is stored so you can review it and can be deleted any time), scoped to what is true here (deletion is from the Alo account; platform-side deletion is not yet in place). The memory-card retirement hunks were not applied (B1 supersedes them).

### D - demo copy pass (commit `e254966`)

See section 3 for the sentence list. Functions touched only for copy: `deleteThread()`, `clearHistory()`, `startPrivateSession()` tip, `startNewConversation()` confirm (now says the truth during a private session), the persistence `message` handler toast. `showGuestBenefitsCard()` is a no-op and its three callers are gone; `checkGuestMemoryPrompt()` still counts turns but never reveals the bar.

### E - CLAUDE.md (commit `b2054fb`)

From `51ba80f` (S4A 4.G), only the `### Git workflow` section (auto/* branches, never push to main, verify pushes, Kano merges) and the `## File Structure` lines for `dev.html`/`dev.css`, `index.html`/`styles.css`, `scripts/scan-invisible.py`, `CLAUDE.md`. The `docs/contracts/...`, `docs/reports/`, `manifest.json`/`icons/`, data-posture, account-types, and consent-contract text were not brought over.

## 3. Demo copy: before / after

Truth table applied: therapist never sees conversations (keep); not used for training/analytics/advertising (keep); memory = brief summaries, on by default, disclosed, can be turned off (align); anything implying deletion from the AI platform after a private session or on request is not yet true (reword to "from your Alo account", platform-side deletion coming, no date); no state, age attestation, waiting room, or reminder cadence may appear (none found); `#guestBenefitsCard` never shown.

| Where | Before | After |
|---|---|---|
| About > Your privacy | Guest conversations aren't saved after the session ends. If you're signed in, you stay in control: turn memory off, start a private session (nothing gets saved), or ask Alo to forget a specific topic. | Guest conversations aren't saved to an account. If you're signed in, you stay in control: turn memory off, start a private session (nothing from it goes into your history or memory), or ask Alo to forget a specific topic. |
| About > How memory works (p1) | Alo doesn't store your conversations word for word. When memory is on, it keeps brief notes - just enough to pick up where you left off next time. | When you're signed in, Alo keeps your conversation history so you can review it, and you can delete any conversation from your Alo account at any time. Deletion from the chat platform Alo runs on is coming and isn't in place yet. |
| About > How memory works (p2, new) | (none) | When memory is on, Alo also keeps brief summaries of past conversations - just enough to pick up where you left off next time. Memory is on by default and you can turn it off any time. |
| About > How memory works (p3) | You're always in control: turn memory off, go private for a session, or ask Alo to forget something. | unchanged |
| About > How memory works (muted line) | Memory is available when you're signed in. Guests start fresh every visit. | Memory and history are for signed-in accounts. Guests start fresh every visit. |
| Menu > Memory setting detail | Alo keeps short summaries of recent conversations (not full transcripts) for continuity. ... | Alo keeps short summaries of recent conversations for continuity. ... (transcripts are kept as history on this build) |
| Privacy Policy > Your Alo conversations | You can delete any conversation at any time from the sidebar | You can delete any conversation from your Alo account at any time from the sidebar. Deletion from the chat platform Alo runs on is coming and is not yet in place |
| Privacy Policy > Your Alo conversations | Guest conversations (no account) are not stored permanently | Guest conversations (no account) are not saved to an account |
| Private-session tip | This conversation won't be saved. Alo won't remember it next time. | Nothing from this conversation goes into your history or memory. |
| Delete-conversation confirm | This permanently removes the conversation and Alo's memory of it. This can't be undone. | This removes the conversation and Alo's memory of it from your Alo account. This can't be undone. |
| Clear-history confirm | This will delete N unpinned conversation(s). | This will delete N unpinned conversation(s) from your Alo account. |
| New-conversation confirm (private session) | Your current conversation is saved in your history. | This private conversation is not kept in your history. (non-private wording unchanged) |
| Persistence failure toast | Message saved locally - will send when reconnected | This message couldn't be saved to your history. (nothing on this build re-sends the local queue) |
| Memory card | Want Alo to remember context? / ... / Enable, Not now | Alo remembers context / ... You can turn this off any time in Settings. / Got it |
| `#guestBenefitsCard` | shown to guests after 2 s (and reaching signed-in users) with "Create Account" | never shown; markup kept; Create Account button removed; "Maybe later" and dismiss remain |
| `#memoryPromptBar` | shown to guests after 5 turns with "Create Account" | never shown; markup kept; Create Account button removed (same truth-table item: a no-invite signup is not available on this build) |

Read and left unchanged as true on this build: onboarding screens 1-4 (gate and read-only), connect modal, connect prompt, Terms modal, privacy bar, memory popover, private-session banner and toast, homework/journal/memory tips, thread and journal empty states, transcript share sheet, share modal, remaining toasts. Kept verbatim on purpose: "Your therapist never sees what you say to Alo" and "Conversations are not used for training, analytics, or advertising".

## 4. The five self-checks

1. `grep -c alo_consent_acknowledged_fallback dev.html` -> **0**.
2. Every `loadConnectedState()` call site, and the gate that precedes any unlock. The gate is inside `loadConnectedState()` itself: predicate at line 1951, check at line 2034, `return` before `therapistLink`/`clientId`/`_aloInitBotpress()` (2047)/`showConnectedUI`. No caller can skip it because there is no ungated function to call.

   | Call site | Line | Path |
   |---|---|---|
   | `_aloOnboardingComplete()` | 1411 | after the consent write is verified server-side; gate re-reads and passes |
   | `handleConnectSubmit()` | 1483 | after the Path P claim; unconsented new row is held here |
   | `showLoginModal()` onConfirm (no invite code) | 1599 | password sign-in / signup |
   | `showSetNewPasswordModal()` | 1701 | after a password reset |
   | `loadConnectedState()` re-entry | 2016 | after a stored invite code did not connect; invite branch skipped by guard |
   | SIGNED_IN listener | 4188 | email confirmation, `?t=` exchange, every SDK sign-in |
   | page load, existing session | 4222 | silent-auth re-entry |

   `?invite=` deep link into a signed-in account goes `showConnectModal()` -> `handleConnectSubmit()` -> 1483. Reconnect after a link change is the same claim path or the page-load path.
3. `_aloOnboardingComplete` (line 1371): `await` on the PATCH at line 1385, on the verify read at 1391, on `loadConnectedState()` at 1411; `localStorage` does not appear in the function.
4. `python3 scripts/scan-invisible.py dev.html dev.css` -> `CLEAN` on both, exit 0, run before each of the four commits and again on the final tree (also `CLEAN` for `CLAUDE.md`). The inline script also passes `node --check` after each commit.
5. `git log --oneline main..auto/s4a-min` -> exactly this session's commits (`5938c40`, `f5e6cca`, `e254966`, `b2054fb`, plus this report). `git diff main --stat` touches `dev.html` and `CLAUDE.md` only; `dev.css` unchanged.

## 5. Verification the session could do

Headless Google Chrome 153 against a harness copy of the final `dev.html` with the Botpress SDK, the Supabase client and `fetch` stubbed per scenario (no network, no writes; scripts in the session scratchpad):

| Scenario | Result |
|---|---|
| active row, consent null | screens open in gate mode; `window.botpress.init` calls = 0; connected actions, tab bar, memory icon, threads all hidden; `clientId`/`therapistLink` null |
| ... then "Start talking to Alo", PATCH 204 and row now consented | button disabled in flight; overlay closes; init calls = 1; connected UI; `session_metadata` written only after the gate |
| ... PATCH returns 500 | overlay stays on screen 4, constant copy shown, button re-enabled, init calls = 0 |
| ... PATCH returns 204 but the row is unchanged (RLS-filtered write) | same as the 500 case: stays closed |
| active row, consented | no overlay; init calls = 1; connected UI |
| signed in, no link (memory row absent, 2nd visit) | init calls = 1; signed-in UI; memory shows ON; card reads "Alo remembers context" with one button |
| signed out | init calls = 1; guest UI; guest card hidden; prompt bar hidden |

The real `dev.html` (unmodified, live Botpress and Supabase CDNs) loaded as a guest in headless Chrome: "[Alo] Botpress webchat initialized", loading overlay hidden, no console errors.

Read-only probe with the public anon key: `GET /rest/v1/therapist_clients?select=consent_acknowledged_at` returns HTTP 200 (a bogus column returns 400), so the column exists on the live database (migration `20260902120100_onboarding_columns.sql` in alo-supabase).

## 6. Not verifiable without Supabase access (Kano's evening check covers these)

- The consent PATCH under RLS Phase 1 as the Z account: that the client may update its own row's `consent_acknowledged_at`. If RLS filters it, the app now stays closed with the constant copy (verified above), and the fix is a policy, not client code.
- The actual state of Z's row after Tuesday's 1.3 claim (consent null is assumed).
- That the bot's server-side memory default with no `client_settings` row is ON, which the brief's truth table states; B1 only changes the display default.
- Sign-in through the login modal end to end (no credentials in this session; the harness stubs auth).
- Phone-width rendering of the new error line on screen 4 (inline style, same pattern as the login error; no dev.css change).

## 7. Kano's five-minute walk on alowen.ai/dev.html

1. Signed in as Z with the unconsented row: the four screens appear on load; the header behind them is the initial one; Network tab shows no `cdn.botpress.cloud` webchat traffic beyond `inject.js` itself until step 3.
2. Wi-Fi off, tick the box, tap "Start talking to Alo": the button greys out, then the copy "Something didn't go through. Nothing was changed. Try again in a moment." appears under the checkbox and the button is enabled again. Wi-Fi on, tap again: overlay closes, "Loading Alo..." then the chat, badge "Hi ... with <therapist>".
3. Reload: straight to chat.
4. Fresh account (no memory row): memory icon shows ON; reload once; the card reads "Alo remembers context" with "Got it".
5. About modal: "How memory works" and "Your privacy" match section 3.

## 8. Declined or left alone, and why

- Path R / item F: Path P was set. `redeem_invite_code` not called.
- Everything in the brief's "Not in scope" list: no waiting room, unbundled consent, history switch, disclosure cadence, deletion flow, guest-chat removal, new column/RPC/edge function, or state-naming constant.
- Login modal title/body ("Sign In or Create Account", "Create an account to save your conversations...") left unchanged: not on the D1 surface list, auth-sensitive, and it is also the invite-code signup path, whose availability this session could not confirm. Flagged for Kano; a copy-only change if signups are confirmed off.
- Privacy Policy "We don't sell or share your data with third parties" left unchanged: not in the truth table; conversations are processed by the chat provider and the LLM, which is a legal-review question, not a build fact.
- Journal empty state / About "Alo may reference your journal entries" left unchanged: whether the bot reads journal entries is a Botpress-side fact this session cannot verify.

## 9. Pre-existing behaviour noticed, not changed (outside section 1)

- On a modal sign-in, `loadConnectedState()` runs twice (SIGNED_IN listener plus the explicit call). Both entries are gated; the guard keeps the second from resetting the screens. When the modal carries an invite code, the listener's pending-invite claim can race the explicit one and toast "Invalid invite code" after "Connected successfully!"; the re-read at line 2016 now lands that path at the gate rather than in a half state.
- A private session started from "Start new private conversation" still inserts an empty `conversations` row (`is_private: true`) that lists in the sidebar with 0 turns.
- A link read that hangs without erroring shows the spinner with no 15 s fallback, because that timeout is now armed at Botpress init (so a client reading the screens is never told the chat is slow). A read that errors shows the load-error state.
- `showConnectPrompt()` can still appear 800 ms after the signed-in UI when a claim is happening in parallel; it sits below the gate overlay (z-index 10000 vs 15000).
