# S4A — Consent gate, waiting room, client-owned history, deletion flow — Report v1.0

Repo: `alo-client-chat-full_v1` · Branch: `auto/s4a-consent-gate` (off `main` @ `1eadd8c`) · Files: `dev.html`, `dev.css`, `CLAUDE.md`, `docs/` · Date: 2026-09-14

## Session Log

**Interruptions / restarts:** none. One tool call (the first headless-Chrome screenshot run) exceeded its 180 s timeout because Chrome stayed alive after writing the screenshot; it was killed and re-run with a hard kill timer. No context resets.

**Model:** Claude Fable 5.1 (`claude-fable-5-1`), effort MAX, session-scoped auto mode. Remote Control: linked (a "Remote Control" peer session was listed at preflight).

**Preflight:** working tree was clean, so no `auto/pre-s4a` backup branch was needed. `git pull` on `main` was already up to date. Branch created from `main` @ `1eadd8c`. The stray root file `padding: 8px 12px;` was `git rm`'d in the first commit ("Remove stray file created by a shell redirect"). `CLAUDE.md` read in full; `dev.html` read end to end before editing.

**Commits on the branch (in order):**

| Commit | Item |
| --- | --- |
| `4faa5f1` | Remove stray file created by a shell redirect |
| `389f81e` | 4.A access gate, waiting room, deferred Botpress init, guest chat removed |
| `22745ac` | 4.B unbundled consent screen, atomic claim via `redeem_invite_code`, renewal mode |
| `4f8f78c` | 4.C client-owned conversation history switch; memory needs history (R-1) |
| `c6cd0b7` | 4.D AI disclosure cadence |
| `a0eee01` | 4.E export my data, server-owned deletion with receipt |
| `b21a08a` | 4.F copy corrections (A-23) and memory-onboard card retired |
| `3f91142` | 4.C follow-up: private session available whenever history or memory is on; CSS cache buster v16 |
| `51ba80f` | 4.G CLAUDE.md refresh + consent-gate contract v1.0 |
| (final) | report + screenshots |

`python3 scripts/scan-invisible.py dev.html dev.css` returned CLEAN before every commit, and `node --check` passed on every inline script block before every commit.

**Task checklist:**

| Item | Status | Notes |
| --- | --- | --- |
| 4.A gate + waiting room | done | `aloComputeAccess`, one link query, Botpress init deferred to `aloOpenChat()`, waiting room for every non-chat state, guest path removed, journal read-only without chat, chat-only header/menu items hidden |
| 4.B consent screen + atomic claim | done | screens 1–3 edits, screen 4 rebuilt, peek → screens → redeem, renewal mode, read-only mode, old claim/consent writes deleted, sign-up never opens the gate |
| 4.C history switch + memory dependency | done | plus one follow-up commit (private session gating, see deviations) |
| 4.D disclosure cadence | done | `aloDisclosure` module, `#aloDisclosureLine` |
| 4.E deletion flow | done | export, typed-DELETE confirm, edge function, receipt; account scope signs out and shows the receipt on the waiting room |
| 4.F copy corrections | done | every replaced/deleted sentence listed below with its original line number |
| 4.G CLAUDE.md refresh | done | plus `docs/contracts/consent-gate-contract-v1_0.md` |
| §6 verification | done, with one substitution | Playwright could not be installed (`npm install` was denied by session permissions); headless Google Chrome 153 was used instead — details under Verification |

**Deviations from the brief, and why (each defaulted and recorded, not asked):**

1. **Commit granularity.** The 4.A commit carried an interim `aloStartConnectFlow` that bridged the waiting-room code field to the old claim path so every commit on the branch loads and runs; 4.B replaced it. The removal of the `isNewInviteSignup` trigger (4.B.5) also landed in the 4.A commit because the login modal was being rewritten there.
2. **Link select has three extra columns** beyond the brief's list: `consent_collect_at`, `consent_share_safety_at`, `attest_location`. Needed so the read-only screen 4 (4.B.7) can render what the user agreed to from the link row.
3. **Unknown link status** (anything other than `pending`/`active`/`archived`) → `no_link` (closed, code field shown). `pending` renders with the signed-in no-link copy, as the brief allows.
4. **`aloComputeAccess(link, settings)`** keeps the `settings` parameter in its signature but does not use it: the v1.0 contract gates on the link row alone.
5. **RPC error copy for codes §5 does not cover** (contract 3.2 says "matching copy from §5", which only has the invalid-code line): `already_linked` → "This account is already connected to a therapist."; `not_authenticated` → "You're signed out. Sign in and try again."; `consent_incomplete` → "Each required box needs a check before Alo can connect you."; `no_active_link` → "There's no active connection to review. A new code from your therapist reconnects you." Everything else → the generic line. Raw error text never reaches the screen.
6. **`consent_outdated` waiting-room heading** is "A quick review" (the brief gave body copy only); body is §5.5 verbatim.
7. **Renewal mode** opens directly at screen 4 (screens 1–3 stay available via "How Alo works"), hides the "4 of 4" progress marker, and pre-fills the optional memory box from the account's current setting so re-confirming never silently changes it. Because the contract's `renew_consent` updates consent columns only, the memory choice is applied client-side afterwards via `aloSaveSettings` (on → history + memory on; off → memory off). See open question 1.
8. **Read-only screen 4** keeps "Back" and "Done" as navigation (I read "no buttons" as no consent-action buttons; the × close also works). Title is "What you agreed to" when a link row exists, "Before you connect" otherwise. The memory box reflects the account's current `memory_enabled` (the link row has no memory column).
9. **Close (×) and Escape** are available in gate and renew mode and behave exactly as "Not now": nothing written; in gate mode the waiting room shows §5.7. In renew mode "Not now" shows no note (§5.7 is about a code).
10. **Receipt, Botpress `failed` status:** the brief specifies the 30-day suffix for `partial` only. For `failed` the line reads "Chat provider copies — 0 of N removed — this part did not complete. You can try again, or email kano@alowen.ai." (adapted from the §3.3 failure copy). `complete` gets no suffix.
11. **More-menu memory block** (inline toggle + detail text) replaced by a "Memory and history" menu item that opens the popover, so both switches live in one place. The header memory icon and the sidebar link now say "Memory and history".
12. **`#shareGuestBtn`** (header "Share" for guests) removed with the guest path; signed-in Share stays in the menu.
13. **`loadConnectedState` re-entrancy guard** added: the SIGNED_IN listener and the explicit call after sign-in overlap, and the new pending-invite hand-off must run once.
14. **4.C follow-up:** private sessions were gated on memory alone; with history now a separate switch that stores the transcript, a private session is offered whenever history **or** memory is on ("History and memory are off — nothing is being kept" otherwise).
15. **`.btn-primary.btn-danger` CSS rule** added — `createModal({ dangerous: true })` sets that class and it had no rule; used by the typed-DELETE confirm.
16. **Journal read-only** hides Edit, Pin, Share and "Bring this to Alo" (Delete kept), per "viewing, export, delete only".
17. **localStorage transcript backups** (`alo_dropped_messages`, `alo_unsent_messages`) are skipped while history is off and during private sessions.
18. **Login modal first paragraph** rewritten (it promised "save your conversations"); the popover's first-open tip rewritten ("History and memory are off unless you turn them on here.").
19. **Return-disclosure heuristic** when `alo_last_active_at` is missing: the account counts as returning if the auth user's `created_at` is ≥ 7 days old.
20. **`profiles.display_name` seeding** from `client_display_name` kept after a successful redeem (client's own row, not `therapist_clients`).
21. **`aloConsumePendingInvite`** clears `user_metadata.invite_code` (one `supabase.auth.updateUser` call, the pre-existing pattern) and `localStorage.alo_pending_invite` before the flow starts, so declining consent can never re-open the gate on a later load. The code stays in the field.
22. **Extra artifact:** `docs/reports/s4a-waiting-room-375.png` alongside the required 390 capture (CLAUDE.md asks for both widths).

## What changed (by function)

**Constants and state** — `ALO_CONSENT_VERSION`, `ALO_PILOT_LOCATION`, `ALO_DISCLOSURE_RETURN_DAYS`, `ALO_DISCLOSURE_INTERVAL_MS`, `ALO_DISCLOSURE_GAP_MS`; `historyEnabled` (default false), `aloAccessState`, `aloLatestLink`, `aloSignedIn`, `aloAccountCreatedAt`, `aloJournalReadOnly`, `aloPrefillCode`, `botpressInitStarted`, `_aloIdentityReady`, `_aloPendingReceipt`.

**4.A**
- `aloComputeAccess(link, settings)` — new, pure; returns `chat | no_link | pending | consent_outdated | paused | ended` in the brief's order.
- `aloFetchLatestLink(userId)` — new; own rows, any status, `order=updated_at.desc&limit=1`, retried with `created_at.desc` if the first query fails.
- `loadConnectedState()` / `_aloLoadConnectedState()` — rewritten: profile fallback kept; one link query; non-chat states → `showLoggedInNoConnection()` + `aloShowWaitingRoom(state)` (+ `aloConsumePendingInvite` for no_link/pending); chat state → `showConnectedUI`, `aloOpenChat()`, `loadMemorySettings`, `loadHomework`, session metadata write, `aloSendBotpressUserData()`, `sendAuthBridge()`. A failed link query renders the `error` waiting room (fail closed).
- `aloShowWaitingRoom(state, opts)`, `ALO_WAITING_COPY`, `aloWaitingRoomNote()` — new; the only place the waiting room is drawn; hides `#aloFrame` and the loading overlay, hides the webchat if one exists, puts the journal in read-only mode, hides the disclosure line.
- `aloSetJournalReadOnly()` — new; `body.alo-journal-readonly` hides the composer and prompt card; `initJournalView` and `viewJournalEntry` honour it.
- `showLoggedInNoConnection()` — rewritten: no connect prompt modal, chat-only icons hidden, tab bar shown, `aloSyncMenuForAccess(false)`.
- `aloSyncMenuForAccess(isChat)` — new; hides Conversations, Share, Message Therapist, private-session items, Memory and history, and the divider outside chat.
- `resetToGuestUI()` — rewritten: clears state, signed-out header, waiting room (`no_link`, signed out, with any pending deletion receipt).
- `aloOpenChat()` — new; the only `window.botpress.init` call; the `webchat:initialized`, `webchat:closed` and `message` handlers and the 15 s load timeout moved here; idempotent on later calls.
- `aloSyncWebchatVisibility()` — new; replaces the two inline cssText blocks in `switchTab`; `positionWebchat` also returns early unless `aloAccessState === 'chat'`.
- `aloSendBotpressUserData()` / `aloBotpressAvailable()` — new; one `updateUser` payload (sessionNonce, clientId, homeworkActive, timeZone, `historyEnabled`, `memoryEnabled`, `privateSession`, all strings), sent after the metadata write, again on `webchat:initialized`, and on every toggle.
- `sendAuthBridge()` — waits for `botpressInitStarted` as well.
- `showLoginModal()` — copy fix; after auth only `loadConnectedState()` (no direct claim, no gate).
- `_aloHandleInviteParam()` — prefills the waiting-room field instead of opening a modal.
- `_aloExchangeClientToken()` — returns true/false; on failure the signed-out waiting room renders under the one constant message (D31 unchanged).
- `handleLogoClick()` / `startNewConversation()` — guarded on an open chat.
- Deleted: `showConnectModal`, `showConnectPrompt`, `showGuestBenefitsCard`, `dismissGuestBenefits`, `checkGuestMemoryPrompt`, `hideMemoryPrompt`, `guestTurnCount`, `#guestBenefitsCard`, `#memoryPromptBar`, `#shareGuestBtn`, the "Connect to Therapist" menu item, and their CSS.

**4.B**
- `ALO_ONBOARDING_SCREENS` — screen 1 opens with "Alo is an AI, not a person."; screen 3 gains the "Telling Alo is not telling your therapist…" paragraph after the 988 paragraph.
- `ALO_DATA_POSTURE`, `ALO_CONSENT_ROWS` (5 rows, §5.6 verbatim), `ALO_NOT_NOW_COPY`.
- `_aloOpenOnboardingScreens(mode, ctx)` — modes `gate | renew | readonly`; `_aloCloseOnboardingScreens()` — close/Escape/Not now; gate mode shows §5.7 in the waiting room.
- `_aloRenderOnboardingScreen()` — screen 4: title, data-posture line, "Connecting you with {therapist}" (gate) or §5.5 (renew), five checkbox rows (unchecked; renew pre-fills memory), "Consent version consent-2026-09-v1.3", error line, Connect/Continue (enabled only when the four required boxes are checked) + Not now; read-only: rows checked-and-disabled from the link row.
- `_aloBuildConsentPayload()` — the contract's `p_consent` shape; `_aloConsentSubmit()` — `redeem_invite_code(p_code, p_consent)` or `renew_consent(p_consent)`; success → close, toast "Connected to {therapist_name}" / "Saved", `loadConnectedState()`; failure → stays on the screen with mapped copy.
- `aloStartConnectFlow(code)` — `peek_invite_code` → invalid → §4.B.3 line; valid → screens in gate mode. Signed out → login modal with the code.
- `aloStartRenewal()`, `aloRpcErrorCopy(err)`, `aloSaveSettings(partial)`, `_aloApplyRenewedMemoryChoice()`, `_aloSeedClientDisplayName()`, `aloConsumePendingInvite(user)`.
- Deleted: `handleConnectSubmit` (PATCH claim), `_aloOnboardingComplete` (consent PATCH + localStorage fallback), `_aloOnboardingConsentToggled`, `isNewInviteSignup`.

**4.C**
- `loadMemorySettings()` — reads `memory_enabled, history_enabled`; missing row/column or failed read → both OFF; memory can only be on with history on.
- `handleHistoryToggle(enabled)` — new; OFF writes `{history_enabled:false, memory_enabled:false}`; ON writes `{history_enabled:true, memory_enabled:<current>}`.
- `handleMemoryToggle(enabled)` — rewritten around `aloSaveSettings`; refuses ON while history is OFF.
- `updateMemoryUI()` — syncs both switches, disables memory while history is off, shows "Memory needs conversation history on.", renders the therapist's `allow_history` sentence (true/false/absent), gates `#threadsBtn` and the Conversations menu item on `historyEnabled && chat`.
- Popover HTML rebuilt (history above memory, `#historyToggle`, `#memoryToggle`, `#aloHistorySuggestion`, `#aloMemoryNeedsHistory`); `toggleMemoryGlobal` and the popover's "Turn off memory" action removed.
- `ensureConversation()` returns null and `saveMessage()` returns early while history is off; the `message` handler returns before content extraction when history is off.
- `togglePrivateChatFromHeader()`, `startNewPrivateConversation()`, private button visibility — gated on history **or** memory (follow-up commit).

**4.D**
- `#aloDisclosureLine` (`role="status"`, `aria-live="polite"`) before `<main>`; `aloDisclosure` module with `onChatOpen()`, `onUserMessage()`, `hide()`; `alo_last_active_at` written on chat open and every user message.

**4.E**
- `_aloShowPrivacyModal()` — now builds the modal (the footer link calls it); copy corrected; "Your data" (Export my data, Delete my data) and "Your account" (Delete my account) sections when signed in.
- `aloExportMyData()`, `aloDownloadJSON()` — `alo-export-YYYY-MM-DD.json`; all-or-nothing; the failing part is named.
- `aloConfirmDelete(scope)` — §5.8 copy, typed DELETE enables the button; `aloCallDeleteFunction(scope)` — contract 3.3; `aloAfterDeletion()` — clears local conversation-id mappings and message backups; account scope signs out and shows the receipt on the waiting room; `aloReceiptHTML(receipt)` — §5.9 from the response only. Waiting room (paused/ended/no_link signed in) has the same Export/Delete buttons.

**4.F**
- About modal "How memory works" replaced with the three approved sentences; "Guests start fresh" line removed; "Your privacy" paragraph rewritten.
- `startNewConversation` confirm copy now depends on history/private state; private-session tip rewritten.
- Deleted: `#memoryOnboardCard`, `checkMemoryOnboarding`, `enableMemoryFromOnboard`, `dismissMemoryOnboard`, keys `alo_memory_onboard_done / _ask / _dismiss_count`, their CSS and keyboard-open rule.

**Copy sentences replaced or deleted (original line numbers in `dev.html` @ `4faa5f1`):**

| Line | Original sentence | Action |
| --- | --- | --- |
| 216 | "Guest conversations aren't saved after the session ends. If you're signed in, you stay in control: turn memory off, start a private session (nothing gets saved), or ask Alo to forget a specific topic." | replaced: "You stay in control: turn history or memory off, start a private session (nothing from it goes into your history or memory), or ask Alo to forget a specific topic." |
| 228 | "Alo doesn't store your conversations word for word. When memory is on, it keeps brief notes — just enough to pick up where you left off next time." | replaced with the brief's three "How memory works" sentences |
| 230 | "Memory is available when you're signed in. Guests start fresh every visit." | deleted |
| 287 | guest benefits card: "Create a free account and Alo can remember your conversations…" | deleted with the card |
| 176 | menu memory detail: "Alo keeps short summaries of recent conversations (not full transcripts) for continuity…" | deleted with the block |
| 241 | popover: "Alo uses short summaries from recent conversations for continuity. Your therapist cannot see this." | replaced by the two switch descriptions (history sentence verbatim from the brief) |
| 302–303 | memory onboard card copy | deleted with the card |
| 340 | "Want Alo to remember your conversations?" (guest prompt bar) | deleted with the bar |
| 843–844 | connect prompt: "No therapist? No problem — Alo works great on its own." | deleted with the prompt |
| 1449 | "Create an account to save your conversations and let Alo remember what you've discussed." | replaced: "Sign in to Alo, or create an account. An invite code from your therapist connects you after you sign in." |
| 2818 | tip: "Alo remembers a little between conversations so you don't have to start over. You can clear it anytime." | replaced: "History and memory are off unless you turn them on here." |
| 2868 | tip: "This conversation won't be saved. Alo won't remember it next time." | replaced: "Nothing from this conversation goes into your history or memory." |
| 2901, 2921 | "Memory is already off — nothing is being remembered" | replaced: "History and memory are off — nothing is being kept" |
| 2976 | "Your current conversation is saved in your history." | now conditional on history/private state |
| 4027 | "If you have an account, conversations are saved so Alo can provide continuity" | replaced: "When conversation history is on, your conversations are saved so you can review them later. When it's off, nothing is kept after the session ends" |
| 4028 | "You can delete any conversation at any time from the sidebar" | replaced: "…at any time, or everything at once from this screen" |
| 4029 | "You can turn off memory in settings — Alo will treat each chat as new" | replaced: "Memory keeps brief notes between sessions. It needs history on, and you can turn either off in settings" |
| 4030 | "Guest conversations (no account) are not stored permanently" | deleted |

Reviewed and kept (accurate to the code): private-session banner "Private session — Alo won't remember this conversation"; toast "Private session — this conversation won't be remembered"; `clearAllMemories` confirm; `deleteThread` / `clearHistory` confirms; Terms modal. Kept but not verifiable from code: "Conversations are not used for training, analytics, or advertising" (privacy modal, pre-existing) — open question 4.

## Grep proofs (final tree)

```text
$ grep -n "therapist_clients" dev.html
481:    let aloLatestLink = null;           // latest therapist_clients row for this account, any status
1375:      var base = '/rest/v1/therapist_clients?client_id=eq.' + userId +      <- the one GET (select), no PATCH/POST
1707:    // The client app makes no direct write to therapist_clients, ever.
2017:    // signup default. profiles is the client's own row; not therapist_clients.

$ grep -c "rest/v1/therapist_clients" dev.html      -> 1   (a GET; the PATCH claim and the consent PATCH are gone)
$ grep -c "word for word" dev.html dev.css          -> 0 / 0
$ grep -c "guestBenefits" dev.html dev.css          -> 0 / 0
$ grep -c "memoryOnboard" dev.html dev.css          -> 0 / 0
$ grep -c "alo_consent_acknowledged_fallback" dev.html -> 0
$ grep -c "consent_acknowledged_at" dev.html        -> 0
$ grep -c "handleConnectSubmit\|showConnectModal" dev.html -> 0
$ grep -c "memoryPromptBar\|alo_memory_onboard\|alo_memory_prompt_dismissed\|Guests start fresh" dev.html dev.css -> 0 / 0
$ grep -n "window.botpress.init" dev.html
486:    let botpressInitStarted = false;    // window.botpress.init() has been called this page load   (comment)
4568:        window.botpress.init({                                                                   (inside aloOpenChat only)
```

## Verification results

1. `python3 scripts/scan-invisible.py dev.html dev.css` → `dev.html: CLEAN`, `dev.css: CLEAN` (run before every commit and at the final commit).
2. Every inline `<script>` block extracted and run through `node --check` (Node v25.8.0): block 1 (theme bootstrap, 10 lines) OK; block 2 (app, ~4,600 lines) OK. Run before every commit.
3. **Browser check — substitution.** Playwright is not installed and `npm install playwright-core` was denied by the session's permissions, so no Playwright. Google Chrome 153 (`/Applications/Google Chrome.app`) was driven headless instead (`--headless=new --screenshot` / `--dump-dom --enable-logging=stderr`) against `python3 -m http.server` serving the repo, signed out, no session in localStorage. Desktop Chrome clamps a headless window to 500 px wide, so the page was rendered inside a same-origin 390×844 (and 375×844) `<iframe>` harness served from the scratchpad and the capture cropped to the frame. Results:
   - DOM after load: `<div id="aloWaitingRoom" class="alo-waiting-room">` (visible), heading "Alo works alongside your therapist.", body copy §5.1, invite-code field, "Continue", "Sign in or create account"; `#aloFrame` has class `hidden`; `#loadingOverlay` `display: none`; `#tabBar` hidden; header shows Sign In.
   - `<iframe` elements in the DOM: **0**. Elements with class `bpWebchat`: **0**. No Botpress iframe was created.
   - Console: one line only, Chrome's own "Banner not shown: beforeinstallpromptevent.preventDefault() called…" (expected — the install banner is captured and never auto-prompted). No errors, no uncaught exceptions, no CSP violations.
   - Screenshots: `docs/reports/s4a-waiting-room-390.png` (390×844) and `docs/reports/s4a-waiting-room-375.png` (375×844), dark theme (host system preference).
4. Grep proofs: above.
5. No live test against Supabase was attempted; the RPCs, the consent columns, `history_enabled` and `delete-client-data` do not exist yet. `aloFetchLatestLink` selects the new columns, so against the current database the gate query fails and the app renders the `error` waiting room (fail closed) — expected until the migration runs.

## Open questions for Kano (yes/no)

1. Should `renew_consent` also upsert `client_settings` (memory/history) server-side, the way `redeem_invite_code` does, so the client-side memory apply after renewal (`_aloApplyRenewedMemoryChoice`) can be removed?
2. Does RLS on `therapist_clients` let a client select its own rows in every status (`pending`, `active`, `archived`)? The gate's single query depends on it.
3. Does `therapist_clients.updated_at` exist? (The query orders by it and falls back to `created_at` only if that request fails.)
4. Can you stand behind "Conversations are not used for training, analytics, or advertising" (pre-existing privacy-modal line) for Botpress and the model vendor under the current agreements?
5. OK that the read-only "How Alo works" screen 4 keeps "Back" and "Done" as navigation buttons?
6. OK that the renewal screen pre-fills the optional memory box from the account's current setting instead of starting unchecked?
7. OK to keep seeding `profiles.display_name` from `client_display_name` after a successful redeem?
8. OK that a private session is now offered whenever history or memory is on (previously memory only)?
9. Should "Delete my account" also appear in the waiting room (it is in the privacy modal; the waiting room has Export and Delete my data only)?
10. Should a legacy `pending` row with a `client_id` get its own waiting-room message instead of the signed-in no-link copy?

## Merge preconditions

Do not merge until the alo-supabase migration (consent columns, `peek_invite_code`, `redeem_invite_code`, `renew_consent`, `delete-client-data`) has been run and deployed — the branch's connect and delete flows depend on them.
