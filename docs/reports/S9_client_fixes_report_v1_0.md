# S9 client fixes report v1.0

Brief #5-client v1.0 (phone header, state cards, sign-in/out boundaries, history-off controls; rulings D40/D41, Sep 26-29). Branch `auto/s9-client-fixes`, created from `main` at `c48d26a` before any file was touched. Session ran 2026-10-01, 08:28 to 09:50 MDT (Claude Code, Claude Opus 5.5, effort max). Nothing was pushed to `main`. `index.html` and `styles.css` are untouched. The change is in `dev.html` and `dev.css` (so `dev.css?v=16` became `?v=17`), plus this report. Code commit: `ddf0764`. Line numbers are `dev.html` on this branch (5,261 lines) unless marked `main:` (4,981 lines).

## 0. Session log

**Run settings.** The brief asks for Fable 5.1 at effort max. This session ran on **Claude Opus 5.5 (1M context)** at effort max; the model was kept at launch (`/model`), and it cannot be changed from inside a session, so this is recorded as a deviation. Claude Code, bypass permissions.

**Interruptions.** One, at launch: the brief was not at `~/Downloads/claude_Brief_5_Client_Fixes_v1_0.md` (nothing in Downloads was newer than Sep 29). The session searched the home folder, Spotlight, iCloud and Google Drive, touched nothing, and asked Kano for the file; Kano saved it to that path and the session started from the top. No other stops or questions.

**Read order followed:** `CLAUDE.md`; `docs/reports/S8_client_claims_fixes_report_v1_0.md`; `docs/reports/S7c_identity_private_session_report_v1_0.md`; then `dev.html` (all 4,981 lines on `main`) and `dev.css` (all 3,873 lines) in full before the first edit. Before touching anything that calls the webchat: the Botpress webchat v3.3 bundles again (`inject.js`, `webchat.js`, as S7c did; S7c cites no docs URL, its source was the bundles), and the official Botpress webchat docs (section 3).

**No live contact.** No request reached the live Supabase API or Botpress Cloud. The harness answered every request locally and blocked every outside host at the browser's resolver. Fetched by anonymous GET: the public Botpress v3.3 bundles and supabase-js 2.39.0 UMD from their CDNs, and four botpress.com documentation pages.

**Deviations and interpretations**, each one a place where the brief left a choice:

1. **Model**, above.
2. **A, "narrow screens".** The pill drops "· with ..." at 640 px and below: the page's existing phone breakpoint, where the header icons are already hidden.
3. **B, what a signed-in account with no link keeps.** No chat, so no private-session items, no Share (it shares a conversation through a paste-into-chat flow), no "New conversation" in the sidebar, and the logo does nothing. No memory controls either (header eye, the menu's memory section, the sidebar's "Memory settings"): E scopes "Memory settings" to linked accounts, and no memory is ever loaded without a link. History stays (the sidebar opens; view, rename, pin, delete, clear), so the account keeps control of what is saved. Consequence: such an account has no "Clear all memories" button (section 7, point 9).
4. **B, "no first-use tips".** The one-time "Connect with your therapist" popup (800 ms after load) is gone with the chat: its line "No therapist? No problem — Alo works great on its own" is untrue on this build, and the card's button does its job. The Journal's own tip is untouched (the Journal is out of scope).
5. **B, the one change inside the Journal.** "Bring this to Alo" starts a conversation, so it is not offered on a page with no chat (4357). Without that, a no-link account tapping it got "Starting a new conversation..." and nothing else.
6. **B, a regression found by the harness.** The menu's theme item label ("Light Mode" when dark) was set in the `webchat:initialized` handler; a no-link page has the menu but no webchat, so in dark mode it said "Dark Mode" and switched to light. It is now set at page start (5040).
7. **C, the guest "Share" button** is hidden for a signed-out visitor (markup 107 starts it hidden; `resetToGuestUI()` keeps it so): it shares a conversation, and a signed-out visitor has none.
8. **C, the one line's wording** (the brief gives its content, not its words): "Alo is by invitation through your therapist, so you need to be signed in to chat". It replaces the guest sentence in About > Your privacy and the Privacy modal's guest item. About > How memory works lost its "Guests start fresh every visit." without a second copy of the line, so the About modal says it once. "What gets saved" has no guest-specific line (its rows are Normal / Memory off / Private session), so nothing changed there. Kano's eye.
9. **C, `?invite=`** is unchanged, as ruled: the connect modal with the code, then "Link" opens the sign-in modal, then the sign-in claims the code (`s9_invite_guest`, which passes on `main` too).
10. **D, what counts as a sign-in.** The first chat a page opens after it showed the signed-out card, the no-link card or the consent screens (and the `?t=` exchange) starts a new conversation (`_aloOpenChatAsNew`, 951). A page that loads straight into the chat resumes its conversation as before.
11. **D, the restart waits for `webchat:ready`**: before it, the SDK's `restartConversation` is a stub that throws, and the page's restart path would reload. If the webchat has not connected within 10 s, no restart is attempted and the page logs it (2667-2672).
12. **D, a different account signing in on a page** (the connect modal's "Sign in", or another tab) is handled as a sign-out of the previous account: the same cleanup, then a reload (2336). `_aloClaimBotpressOwner()`, which handed a running webchat to the account that signed in on top of it, is removed.
13. **D, a link that ends while a chat is open** reloads the page into the no-link card (`_aloShowStateCard`, 954): the webchat is laid over the chat area, so a card cannot be shown under it.
14. **D, sign-out storage.** The SDK has no documented way to clear its stored conversation (section 3). The strongest documented option, `restartConversation()`, is added. The S7 removal of the webchat's keys by name stays as it was: it is the only thing that removes the client's typed words from `botpress-message-history`. **Needs a ruling** (section 7, point 1).
15. **D, "Signing out…"** in the chat area while sign-out runs (1422) is my copy.
16. **D, a getUser network failure** on a page that still holds a session now leaves the page as it is (2323). It used to fall through to the guest UI, which would now be the signed-out card under a running chat.
17. **E, placement and wording.** "Memory settings" and "Delete my conversation history" sit in the private/memory group, after the private items. The delete uses Clear History's confirm as it stands (title "Clear conversation history?", buttons Keep / Clear History) with the ruled wording. Summaries are handled as Clear History handles them (marked `source_expired`, kept), which is what "Alo will still remember themes from recent sessions" says.
18. **E, beyond the letter: "Clear all memories" was invisible in the light theme.** Its colour used `--text-tertiary`, which is defined nowhere, so it fell back to white at 40%: 1.00:1 on the light theme's white panel, 3.7:1 on the dark one (measured, `main` and branch). "Memory settings" now brings every phone user to that button, so it takes the token its sibling actions use (`dev.css` 2322): 7.0:1 light, 7.5:1 dark.
19. **G and the light theme.** The menu icon now uses the other header icons' token in every theme, as ruled. In the light theme that lowers it from 9.5:1 to 4.8:1, the same as the others.
20. **F has no code change**: the fallback stays (section 2, F).
21. **`dev.css` changed** (A, B/C cards, G, point 18), so the cache-buster moved to `?v=17` (63).
22. **This repo is public.** The report describes what the page does and did, and what the published SDK bundles and docs say. It says nothing about the database beyond what the page's own source shows.

**Checklist (brief sections 2-4):**
- Branch created from `main` at `c48d26a` before any file was touched.
- Only `dev.html` and `dev.css` edited, plus this report.
- `scripts/scan-invisible.py dev.html dev.css`: CLEAN, exit 0, before each commit.
- Verification items 1 to 9 all pass (section 5).
- Report committed and pushed to `auto/s9-client-fixes`; the push verified with `git status` and `git log`.
- Not pushed to `main`; `index.html` and `styles.css` unchanged.

## 1. Summary

| Task | What changed | Where | Harness |
|---|---|---|---|
| A | The header's action group and the pill can shrink (`min-width: 0`); every other header item, the menu button above all, keeps its size (`flex-shrink: 0`). The pill's text box truncates with an ellipsis. At 640 px and below the pill shows the name only. | `dev.css` 288-306, 370-386, 506-511, 1723; `dev.html` 1016 | `s9_header` at 320, 375, 390, 414, 768, 1280 × light, dark, system-dark |
| B | Signed in, no active link: the no-link card, no Botpress init, no memory load, no memory card, no privacy bar, no popup; controls that need a chat or a link are not offered. Journal and history stay. | 416-423, 908-1003 | `s9_nolink`, `s9_nolink_claim`, `s9_link_ended`, `s9_header_states` |
| C | Signed out: the signed-out card, no Botpress init, no Share. The guest lines in About and Privacy are replaced by one line. | 408-415, 1167-1188, 232, 247, 5098 | `s9_signedout`, `s9_invite_guest`, `s9_token_failed`, `s9_header_guest`, `s9_copy` |
| D | Sign-in: the new chat's box opens only after the identity is verified and a new conversation has started (the private-transition restart). Sign-out: the conversation leaves the screen at once; blank identity, then `restartConversation()`, then close and unmount; storage removed (S7); reload to the signed-out card. A different account signing in on a page is a sign-out of the previous one. | 2629-2696, 951, 1381-1470, 2336, 5157 | `s9_signin_stale`, `s9_signin_consent`, `s9_token_ok`, `s9_signout`, `s9_signout_other_tab`, `s9_account_switch` |
| E | "Memory settings" in the menu for every linked account. With history off, "Delete my conversation history": every conversation of the account, pinned included, behind the adjusted confirm; success is checked against the server. "Clear all memories" made readable. | 173-183, 3047-3050, 3518-3570; `dev.css` 2322 | `s9_history_off` (phone and 1280), `s9_history_off_delete_blocked`, `s9_history_on`, `s9_clear_memories_contrast` |
| F | Diagnosed; no code change: the name is not readable by the client from anything the page may read; the fallback stays. | 2449-2452 (unchanged) | `s9_name_readable`, `s9_name_withheld` |
| G | The menu icon takes the other header icons' token (`--text-muted`) in every theme; the dark-only override is gone. | `dev.css` 370-386 | `s9_contrast` (light, dark, system-dark; 1280 and 500) |
| H | The memory tip points at the menu. No other sentence points at an icon hidden at 640 px and below. | 193 | `s9_copy` |

Harness (section 6): the branch passes all 229 runs (1,377 checks) with no page error: 45/45 brief scenarios on the Botpress stand-in, 33/33 on the real v3.3 bundles, 50/50 S7c/S8 regression scenarios in each tier, 51/51 at 375 px, 390 px and 375 px dark. `main` passes the same 100 regression runs and fails 40 of the 45 brief scenarios on the stand-in and 28 of the 33 on the real bundles; the 5 it passes in each tier are controls (section 6).

## 2. Task by task

### A - the phone header

**Diagnosis** (`main`, measured at 320, 375, 390, 414 px with a 40-character name):

| Element | `main` rule | Effect |
|---|---|---|
| `header` | flex, `space-between` | the brand and the action group share the width |
| `.header-actions` | `flex-shrink: 0` | the action group never gets narrower than its content |
| `.trust-badge.connected` (the pill) | `inline-flex`, `max-width: 280px` (160 px at 400 px and below), `overflow: hidden`, `text-overflow: ellipsis` | a flex item's `min-width` is its content, so inside a group that cannot shrink the pill takes its full max-width; and `text-overflow` on a flex container never applies to its text (a flex item), so no ellipsis ever showed: the text was clipped |
| `.more-btn` | no `flex-shrink` rule | nothing kept it in view |

Result on `main`: at 320 px the menu button starts at x=318 of 320 (`s9_header?w=320`: "menu button fully inside the viewport" fails, the tap at its centre hits nothing); at 414 px it is wholly off screen (screenshot); 375 and 390 px fit only because the 160 px cap applies below 400 px. `overflow-x: clip` on the page means no horizontal scroll: the button was simply cut off.

**Fix** (`dev.css`): `.header-actions` is `flex: 0 1 auto; min-width: 0`; every child of it and of `.connected-actions` is `flex-shrink: 0`, except `.connected-actions` and the pill, which may shrink (`min-width: 0`); `.more-btn` also carries `flex-shrink: 0` itself; `#trustBadgeText` is the box that truncates (`overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0`). The pill's markup gives "· with ..." its own span (1016), hidden at 640 px and below.

**Measured on the branch**, every width × light / dark / system-dark: the menu button is 44 × 44, wholly inside the viewport, and a tap at its centre reaches it; the pill is truncated with an ellipsis and ends before the button; nothing in the header passes either edge; no horizontal scroll. Geometry at 320 px: menu button 264-308 of 320; pill 106 px, "Hi kanomel…". The icons hidden at 640 px and below stay hidden; what they open is in the menu: Conversations (unless history is off), Start private session, and "Memory settings" (E).

### B - signed in, no active link

`showLoggedInNoConnection()` (908) now calls `_aloShowStateCard('noLink')` and sets the header and menu; it no longer calls `_aloInitBotpress()` or `loadMemorySettings()`, and no longer schedules the connect popup. The card (416-423) is the brief's copy verbatim. "Enter invite code" opens `showConnectModal()`, the existing connect flow. A pending link that needs consent still goes to the consent screens: that branch of `loadConnectedState()` is unchanged apart from marking the next chat as new.

`_aloApplyChatControls(hasChat)` (987) is the one place that offers or withholds the chat- and link-bound controls: the menu's private item and its divider, "Memory settings", the memory section, Share; the sidebar's "New conversation" and "Memory settings"; the header eye. It runs with `false` for a no-link page and `true` on every connected-state load. `startNewConversation()` and `handleLogoClick()` return when the page has no chat (`_aloHasChat()`, 941): the SDK's pre-init restart throws, and the page's restart path reloads.

### C - signed out

`resetToGuestUI()` ends in `_aloShowStateCard('signedOut')` instead of `_aloInitBotpress()`. The page-load path with no session and the failed `?t=` path both call `resetToGuestUI()` (5157-5180). The card (408-415) is the brief's copy verbatim; its "Sign In" opens the existing sign-in modal. A sign-in from the card loads the chat in the card's place (`_aloHideStateCards()`, 2446) and then follows D. The `?t=` failure still shows its one constant line (D31); the exchange function itself is untouched.

### D - sign-in and sign-out

Section 3.

### E - history off never removes a client's controls

- **"Memory settings"** (173) opens the existing memory popover (`toggleMemoryPopover()`), shown for every linked account by `_aloApplyChatControls(true)`.
- **"Delete my conversation history"** (179) is shown only while history is off (`_aloApplyHistorySetting()`, 3047). `deleteAllConversationHistory()` (3528) asks first with Clear History's confirm and the ruled wording, then: `PATCH conversation_summaries?client_id=eq.<id>&source_expired=not.is.true {source_expired: true, last_referenced_at}` (as Clear History marks them), `DELETE conversations?client_id=eq.<id>` (every row, pinned included), and a re-read. "Deleted" means the server no longer has them: a DELETE that the server filters down to nothing still answers 204, so the page re-reads and reports "Could not clear history. Try again." if any row is left (`s9_history_off_delete_blocked`). After a delete the page drops its mapping from the Botpress conversation on screen to its (deleted) row, so the next message starts a new row instead of failing (`s9_history_off`: "AFTER-DELETE" is saved).
- **The three deletion sentences** (About 244, Privacy modal 5096, What gets saved 262) are unchanged.

`s9_history_off` checks "nothing else": another account's conversation and summary untouched, the client's summaries kept (marked expired), the journal untouched, one DELETE, by account.

### F - the therapist's name

**What the page fetches.** `loadConnectedState()` reads `GET /rest/v1/profiles?id=eq.<therapist_id>&select=display_name` with the client's own token (2449) and falls back to `'Your therapist'` when `therapist?.[0]?.display_name` is empty (2452). The pill then reads "with Your therapist".

**What comes back, and why.** Two answers give that fallback: `[]` (the row is withheld from the client) or `[{display_name: null}]` (the therapist has no name). The second is unlikely: therapist accounts get a required, non-empty `display_name` at signup (`seed_therapist_account`, alo-supabase migration v1.5 step 3b). Nothing the page may read carries the therapist's name: the client's `therapist_clients` row holds the client's label, not the therapist's name, and no view or function the page could call returns it. The one server function that reads it, `redeem_invite_code`, runs with definer rights and only at claim time. The read rules on `profiles` are not in any repo in a form that settles whether a client may read its linked therapist's row (the client security review R-C listed this as unverified for the same reason). So the evidence points to the row being withheld from the client role. The live check is one console line (section 8, step 7).

**Decision.** Nothing the client is allowed to read carries the name, so the fallback stays, exactly as it was (`s9_name_withheld`: "Hi Sam · with Your therapist"). No policy was touched and nothing is fetched through any other key. If the live check returns the name, the profile is readable and the fallback comes from somewhere else; that needs looking at again.

### G - dark-mode menu icon

**Diagnosis.** `.more-btn` used `--primary-dark`, overridden to `--text-secondary` only under `[data-theme="dark"]`. A phone in dark mode with no toggle gets the dark theme from the system setting, where `--primary-dark` is `#1A2420`, the header's own colour. Measured on `main` with the system setting dark: 1.06:1, against 4.70:1 for the other header icons. With the explicit dark toggle it was 8.0:1 (that is why it looked fine on a toggled device).

**Fix.** `color: var(--text-muted)`, the other header icons' token, in every theme; the override is removed.

**Measured** (section 5, item 8): from the computed colour against the header's gradient at the icon's centre, the menu icon equals the other header icons in every theme (4.70:1 system-dark and dark, 4.84:1 light). From screenshot pixels, at phone widths (18 px icon) the menu icon peaks at exactly the info icon's value (4.76:1 at 375 px and 4.81:1 at 414 px system-dark, 4.87:1 light). At desktop size (20 px), thin horizontal strokes fall across two pixel rows, so the menu icon's peak is 3.27:1, identical to the list icon's line strokes (3.27:1); the eye and info icons peak higher because of their curves. `main` at desktop size did not register as an icon at all.

### H - copy

The memory tip now says "from the menu" (193). A search of every user-facing string for icon, eye, header, sidebar, settings, top, tap found one other place that names a location: the Privacy modal's "...at any time from the sidebar." It is one of E's three deletion sentences, kept as ruled, and it names a panel, not an icon (section 7, point 4).

## 3. Sign-in and sign-out: before and after

Measured with the real v3.3 bundles (`diag_signin_guest`, `diag_signout`; the stand-in agrees).

**SIGNED_IN from a guest page, `main`:**

| | What happened |
|---|---|
| (1) On-screen transcript | Stayed. The guest's turns ("GUEST-TURN", its reply) were still on screen after sign-in, and the conversation carried on. |
| (2) Botpress conversation and storage | The same Botpress user and conversation continued. `alo_bp_owner` was re-labelled from `g:<visit>` to `u:<client>`. `botpress-message-history` kept the guest's typed line (up-arrow recall). The client's first saved turn went into a history row for that same Botpress conversation, which on Botpress also holds the guest's turns. |
| (3) Identity on the Botpress user | The guest user (data `{}`) received the client's full five-key identity, verified by read-back. |

**Sign-in now:** a signed-out page has no webchat and no stored webchat state. After sign-in the webchat starts; the identity send is awaited and read back; then, once `webchat:ready`, `_aloRestartConversation()` (the restart the private on/off transitions use) starts a new conversation; then the composer is released and the bridge sent. Console, in order: `[Alo] Identity verified with Botpress (startup)`, `[Alo] Signed in: starting a new conversation`, `[Alo] New conversation started via restartConversation()`, `[Alo] Auth bridge sent to Botpress`. With a conversation this browser kept from an earlier session of the same account (`s9_signin_stale`), the box opens on the new conversation, never on the old one, and the first message goes into a new history row. The same holds after consent (`s9_signin_consent`), after an invite claim (`s9_nolink_claim`) and after the `?t=` exchange (`s9_token_ok`).

**SIGNED_OUT, `main`:**

| | What happened |
|---|---|
| (1) On-screen transcript | Still visible when sign-out started (webchat `visibility: visible`), through `signOut()`'s request and the up-to-2-s blanking; it left when `unmount('webchat')` removed the iframe; then the page reloaded. |
| (2) Botpress conversation and storage | `close()`, `unmount('webchat')`; the webchat's keys removed by name (`bp-webchat-<id>`, `botpress-message-history`, `webchat-sound-<id>`, three sessionStorage keys) and `alo_bp_owner`. The conversation was not ended. After the reload the guest page started a new webchat user and conversation. |
| (3) Identity on the Botpress user | Blanked: `clientId ''`, `sessionNonce ''`, `privateSession 'false'`, `homeworkActive '[]'` (2 s cap, no read-back). |

**Sign-out now** (`_aloSignOutCleanupAndReload()`, 1381): at once, `_aloHideAccountContentNow()` (1403) hides the webchat, removes every open modal (a saved transcript included), closes the menu, sidebar, popover and About, hides the journal, homework, banner and tab bar, and shows "Signing out…"; `positionWebchat()` stands down while it runs (4821). Then: blank the identity (unchanged); `restartConversation()` (new, 2 s cap, only once the webchat's conversation client is up); `close()`, `unmount('webchat')`; the storage removal (S7, unchanged); reload. Measured: the webchat was hidden at sign-out start; at unload there was no webchat in the page, the words were nowhere in it, and no webchat key was left; Botpress calls in order `updateUser` (blank), `restartConversation`, `close`, `unmount`; the next load shows the signed-out card and makes no webchat or Chat API request; the old Botpress user's data is blank. The conversation itself stays on Botpress (as "Deletion from the chat platform Alo runs on isn't in place yet" says).

**SDK methods used, and where they are documented** (Botpress webchat docs, fetched 2026-10-01; bundles v3.3.0, `inject.js` sha256 `bb1b4365c43c…`, `webchat.js` `ff66947745df…`):

| Method / setting | Used for | Documented |
|---|---|---|
| `window.botpress.restartConversation()` | sign-in (via `_aloRestartConversation`), sign-out | Yes: botpress.com/docs/webchat/interact/reference, "ends the current conversation and starts a new one". In the bundle it clears the message list and stores the new conversation id; it becomes real when the conversation client connects (`webchat:ready`, documented event), before that it throws "not initialized". |
| `updateUser()`, `getUser()` | identity send and read-back (S7c), blanking (S7) | Yes, same page |
| `close()` | sign-out | Yes, same page |
| `unmount('webchat')` | sign-out (S7, unchanged) | No: not in the methods reference; read from `inject.js` by S7 |
| Clearing what the webchat stores | - | **No documented way.** The methods reference has none, and neither does the user-data page. The documented "Chat history reset" setting (botpress.com/docs/webchat/get-started/configure-your-webchat: "Session storage creates a new user and conversation each time the page is re-opened. Local storage keeps them for your next visits.", the `storageLocation` init key in the v3.3 bundle) was considered and not used: it would change whether every client's conversation survives closing the tab, which the brief does not ask for, and the composer's recall list (`botpress-message-history`) is always kept in localStorage whatever it says. |

So the strongest documented option, `restartConversation()`, is implemented: it takes the transcript off the webchat, and if the storage removal ever missed a key (a renamed key under the same `/v3.3/` URL), the stored conversation would be a new empty one, not the client's. No new access to undocumented storage was added. The S7 removal by name stays (section 7, point 1).

**Nothing from a guest or earlier session is persisted into the new account's history.** A signed-out page has no webchat, so there are no guest turns. The local queues (`alo_unsent_messages`, `alo_dropped_messages`) are cleared at sign-out (S7) and nothing replays them. `s9_signin_stale` checks the history after sign-in: only the signed-in turn.

## 4. Copy: before / after

| Where | Before (`main`) | After (branch) | Source |
|---|---|---|---|
| Menu > Memory, the tip (main:177; 193) | ...You can start a private session anytime from the eye icon. | ...You can start a private session anytime from the menu. | brief H, verbatim |
| About > Your privacy (main:216; 232) | Guest conversations aren't saved to an account. If you're signed in, you stay in control: ... | Alo is by invitation through your therapist, so you need to be signed in to chat. If you're signed in, you stay in control: ... | brief C; **the line's words are mine** |
| About > How memory works (main:231; 247) | Memory and history are for signed-in accounts. Guests start fresh every visit. | Memory and history are for signed-in accounts. | brief C (the About modal says the one line once) |
| Privacy modal > Your Alo conversations (main:4822; 5098) | Guest conversations (no account) are not saved to an account | Alo is by invitation through your therapist, so you need to be signed in to chat | brief C; my words, as above |
| Signed-out card (new, 408-415) | (a guest chat) | **Alo is by invitation through your therapist.** Sign in to get started. [Sign In] If you need someone now, call or text 988. | brief C, verbatim; 988 is a `tel:` link |
| No-link card (new, 416-423) | (a chat the bot answered with a by-invitation line) | **Hi — I'm Alo.** I can't talk with you until your therapist's invite code is connected to this account. Once it is, I'm here. [Enter invite code] If you need someone now, call or text 988. | brief B, verbatim |
| Connect popup, no link (main:899-914) | Connect with your therapist / If your therapist gave you an invite code, ... / No therapist? No problem — Alo works great on its own. You can always connect later from the menu. [Enter Code] [Not Now] | (removed) | deviation 4 |
| Menu item (new, 173) | - | Memory settings | brief E |
| Menu item (new, 179) | - | Delete my conversation history | brief E |
| Delete-all confirm (new, 3525) | (Clear History's: This will delete all your unpinned conversations from your Alo account. Your pinned conversations won't be affected. Alo will still remember themes from recent sessions. This can't be undone.) | This will delete all your conversations from your Alo account. Alo will still remember themes from recent sessions. This can't be undone. (title and buttons as Clear History's) | brief E |
| Chat area during sign-out (new, 1422) | (the conversation, until unmount) | Signing out… | **mine** |
| Pill, 640 px and below (1016) | Hi {name} · with {therapist} | Hi {name} | brief A |
| Header "Share", signed out (main:107) | shown | hidden | deviation 7 |
| Journal entry, no link (4357) | Bring this to Alo | (not offered) | deviation 5 |

Byte-identical to `main` (checked over the diff: every removed line that is not a comment is listed above or is code): every other string, including all of Brief 4's ruled copy and the three deletion sentences (244, 262, 5096).

## 5. Verification (brief section 3)

| # | Item | How | Result |
|---|---|---|---|
| 1 | Header at 320, 375, 390, 414, 768, 1280 px, light and dark, 40-character email, 30-character therapist name | `s9_header` (`kanomelvin+zztest1-longaddress@alowen.ai`, `Dr. Alexandra Montgomery-Smith`) at the six widths × light, dark (toggle), dark (system setting): 18 runs per tier; 320-414 px in a same-origin frame | PASS 18/18 (stand-in), 6/6 (real bundles: 320, 414, 1280 × light, system-dark). Menu button inside, 44 × 44, tappable; pill truncated with an ellipsis; nothing past the edges; no horizontal scroll. `main` fails all 18 (button off screen at 320 and 414; no ellipsis anywhere) |
| 2 | Signed in, no link | `s9_nolink` (40 checks), `s9_nolink_claim`, `s9_header_states` | PASS. The card; no composer, no Botpress init, no Chat API request; no memory card (seeded to appear), memory settings not read; no privacy bar (seeded not dismissed); no popup; "Enter invite code" opens "Link to Your Therapist"; Journal lists, saves and opens entries; history opens without "New conversation". `main`: 25 of the checks fail |
| 3 | Signed out | `s9_signedout`, `s9_invite_guest`, `s9_token_failed`, `s9_header_guest` | PASS. The card; no composer, no init, no request; `?invite=` opens the connect modal with the code, then "Link" opens the sign-in modal and the sign-in claims; Sign In works |
| 4 | Sign-in: a new conversation, identity verified before the box opens | `s9_signin_stale`, `s9_signin_consent`, `s9_token_ok`, `s9_nolink_claim`, `s9_signedout`; console lines as in section 3 | PASS. Verified, then one restart, then the box opens on the conversation created after verification; nothing earlier on screen; the first turn reaches a bot holding the new nonce. `main`: the guest's conversation continues |
| 5 | Sign-out: transcript gone from the DOM and the webchat's storage; identity blanked; the card | `s9_signout` (phase checks at sign-out start and at unload, then the next load), `s9_signout_other_tab` | PASS. Hidden at sign-out start (an open saved transcript too); at unload no webchat and no key; Botpress user data blank; the next load shows the card. `main`: visible at sign-out start, no restart, a guest chat next |
| 6 | History off: menu items; delete removes every conversation and nothing else; history on unchanged | `s9_history_off` (phone and 1280 px), `s9_history_off_delete_blocked`, `s9_history_on`, `s9_clear_memories_contrast`, plus S8's `task_c_*` | PASS |
| 7 | The therapist name renders when readable; the fallback is exact otherwise | `s9_name_readable` ("Hi Sam · with Dr. Lee"), `s9_name_withheld` ("Hi Sam · with Your therapist") | PASS (both pass on `main` too: F changed nothing) |
| 8 | Dark-mode menu icon contrast ≥ the other header icons, measured | `s9_contrast` (computed colour against the header gradient at the icon's centre), plus screenshot pixels (section 2, G) | PASS: 4.70:1 = the others in dark and system-dark; 4.84:1 = the others in light. `main` system-dark: 1.06:1 |
| 9 | S7c and S8 scenarios; `node --check`; scan; no invisible characters in the diff | section 6; `node --check` on both inline scripts (348 and 217,831 characters); `scan-invisible.py`; a count over the diff's 475 added lines | PASS: regressions 50/50 in each tier; `node --check` exit 0 twice; CLEAN, exit 0; 0 of U+200B, U+200C, U+200D, U+FEFF, U+2060 (and 0 NBSP, 0 smart quotes) |

## 6. Harness

**Method** (the S7c/S8 harness, rebuilt this session; scratchpads are not kept between sessions). Headless Google Chrome 154, a local `python3 -m http.server`, a fresh profile per run, every outside host blocked at the resolver, virtual time. The harness copy of `dev.html` keeps the page's own CSP and replaces only its two CDN script tags. supabase-js is the real 2.39.0 UMD. `window.fetch` is answered in-page by an emulator: GoTrue (password, refresh, user, logout, verify), PostgREST with row-level rules per table, `redeem_invite_code`, the `?t=` exchange, and the Botpress Chat API routes read from the v3.3 `webchat.js` client (`/users`, `/users/me`, `/conversations`, `/conversations/{id}/messages|participants|listen` (fetch-based event stream), `/events`, `/messages`, and `inject.js`'s timing post `/p`). The emulator's state survives reloads, so multi-phase scenarios (sign-out, reload, account switch) keep their "server". 60 ms per Supabase request by default (0 ms in one scenario). A driver works the real UI with hit-tested taps, samples the composer every 5 ms, and instruments `window.botpress` the same way in both tiers.

Botpress, two ways:
- **Stand-in**, modelled on the v3.3 bundles as read this session: pre-init stubs (the restart one throws), `webchat:initialized` then `initialized = true`, restored or created user, the stored conversation shown on restore, `webchat:ready` after connect, `restartConversation` = new conversation, events wrapped as the real client sends them, the composer recall list, `unmount`.
- **The real v3.3 `inject.js` and `webchat.js`**, unmodified apart from their three script URLs, with a fetch shim prepended to `webchat.js` inside its iframe.

**Brief 5 scenarios** (45 on the stand-in; the 33 marked † also on the real bundles). `main` FAIL counts are failed checks.

| Scenario | What it encodes | `main` | Branch | Branch, real |
|---|---|---|---|---|
| `s9_header` ×18 (6 widths × light, dark, system-dark) † 6 of them | A, item 1 | FAIL (3-7) | PASS | PASS |
| `s9_header_states` † | the no-link header and card at 320 px | FAIL | PASS | PASS |
| `s9_header_guest` † | the signed-out header and card at 320 px | FAIL | PASS | PASS |
| `s9_nolink` † | B, item 2 (40 checks) | FAIL (25) | PASS | PASS |
| `s9_nolink_claim` † | no link → code → consent → a new conversation | FAIL (4) | PASS | PASS |
| `s9_link_ended` † | the link ends under a running chat → the no-link card | FAIL | PASS | PASS |
| `s9_signedout` † | C, item 3, and sign-in from the card | FAIL (17) | PASS | PASS |
| `s9_invite_guest` † | `?invite=` as a signed-out visitor | PASS (control) | PASS | PASS |
| `s9_token_failed` † | failed `?t=`: the card, the D31 line | FAIL (2) | PASS | PASS |
| `s9_token_ok` † | `?t=` is a sign-in: a new conversation | FAIL (3) | PASS | PASS |
| `s9_signin_stale` † | D, item 4, with a conversation this browser kept | FAIL (4) | PASS | PASS |
| `s9_signin_consent` † | client → consent → chat | FAIL (3) | PASS | PASS |
| `s9_signout` † | D, item 5 | FAIL (4) | PASS | PASS |
| `s9_signout_other_tab` † | sign-out from another tab with a saved transcript open | FAIL (2) | PASS | PASS |
| `s9_account_switch` † | a different account signs in on a no-link page | FAIL | PASS | PASS |
| `s9_history_off` (500 px, 1280 px) † | E, item 6 | FAIL (3) | PASS | PASS |
| `s9_history_off_delete_blocked` † | a delete the server did not carry out is reported | FAIL (2) | PASS | PASS |
| `s9_history_on` † | E with history on; the sidebar as before | FAIL (2) | PASS | PASS |
| `s9_clear_memories_contrast` (light, system-dark) † | deviation 18 | FAIL (3) | PASS | PASS |
| `s9_name_readable`, `s9_name_withheld` † | F, item 7 | PASS (controls) | PASS | PASS |
| `s9_contrast` (1280 light, dark, system-dark; 500 system-dark) † | G, item 8 | light and dark PASS (controls); system-dark FAIL (1.06:1) | PASS | PASS |
| `s9_copy` † | H and C copy, rendered | FAIL (5) | PASS | PASS |

**S7c and S8 regressions** (50 scenarios, each run on `main` and the branch, stand-in and real bundles):

| Group | Scenarios | `main` | Branch |
|---|---|---|---|
| Startup handshake (S7c A, B) | `load_linked` (= S7c `startup_verified`), `startup_new_bp_user`, `startup_stale_once`, `startup_fails_twice`, `startup_getuser_fails_twice`, `startup_nodata`, `startup_hangs`, `startup_update_timeout_once`, `startup_metadata_write_fails`, `startup_profile_read_throws`, `fast_supabase_cold_webchat`, `bridge_order`, `refresh_reentry`, `refresh_during_private`, `concurrent_entries`, `homework_identity` | PASS, both tiers | PASS, both tiers |
| Private sessions (S7c C-F, S8 E) | `private_start_menu` (= S7c `private_start`), `private_start_popover`, `private_end_x`, `private_end_menu`, `new_private_while_private`, `new_conversation_while_private`, `private_start_fails`, `private_start_lands_but_times_out`, `private_end_fails`, `memory_off_private`, `private_end_late_reply`, `stuck_private_no_marker`, `reload_private_marker`, `private_reload`, `task_e_menu` (= S7c `menu_private_toggle`), `f_banner_x_overlay` | PASS | PASS |
| Gates and sign-in (S7c, S8 A, B) | `gate_consent`, `signin_without_reload`, `task_a_wrong_password`, `task_a_unknown_email`, `task_b_no_reset` (+ `task_a_dormant`) | PASS | PASS |
| History setting (S8 C) | `task_c_history_off`, `task_c_history_off_desktop`, `task_c_history_on`, `task_c_history_on_desktop`, `task_c_history_live` | PASS | PASS |
| Homework (S8 D) | `task_d_homework` | PASS | PASS |
| No-link copy (S8 section 3) | `classd_linked`, `classd_unlinked`, `classd_guest`, `about_table` (375, 390 px) | PASS | PASS |
| Pages without identity | `guest_unaffected`, `nolink_unaffected` | PASS | PASS |

S8 scenarios whose expectation this brief changes were re-cast, not dropped: `load_guest` → `s9_signedout` + `guest_unaffected` (a signed-out page now has no chat at all; nothing is written either way); `load_unlinked` → `s9_nolink` + `nolink_unaffected` (no popup, no chat); `logout` → `s9_signout` (the next page shows the card, not a guest chat); `task_a_signin_ok` → `s9_signedout` and `signin_without_reload`; `task_a_invite_guest` → `s9_invite_guest`; `task_c_unlinked` → `s9_nolink`; S8's `copy_*` → `s9_copy` plus the diff audit in section 4; S7c `f_banner_x` and `f_banner_x_nobar` → `private_end_x` (the 44 × 44 X, hit-tested) and `f_banner_x_overlay`. `classd_unlinked` no longer checks the private banner for a no-link account: such an account cannot start a private session now.

**Phone widths** (`CLAUDE.md`: 375 and 390): 16 scenarios (`s9_nolink`, `s9_signedout`, `s9_signout`, `s9_signin_stale`, `s9_history_off`, `s9_history_on`, `s9_copy`, `s9_clear_memories_contrast`, `s9_nolink_claim`, `s9_header_states`, `s9_header_guest`, `private_end_x`, `task_e_menu`, `about_table`, `classd_linked`, `task_c_history_off`) at 375 px light, 390 px light and 375 px system-dark, plus three on the real bundles: 51/51. Screenshots, checked by eye in both themes: both cards centred and whole at 320 and 375 px with the 988 line and a 44 px button; the phone menu with history off (Start private session, Memory settings, Delete my conversation history, the memory switch and its tip, Log Out); the no-link menu (Conversations, theme, About, How Alo works, Your privacy, Connect to Therapist, Log Out); the delete confirm as a bottom sheet; the memory sheet from the menu; the header at every width.

**Totals.** Branch: 229 runs, 1,377 checks, all pass; no page error. The only console errors in branch runs are the expected ones inside the failure-injection scenarios (identity failures, the failed metadata write, the failed profile read, the blocked delete). No run needed a retry. `main`: 100/100 regression runs pass; 78 brief runs, 10 pass (the controls above, in both tiers).

**Harness artefacts**, fixed in the harness and not in the page: the real `webchat.js` builds its `Request` objects inside its own iframe, so the emulator duck-types them (`instanceof` fails across realms); the real client posts events as `{type: 'custom', data}`, which the stand-in now mirrors; `inject.js` posts its timings to `/<clientId>/p` from the page; `--dump-dom` renders no frames, so motion is off in the harness copy; `isPrivateSession` turns on before the private restart (S7c's design, so nothing in the new conversation is written) and the banner after it, so scenarios wait for the banner.

## 7. Declined, rulings needed, observations

Declined (out of scope by the brief): the bot; `index.html`; the parked branch; the consent flow; the Journal (apart from deviation 5); About/Privacy restructuring beyond the named lines; the memory-aware greeting.

**Needs a ruling:**

1. **D: the S7 storage removal by name.** The brief says "do not reach into undocumented storage". The page already did, since S7: at sign-out it removes the webchat's keys by name, and that is the only thing that removes `botpress-message-history`, the client's last ~100 typed messages in plaintext. That key is not tied to any user: the next account to sign in on the browser would load it, and could step back through the previous client's words with up-arrow. So this session added no new access to undocumented storage, kept the S7 one, and added the documented `restartConversation()`. If the intent was to remove the S7 removal, it is one call (`_aloClearBotpressStorage()` in `_aloEndBotpressIdentity()`), with that consequence.
2. **C-052, the sign-in modal:** "Sign in to save your conversations and let Alo remember what you've discussed. New accounts are set up by invitation." It implies a signed-out visitor can talk without saving, which is no longer so. It is ruled copy (Brief 4) and not in this brief's list, so it is unchanged. Something like "Sign in to talk with Alo. New accounts are set up by invitation." would fix it.
3. **About > Your privacy, "If you're signed in, you stay in control: turn memory off, start a private session ..., or ask Alo to forget a specific topic."** It is untrue for a signed-in account with no link (no chat, no memory controls). Not in the named lines.
4. **Privacy modal, "...at any time from the sidebar."** It is one of E's three deletion sentences, kept as ruled. With history off, deletion is in the menu, not the sidebar.

**Found on the way, not changed:**

5. **Deleting the conversation on screen from the sidebar** (existing, `main` and branch): the page keeps writing to the deleted row, so with the database refusing that, the conversation's later messages are not saved, with no message to the client (console only). Measured with the emulator's foreign key (`obs_delete_current_thread`). The fix is the reset `deleteAllConversationHistory()` does, in `deleteThread()` when the deleted id is the current one.
6. **Primary buttons in the dark theme**: white on `--primary` is about 3.3:1 (`.btn-primary`, every primary button, the header Sign In included). The cards use the shared button.
7. **The phone keyboard and a no-link Journal.** The code that hides the header and footer while the keyboard is open lives in the webchat's start, so a no-link account (no webchat) keeps them while writing in the Journal. The Journal works; there is less room. Moving that code also touches the linked chat's keyboard positioning, which headless Chrome cannot exercise, so it was left.
8. **Sign-out without a network**: `signOut()` fails and the page stays signed in, showing the conversation (existing). A local-scope sign-out would be an auth change.
9. **A no-link account has no "Clear all memories"** (deviation 3). Deleting a conversation deletes its summaries; clearing unpinned ones marks them expired.
10. **The sign-in restart** creates a second conversation when the webchat's start already created a fresh one (one empty conversation on Botpress per sign-in). If the live bot greets on conversation start, a greeting may reach the first conversation and be saved as a one-message history row before the restart.
11. **"Signing out…"** also shows briefly when a different account signs in on top of a page (deviation 12).
12. **After a restart the auth bridge is bound to the conversation just left** (S7c's observation, unchanged; now also at sign-in).

## 8. Kano's check on alowen.ai/dev.html (after merge, about ten minutes)

1. **Phone, signed out** (a private window). Expect the card "Alo is by invitation through your therapist." with Sign In and the 988 line; no message box; no Share in the header. Tap the card's Sign In and sign in as zztest1: "Connecting…" briefly, then an empty conversation. On desktop with the console open, the order is: `Identity verified with Botpress (startup)`, `Signed in: starting a new conversation`, `New conversation started via restartConversation()`, `Auth bridge sent to Botpress`.
2. **Phone header, zztest1.** The ☰ is whole at the right edge; the pill reads "Hi kanomelvin+zz…" with an ellipsis and no "with …". Open ☰: "Memory settings" is there; tap it: the memory sheet, with "Clear all memories" readable.
3. **Dark mode from the phone's own setting** (no toggle): the ☰ as visible as the ⓘ.
4. **A signed-in test account with no link.** The card "Hi — I'm Alo. …"; "Enter invite code" opens "Link to Your Therapist"; the Journal saves an entry; ☰ has no private session, no Memory, no Share, and the theme item names the other theme.
5. **History off** (dashboard: Client Settings → Conversation history off; reload the client page; **a test account only**). ☰ shows "Memory settings" and "Delete my conversation history". Delete, read the confirm, confirm: "History cleared". Send a message, turn history back on, reload: the sidebar lists only the new conversation.
6. **Sign-out.** Send a message, then ☰ → Log Out: the conversation disappears at once ("Signing out…"), then the signed-out card. DevTools → Application → Local Storage: no `bp-webchat-*`, no `botpress-message-history`.
7. **The therapist's name** (F), signed in as zztest1, in the console: `await api('/rest/v1/profiles?id=eq.' + therapistLink.therapist_id + '&select=display_name')`. `[]` means the row is withheld from the client, and the fallback stays as ruled. `[{display_name: null}]` means the therapist has no name. A name means it is readable, and the fallback has another cause.
8. **`?invite=<code>`** in a signed-out tab: "Link to Your Therapist" with the code; Link → Sign In.
9. **Copy for your review:** the by-invitation line in About and Privacy; "Signing out…"; the delete confirm; and section 7, points 1 to 4.
