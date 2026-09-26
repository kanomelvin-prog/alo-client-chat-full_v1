# S8 client claims fixes report v1.0

Brief #4-client v1.0 (claims fixes, dead flows, hide-history enforcement; rulings D40, Sep 21). Branch `auto/s8-client-claims`, created from `main` at `c0771b4` before any file was touched. Session ran 2026-09-26, 09:05 to 10:00 MDT (Claude Code, Claude Opus 5.5, effort max). Nothing was pushed to `main`. `index.html` and `styles.css` are untouched, and so is `dev.css` (so `dev.css?v=16` stays). Commits: `c402da4` (`dev.html`, sections 2 to 4, tasks A to E), `cac811a` (task F), and this report. Line numbers are `dev.html` on this branch (4,981 lines) unless marked `c0771b4` (5,137 lines, the numbering the brief and the inventory use).

## 0. Session log

**Run settings.** The brief asks for Fable 5.1 at effort max. This session ran on **Claude Opus 5.5 (1M context)** at effort max. The model is fixed when the session is launched and cannot be changed from inside it, so this is recorded as a deviation rather than corrected. Claude Code, bypass permissions, unattended. No interruptions, no restarts, no questions asked.

**Read order followed:** `CLAUDE.md`; `docs/reports/S7c_identity_private_session_report_v1_0.md`; the Claims Inventory (section 2, every entry the brief names; section 3; section 4; and the client rows of the full table for the verbatim texts at `c0771b4`), read where it lives, outside every repo, and not copied anywhere; then `dev.html` in full (all 5,137 lines) before the first edit.

**No live contact.** No request reached the live Supabase API or Botpress Cloud. The harness answered every request locally, and every outside host was blocked at the browser's resolver. The public supabase-js 2.39.0 UMD and the Botpress webchat v3.3 bundles were fetched from their CDNs (anonymous GET) into the session scratchpad.

**Deviations and interpretations**, each one a place where the brief left a choice:

1. **Model**, above.
2. **Task A, "the existing wrong-email-or-password message".** There is no such text in `dev.html`. There are two failure lines: "Incorrect password." (inline, with a "Forgot password?" button), shown only when the sign-up probe said the account existed; and the toast "Authentication failed. Please try again.", shown for every other failure, including whenever the sign-up call itself errored. Without the probe the page cannot tell a wrong password from an unknown email, so "Incorrect password." would be false half the time. Every failed sign-in now shows the existing toast, which is true either way. If Kano wants "Wrong email or password." instead, it is one string.
3. **Class E, which lists change.** The rule is the same four things, with no "patterns", "themes" or "reflections" and nothing that implies real-time notice. Onboarding screen 2 (`c0771b4:1498`) and the sign-in modal's muted line (`c0771b4:1883`) lacked the safety note (the sign-in line also lacked what the client shares). Each gained it in its own short form; the phrase is "a safety note", because screen 2 already uses "a note" for something the client writes. The consent screen (`c0771b4:1596`) had all four, so only its alert verb changed. The Privacy modal's list (`c0771b4:4986`) is unchanged: its third item is the safety note (C-105).
4. **Section 3, the Memory-off row's no-link form.** The literal reduction of "Safety notes still" is "Alo still records that something happened — never your words", which on its own reads as a general record. It keeps the danger condition the other two rows carry: "If you seem to be in danger, Alo still records that something happened — never your words". All three no-link rows are therefore identical. Kano's eye.
5. **Section 3, what "linked" means.** `therapistLink` is set only past the consent gate (an active, consented link). Guests and signed-in accounts with no link get the no-link forms. The markup keeps the linked form as its default, and the helper rewrites it each time the banner, the About table or the recap is shown.
6. **C-044.** The words are the ruled text. The page's existing paragraph break between its two paragraphs is kept.
7. **S2** sits in the same list item as C-099, directly after it. The list already pairs an Alo-account claim with a platform caveat in one item (C-095).
8. **C-093.** The four new items are appended to the list in the brief's order.
9. **C-065** is now one constant string. "Your pinned conversations won't be affected." now shows even when there are none; before, it appeared only with a count.
10. **Task B's comment** is one line at the top of `showLoginModal()` (1861). The button sat inside a template literal, where a JS comment cannot go, and an HTML comment there would ship into the modal. It avoids the literal button text, so `grep "Forgot password"` returns 0.
11. **Task C, beyond the letter.** Two additions, both needed for the brief's "cannot open from anywhere":
    - When a load finds history off, the sidebar is also closed directly. A sidebar opened before the setting arrived could otherwise stay open with `toggleThreadSidebar()` inert.
    - The setting is applied in both directions on every connected-state load. `main` only ever un-hid the header button, never hid it again.
12. **Task F** is its own commit.
13. **`dev.css` not touched.** The removed markup leaves dead rules (`.guest-benefits-*`, `.memory-prompt-*`, one `body.keyboard-open #memoryPromptBar` selector). They are harmless, and removing them is not a fix the brief needs.
14. **Stale comments** were corrected where this change made them wrong: the focus-trap list, the list of entries into the connected state, and the fix H note.
15. **This repo is public.** This report describes what the page does and did. It says nothing about database configuration beyond what the page's own source shows.

**Checklist (brief sections 1, 5, 6):**
- Branch created from `main` at `c0771b4` before any file was touched.
- Only `dev.html` edited, plus this report and the `git rm` of task F.
- The stray file `git rm`-ed.
- `scripts/scan-invisible.py dev.html dev.css`: CLEAN, exit 0, before each of the three commits.
- Verification items 1 to 10 all pass (section 5).
- Report committed and pushed to `auto/s8-client-claims`; the push was verified with `git status` and `git log`.
- Not pushed to `main`; `index.html`, `styles.css` and `dev.css` unchanged.

## 1. Summary

| Part | What changed | Where | Evidence |
|---|---|---|---|
| Section 2 | Every ruled string at every location the inventory lists, markup and JS constant alike. Removed sentences are gone. | the 38 locations in the brief's table (37 changed; C-048 unchanged by ruling), listed in section 2 | static check: 116 checks, 0 failures (section 5); harness `copy_*`, `classd_*` |
| Section 3 | One helper, `_aloTherapistCopy(key)`, over one table, `ALO_THERAPIST_COPY`. The banner, the three safety rows and the "How Alo works" recap get the no-link form when `therapistLink` is null. | 3515-3551, 958-967, 1589, 3429 | `classd_linked`, `classd_unlinked`, `classd_guest` |
| A | The `signUp()` fallback and the "Account created!" toast are removed. The dormant guest card and memory prompt bar are removed with their functions. `?invite=` routing is unchanged. | 1860-1919, 4661 | `task_a_*` |
| B | Both "Forgot password?" buttons, the Reset Password modal and toast, the Set New Password modal and the `PASSWORD_RECOVERY` branch are removed. One dated comment. | 1861, 4858 | `task_b_no_reset`, `copy_login` |
| C | `allow_history === false` hides the header button and the menu item "Conversations", and makes `toggleThreadSidebar()` a no-op. Applied on every connected-state load. | 126, 2310, 2826-2850 | `task_c_*` (phone and desktop widths) |
| D | The homework fetch names its columns: `select=id,title,homework_type,goal,viewed_at` | 1106-1109 | `task_d_homework` |
| E | "Start new private conversation" appears only while private | 163, 3637-3648 | `task_e_menu` |
| F | `git rm "padding: 8px 12px;"` (103 KB; nothing references it) | repo root | `cac811a` |
| G | `scan-invisible.py`: CLEAN before every commit; the diff adds no invisible or smart-quote character | - | section 5 |

Harness (section 6): the branch passes 42/42 scenarios on the Botpress stand-in and 42/42 on the real v3.3 bundles, 263/263 checks each. It also passes the 22 regression scenarios at 0 ms latency, and 19/19 at 375 px, at 390 px and at 375 px in the dark theme. `main` passes the same 22 regression controls and fails all 20 scenarios that encode this brief, in both tiers. No page error or unexpected console error appears in any branch run.

## 2. Copy: before / after

Every string changed, at every location. "Before" is the verbatim text at `c0771b4` from the inventory; "After" is the ruled text as it now renders. A location marked "(JS)" is a string constant or literal in the script.

| ID | `c0771b4` | Before | After | Branch |
|---|---|---|---|---|
| C-008 | 214 | Your conversations are private — always. Your therapist never sees what you say to Alo. | Your conversations are private from your therapist — they never see what you say to Alo. | 214 |
| C-009 | 215 | If you're connected to a therapist through Alowen, they can see general patterns across your sessions, when you use Alo, and when you view or complete reflections they've assigned. They also see messages you send them, journal entries you choose to share, and, if Alo notices you might be in trouble, that something happened — never what you said. They aren't notified in real time — they review at their own pace, usually to prepare for your next session. | If you're connected to a therapist through Alowen, they can see when you use Alo and when you view or complete homework they've assigned. They also see messages you send them, journal entries you choose to share, and, if Alo notices you might be in trouble, that something happened — never what you said. They aren't notified in real time — they see it the next time they open their dashboard. | 215 |
| Class E (C-043) | 1498 (JS) | ... Beyond what you share, your therapist can see when you use Alo and when you view or complete homework they assign — never what you say to Alo. | ... Beyond what you share, your therapist can see when you use Alo, when you view or complete homework they assign, and a safety note if Alo thinks you may be in danger — never what you say to Alo. | 1476 |
| Class E (C-045) | 1596 (JS) | ... If Alo notices you might be in trouble, it'll point you to help and let your therapist know something happened, never what you said. | ... If Alo notices you might be in trouble, it'll point you to help and leave a note for your therapist that something happened, never what you said. | 1574 |
| Class E (C-053) | 1883 | Your conversations stay private. If you're connected to a therapist, they can see when you use Alo and when you view or complete homework they assign — never what you say. | Your conversations stay private. If you're connected to a therapist, they can see when you use Alo, when you view or complete homework they assign, what you choose to share with them, and a safety note if Alo thinks you may be in danger — never what you say. | 1864 |
| Class E (C-103) | 4986 | Your therapist sees when you use Alo, when you view or complete homework, messages you send them, and any journal entries you explicitly share | (unchanged: its list's third item is the safety note, C-105) | 4836 |
| C-013 | 223 | If you share something that sounds like a crisis, Alo will pause and share these resources with you directly. | If you share something that sounds like a crisis, Alo will share these resources with you directly. | 223 |
| C-014 | 228 | ... Deletion from the chat platform Alo runs on is coming and isn't in place yet. | ... Deletion from the chat platform Alo runs on isn't in place yet. | 228 |
| C-095 | 4970 | ... Deletion from the chat platform Alo runs on is coming and is not yet in place | ... Deletion from the chat platform Alo runs on isn't in place yet. | 4820 |
| C-020 | 245, 256 | Journal saves when you ask | Journal saves only with your OK | 248, 259 |
| C-021 (row 246) | 246 | Safety alerts to your therapist, never your words | A note for your therapist if you seem to be in danger — never your words (no-link form: section 3) | 249; 3530 (JS) |
| C-024 (row 257) | 257 | Safety alerts still | Safety notes still (no-link form: section 3) | 260; 3534 (JS) |
| C-025, C-024 (265-266) | 265, 266 | Nothing saved — no history, no memory, no journal · Safety alerts still | Nothing from the conversation goes into your history, memory or journal · Alo still records when you used it · If you seem to be in danger, a note for your therapist that something happened — never your words (no-link form: section 3) | 268, 269, 270; 3538 (JS) |
| C-030 | 317, 3698 (JS) | Private session — nothing here is saved or remembered. If you're in danger, Alo still sends your therapist a safety alert, never your words. | Private session — nothing here goes into your history or memory. If you're in danger, Alo still leaves a note for your therapist that something happened — never your words. (no-link form: section 3) | 322; 3525 (JS; `ALO_PRIVATE_BANNER_TEXT` became `ALO_THERAPIST_COPY.privateBanner`) |
| C-044 | 1503 (JS) | Alo isn't built for a crisis. If you're in danger or thinking about hurting yourself, call or text 988 or go to your nearest emergency room. If Alo notices you might be in trouble, it will tell you where to get help — and it will let your therapist know something happened. Not what you said. Just that you might need them. | Alo isn't built for a crisis. If you're in danger or thinking about hurting yourself, call or text 988 or go to your nearest emergency room. If Alo notices you might be in trouble, it will tell you where to get help — and it will leave a note for your therapist that something happened, which they see the next time they open their dashboard. Not what you said. Just that you might need them. | 1481 |
| C-047 | 1609 (JS) | Before your first conversation, you confirmed: "I understand what Alo is and isn't, and how sharing works." Then you tapped "Start talking to Alo." | Linked: unchanged. No link: When you link with a therapist, you'll confirm this before your first conversation. | 1589; 3543-3544 (JS) |
| C-049 | 1682 | Stay connected with your therapist between sessions. They can send you exercises, and you can message them anytime. | Stay connected with your therapist between sessions. They can send you exercises, and — if they turn messages on — you can message them. | 1662 |
| C-051 | 1881 | Sign In or Create Account | Sign In | 1862 |
| C-052 | 1882 | Create an account to save your conversations and let Alo remember what you've discussed. | Sign in to save your conversations and let Alo remember what you've discussed. New accounts are set up by invitation. | 1863 |
| C-054 | 1965 (JS) | Account created! Check your email to confirm. | (removed with the sign-up fallback, task A) | - |
| (not inventoried) | 1954 (JS) | Incorrect password. [Forgot password?] | (removed with the sign-up fallback, tasks A and B) | - |
| C-031 | 328 | Create a free account and Alo can remember your conversations, pick up where you left off, and connect with your therapist if you have one. (dormant) | (markup removed, task A) | - |
| C-034 | 379 | Want Alo to remember your conversations? (dormant) | (markup removed, task A) | - |
| C-055 | 2002 (JS) | Enter your email and we'll send you a link to reset your password. | (modal removed, task B) | - |
| C-056 | 2032 (JS) | Reset link sent — check your email | (removed, task B) | - |
| C-057 | 2050 (JS) | Choose a new password for your Alowen account. | (modal removed, task B) | - |
| (buttons) | 1896, 1954 | Forgot password? | (removed, task B) | - |
| C-058 | 2135 | {Therapist name} will see this message in their dashboard. They'll respond when they can. | {Therapist name} will see this message in their dashboard. They'll pick it up when they can — replies don't come through Alo. | 1937 |
| C-060 | 3070, 3247, 3278 (JS) | Save this conversation | Pin this conversation | 2893, 3070, 3101 |
| C-063 | 3415 (JS) | Conversation deleted | Deleted from your account | 3238 |
| C-064 | 3436 (JS) | Conversation saved | Conversation pinned | 3259 |
| C-065 | 3452-3458 (JS) | This will delete {N} unpinned conversation(s) from your Alo account. Your {M} saved conversation(s) won't be affected. Alo will still remember themes from recent sessions. This can't be undone. | This will delete all your unpinned conversations from your Alo account. Your pinned conversations won't be affected. Alo will still remember themes from recent sessions. This can't be undone. | 3276 |
| C-070 | 3693 (JS) | Memory is off, but your conversations are still saved to your history. | Private sessions are available while memory is on. Right now memory is off, and your conversations are still saved to your history. | 3511 |
| C-091 | 4944 | You are responsible for deciding what to share with your therapist | You decide what to share with your therapist. Alo also leaves them a note if it thinks you may be in danger — never what you said. | 4790 |
| C-093 | 4958-4965 | Homework completion status (and a five-item list) | When you view and complete homework; added: When you use Alo (activity records) · Brief memory summaries when memory is on · Safety notes — that something happened, never your words · Your display name and settings | 4808; 4811-4814 |
| C-099 | 4974 | Conversations are not used for training, analytics, or advertising | Alowen doesn't use your conversations for advertising, and we don't train AI models on them. | 4824 |
| S2 | after 4974 | (absent) | Alo runs on a chat platform that keeps its own copy of conversations, and an AI model provider that processes your messages so Alo can reply. | 4824 (same item) |
| C-105 | 4988 | If Alo detects a safety concern, your therapist is alerted that something happened — never what you said. | If Alo detects a safety concern, it leaves a note for your therapist that something happened — they see it the next time they open their dashboard — never what you said. | 4838 |
| C-106 | 4989 | We don't sell or share your data with third parties | We never sell your data. Nothing is shared beyond what it takes to run Alo. | 4839 |
| C-107 | 4994 | All stored data is encrypted at rest (AES-256) and in transit (TLS) | Your data travels over encrypted connections (TLS), and our database encrypts stored data at rest. | 4844 |
| C-108 | 4995 | Chat data is encrypted at rest and in transit by our chat provider | (removed) | - |
| S3 | after 277 | (absent) | If you write about being in danger, Alo shows you where to get help. Journal entries don't create a note for your therapist. | 282 |
| C-048 | 1624 | (no change, ruling-pattern constant) | unchanged | 1604 |

**Not changed by ruling, byte-identical to `main`** (checked by script, section 5): C-010 (216), C-011 (217), C-016 (230), C-026 (280), C-062 (3215, 3217), C-067 (3453), C-068 (3468), C-069, C-078, C-079, C-082 and C-100.

## 3. Section 3: "your therapist" only for an account that has one

`ALO_THERAPIST_COPY` (3522-3546) holds five entries, each with a linked and a no-link string. `_aloTherapistCopy(key)` (3548) returns one of them from `therapistLink`. It has five uses and no inline ternaries:

| Where | How it is applied | Linked | No link |
|---|---|---|---|
| Private banner | `updateMemoryUI()` sets the text on every call (3429) | the C-030 ruled text | Private session — nothing here goes into your history or memory. If you're in danger, Alo still records that something happened — never your words. |
| About > What gets saved, Normal (row 246) | `showAboutModal()` rewrites each `[data-alo-therapist-copy]` item on open (958-967) | A note for your therapist if you seem to be in danger — never your words | If you seem to be in danger, Alo still records that something happened — never your words |
| ... Memory off (row 257) | same | Safety notes still | same as above (deviation 4) |
| ... Private session (row 266) | same | If you seem to be in danger, a note for your therapist that something happened — never your words | same as above |
| "How Alo works", screen 4 (C-047) | `_aloRenderOnboardingScreen()`, read-only mode (1589) | the recap, unchanged | When you link with a therapist, you'll confirm this before your first conversation. |

The markup at 249, 260, 270 and 322 keeps the linked form. The banner is hidden (`display: none`) until `updateMemoryUI()` has written its text, and the table rows are rewritten before the About modal is shown, so no one sees the default out of turn. `classd_unlinked` shows the no-link forms on all five surfaces, and that no table row names a therapist. `classd_guest` shows the no-link rows to a guest. `classd_linked` shows the linked forms.

## 4. Code tasks: before and after

### A: dead sign-up flow

| | Before (`c0771b4`) | After |
|---|---|---|
| Failed sign-in | On "Invalid login credentials", `supabase.auth.signUp({ email, password, options: { data: { role: 'individual', display_name, invite_code } } })` (1929-1940). Empty identities meant "Incorrect password." plus a "Forgot password?" button. A sign-up error gave "Authentication failed. Please try again.". No session gave "Account created! Check your email to confirm." (1965) | `signInWithPassword` only (1903). Any error gives "Authentication failed. Please try again." and the modal stays open |
| Dormant markup | `#guestBenefitsCard` (320-335) with `showGuestBenefitsCard()` (a no-op) and `dismissGuestBenefits()`; `#memoryPromptBar` (377-381) with `checkGuestMemoryPrompt()` (it only counted guest turns into `guestTurnCount`, which nothing read) and `hideMemoryPrompt()` | All removed. The guest branch of the message handler (4661) still returns before any write |
| `?invite=` as a guest | connect modal with the code; "Link" (or "Sign in") opens the sign-in modal; the sign-in then claims through `redeem_invite_code` (Brief 3b) | unchanged (`task_a_invite_guest`, both tiers) |

The user_metadata claim path in `loadConnectedState()` stays. Accounts made before this change can still carry an `invite_code` there. Nothing on the page sets it any more; the page still clears it after a claim attempt.

### B: dead password-reset flow

| | Before (`c0771b4`) | After |
|---|---|---|
| "Forgot password?" | Under the password field (1896), and inside the "Incorrect password." line (1954) | gone; one comment at 1861: `2026-09-26 (Brief 4 B): no password-reset link here -- client password reset returns with the Auth-side fix (token_hash / verifyOtp), Gate B.` |
| Reset Password modal (`handleForgotPassword`, `resetPasswordForEmail`, the toast) | 1993-2043 | removed |
| Set New Password modal (`showSetNewPasswordModal`, `toggleNewPasswordVisibility`) | 2045-2117 | removed |
| `onAuthStateChange` | a `PASSWORD_RECOVERY` branch first (5010-5014) | starts at `SIGNED_IN` (4858) |

With this change and task A, the page sends no auth email of any kind.

### C: hide-history is a control

| | Before (`c0771b4`) | After |
|---|---|---|
| Header button `#threadsBtn` | un-hidden when `allow_history !== false` (2507), and never hidden again, even when a later load found it off. It is also hidden by the page's CSS on phones (<= 640 px) | `_aloApplyHistorySetting()` (2836) toggles it both ways on every connected-state load (2310) |
| Menu item "Conversations" (126) | always shown. On phones it is the only way into history, because the header button is hidden there | gets `id="moreConversationsBtn"`; `display: none` while history is off (the menu's keyboard navigation already skips hidden items) |
| `toggleThreadSidebar()` | opened for anyone | `if (_aloHistoryOff()) return;` (2849), so the header button, the menu item, the sidebar's own X (344; `c0771b4:355`), its "Memory settings" link (358; `c0771b4:369`) and the backdrop (364) are all inert |
| A sidebar already open when history turns off | stayed open | closed directly (2842-2845) |

`chatSettings` is `{}` for guests and for accounts with no link, so for them nothing changes (`task_c_unlinked`). Two consequences need a ruling (section 7, points 1 and 2).

### D: homework fetch names its columns

| | Before (`c0771b4`) | After |
|---|---|---|
| Request | `homework_cards?client_id=eq.{id}&is_active=eq.true&order=created_at.desc` (1131). No `select=`, so every column of the row is asked for | `...&is_active=eq.true&select=id,title,homework_type,goal,viewed_at&order=created_at.desc` (1109) |

These are the columns the page reads: `id`, `title`, `homework_type`, `goal` and `viewed_at` for the cards and the viewed-at write, and `title`, `homework_type` and `goal` for the bot's `homeworkActive`. Filtering and ordering on `is_active` and `created_at` need no column in the list. `clinical_rationale` appears nowhere in `dev.html` (grep: 0). `task_d_homework` checks the rest:
- the request carries the list;
- the page's homework objects hold only those five fields;
- both cards render title, type and goal;
- `viewed_at` is written for the unviewed card only;
- "Mark complete" writes `is_active: false` and `completed_at`;
- the bot still gets each card's title, type and goal.

### E: one private menu item unless private

| | Before (`c0771b4`) | After |
|---|---|---|
| `#moreNewPrivateBtn` | always visible, so there were two items doing the same thing when not private | `style="display: none;"` in the markup (163); `updatePrivateChatBtn()` shows it only while `isPrivateSession` (3647). A page load is never private (Brief 3c C), so hidden is the right start |

### F: stray file

`padding: 8px 12px;` at the repo root was a 103 KB copy of an old `dev.html` from the rename in `b459461`. It was removed with `git rm` (`cac811a`). Nothing references it: a search of the repo for its name in an `href`, `src`, `url()`, import or fetch found nothing. The only other mention is the S7c report's note, which is not a reference.

## 5. Verification (brief section 5)

| # | Item | How | Result |
|---|---|---|---|
| 1 | Every ruled string at every listed location; none of the old strings remain | Script over the committed `dev.html`: the exact source form of each ruled string (JS escapes included) with its expected count and the lines found (section 2's last column); every old verbatim text from the inventory counted; the frozen entries compared with `main` | 116 checks, 0 failures: 39 ruled strings at their expected counts and lines; 40 old texts at 0; 14 frozen strings byte-identical to `main`; 8 section 3 checks; 12 dead-flow and homework greps; the alert-verb grep; `node --check` twice. Rendered text checked as well: `copy_about` (23 checks), `copy_privacy_terms` (24), `copy_gate_screens`, `copy_login`, `copy_connect`, `copy_message`, `copy_threads`, `copy_memory_off_hint` |
| 2 | `grep -ci "sends your therapist\|is alerted\|let your therapist know"` = 0 | the same grep, whole file (comments included) | 0 |
| 3 | `therapistLink = null` gives the no-link banner, three rows and screen 4; a link gives the linked ones | `classd_unlinked`, `classd_guest`, `classd_linked` | PASS (both tiers, and at 375 and 390 px) |
| 4 | No `signUp(` call; a wrong password shows the existing failure line; `?invite=CODE` as a guest still opens the sign-in modal | grep `signUp(`: 0. `task_a_wrong_password`, `task_a_unknown_email`: the toast, the modal still open, no request to `/auth/v1/signup`. `task_a_invite_guest`: the connect modal opens with the code; "Link" opens the sign-in modal; the sign-in claims through `redeem_invite_code`; the new link then waits at the consent gate | PASS. `main` requests `/auth/v1/signup` on every failed sign-in |
| 5 | No "Forgot password?", no reset modal, no `PASSWORD_RECOVERY`; sign-in unaffected | grep: 0 each. `task_b_no_reset`: none of the three functions exists; no button before or after a failed sign-in; no reset request. `task_a_signin_ok`: sign-in, then connected state and a verified identity | PASS |
| 6 | `allow_history: false`: header button, menu item and `toggleThreadSidebar()` inert; `true`: all work | `task_c_history_off` (500 px, phone layout) and `task_c_history_off_desktop` (1280 px): hidden button and item; their handlers, `toggleThreadSidebar()`, the sidebar's X, its "Memory settings" link and the backdrop leave it closed; no conversation list is read. `task_c_history_on` and `task_c_history_on_desktop`: each opens and closes it. `task_c_history_live`: off then on again within one page | PASS. `main` opens the sidebar from the menu item and reads the list |
| 7 | The homework URL has `select=` with an explicit list and not `clinical_rationale`; homework renders; viewed/completed writes work | `task_d_homework` (section 4 D) | PASS |
| 8 | One private item when not private, two when private | `task_e_menu`: one, then two (End / Start new), then one after ending | PASS. `main` shows two when not private |
| 9 | Both inline scripts pass `node --check`; the rebuilt S7c harness loads the page with no console error as guest, linked and unlinked; the S7c private start and end paths still pass | `node --check`: exit 0 on both (348 and 204,814 characters). Section 6 | PASS: `load_guest`, `load_linked`, `load_unlinked` with no page error and no console error, on the stand-in and the real v3.3 bundles; 12 private-path scenarios pass on both |
| 10 | `scan-invisible.py` CLEAN; zero U+200B/U+200C/U+200D/U+FEFF/U+2060 in the diff | the script; a count over the diff's 142 added lines | CLEAN, exit 0; 0 of each (and 0 NBSP and 0 smart quotes) |

## 6. Harness

**Method.** This is the S7c harness, rebuilt this session as that report describes (harnesses are not kept between sessions): headless Google Chrome 153, a local `python3 -m http.server`, a fresh profile for every run, and every outside host blocked at the resolver. The harness copy of `dev.html` keeps the page's own CSP and replaces only its two CDN script tags. supabase-js is the real 2.39.0 UMD, served locally. `window.fetch` is answered by a local GoTrue/PostgREST emulation that logs every request, with 60 ms of latency per request by default. A driver works the real UI with hit-tested taps and writes its checks into the page.

Botpress, two ways:
- **Stand-in** v3.3, modelled on the S7c findings: pre-init stubs, `webchat:initialized` then `webchat:ready`, `updateUser`/`getUser` against user data kept across reloads, restarts, the composer DOM in a same-origin iframe, and a bot that records the user data it sees on each turn.
- **The real v3.3 `inject.js` and `webchat.js`**, unmodified apart from their three script URLs, with only the Chat API answered locally. That covers `/users`, `/users/me`, `/conversations`, the event stream, `/messages` and `/events`, through a fetch shim prepended to the local `webchat.js` inside its iframe.

Each scenario ran on `main` and on the branch.

**All scenarios, 60 ms latency.** The first 22 are regression controls, and the remaining 20 encode this brief.

| Scenario | What it does | `main` | Branch | `main`, real SDK | Branch, real SDK |
|---|---|---|---|---|---|
| `load_guest` | guest load; a message writes nothing | PASS | PASS | PASS | PASS |
| `load_linked` | linked load; startup identity verified; composer released; bridge sent | PASS | PASS | PASS | PASS |
| `load_unlinked` | signed in with no link; connect prompt | PASS | PASS | PASS | PASS |
| `private_start_menu` | menu: `'true'` sent and read back, then the restart; nothing written; the bot sees `'true'` | PASS | PASS | PASS | PASS |
| `private_start_popover` | the same from the eye icon (1280 px) | PASS | PASS | PASS | PASS |
| `private_end_x` | the banner X (44x44): `'false'`, then the restart; toast; the next message saved | PASS | PASS | PASS | PASS |
| `private_end_menu` | end from the menu | PASS | PASS | PASS | PASS |
| `new_private_while_private` | "Start new private conversation" while private | PASS | PASS | PASS | PASS |
| `new_conversation_while_private` | logo: "Start fresh" ends the private session (one path) | PASS | PASS | PASS | PASS |
| `private_start_fails` | `'true'` cannot be sent: the constant line; no banner, no restart | PASS | PASS | PASS | PASS |
| `private_end_fails` | `'false'` cannot be sent: still private, banner up | PASS | PASS | PASS | PASS |
| `memory_off_private` | memory off: a hint, no private session | PASS | PASS | PASS | PASS |
| `private_end_late_reply` | X tapped while a private reply is on its way: nothing written | PASS | PASS | PASS | PASS |
| `stuck_private_no_marker` | Botpress user left holding `'true'`, no marker: startup and the first turn say `'false'` | PASS | PASS | PASS | PASS |
| `private_reload` | reload mid-private: not private, marker gone, a fresh Botpress user | PASS | PASS | PASS | PASS |
| `gate_consent` | unconsented link: gate, consent, chat | PASS | PASS | PASS | PASS |
| `logout` | Log Out, then a guest page | PASS | PASS | PASS | PASS |
| `task_a_signin_ok` | a correct sign-in: connected, no sign-up request | PASS | PASS | PASS | PASS |
| `task_a_invite_guest` | `?invite=` as a guest: connect modal, sign-in modal, claim, gate | PASS | PASS | PASS | PASS |
| `task_c_history_on` | history on (phone layout): the menu item opens the sidebar | PASS | PASS | PASS | PASS |
| `task_c_history_on_desktop` | history on (1280 px): the header button too | PASS | PASS | PASS | PASS |
| `task_c_unlinked` | no link: history available | PASS | PASS | PASS | PASS |
| `classd_linked` | section 3, linked | FAIL: old rows, old banner | PASS | FAIL | PASS |
| `classd_unlinked` | section 3, no link | FAIL: "your therapist" on all five | PASS | FAIL | PASS |
| `classd_guest` | section 3, guest | FAIL | PASS | FAIL | PASS |
| `copy_about` | every About string, the old ones gone | FAIL (21 of 23) | PASS | FAIL | PASS |
| `copy_privacy_terms` | Privacy and Terms modals | FAIL (22 of 24) | PASS | FAIL | PASS |
| `copy_gate_screens` | onboarding screens 2 to 4 | FAIL: "let your therapist know" | PASS | FAIL | PASS |
| `copy_login` | title, body, muted line, no reset button | FAIL | PASS | FAIL | PASS |
| `copy_connect` | C-049 | FAIL | PASS | FAIL | PASS |
| `copy_message` | C-058 | FAIL | PASS | FAIL | PASS |
| `copy_threads` | C-060 (x3), C-063, C-064, C-065 | FAIL | PASS | FAIL | PASS |
| `copy_memory_off_hint` | C-070 | FAIL | PASS | FAIL | PASS |
| `task_a_wrong_password` | failure line; no sign-up request | FAIL: requests `/auth/v1/signup` | PASS | FAIL | PASS |
| `task_a_unknown_email` | the same for an unknown email | FAIL: requests `/auth/v1/signup` | PASS | FAIL | PASS |
| `task_a_dormant` | card, bar and their functions gone | FAIL | PASS | FAIL | PASS |
| `task_b_no_reset` | no reset code or buttons | FAIL | PASS | FAIL | PASS |
| `task_c_history_off` | history off (phone layout) | FAIL: menu item opens it | PASS | FAIL | PASS |
| `task_c_history_off_desktop` | history off (1280 px) | FAIL | PASS | FAIL | PASS |
| `task_c_history_live` | off, then on, in one page | FAIL | PASS | FAIL | PASS |
| `task_d_homework` | column list; rendering; viewed/completed writes | FAIL: no column list | PASS | FAIL | PASS |
| `task_e_menu` | private menu items: 1 / 2 / 1 | FAIL: 2 / 2 / 2 | PASS | FAIL | PASS |

Totals: the branch passes 42/42 in each tier (263/263 checks each); `main` passes 22/42 in each tier, and the 22 are the controls. At 0 ms latency the 22 regression scenarios pass on both. The only console errors in any run are the expected identity-failure lines inside `private_start_fails` and `private_end_fails`. No run needed a retry.

**Phone widths** (`CLAUDE.md`: 375 and 390). The app ran in a same-origin frame at 375x812 and at 390x844, because desktop Chrome will not open a window narrower than 500 px. 19 scenarios ran:
- all section 3 and copy surfaces;
- `task_c_history_off`, `task_d_homework`, `task_e_menu` and `private_end_x`;
- seven layout states: the banner linked and with no link, the About table linked and with no link, the sign-in modal, the Privacy modal, and the menu while private.

Result: 19/19 at 375, 19/19 at 390, and 19/19 at 375 in the dark theme. Nothing scrolls sideways. The banner is 76 px tall at both widths, wrapping to four lines, with the X at 44x44 on the right. The About table is 310 px wide at 375 and 325 px at 390, with no overflow. The screenshots were checked by eye in both themes.

**Harness artefacts**, fixed in the harness and not in the page:
- `--dump-dom` renders no frames, so bottom sheets stay on their first animation frame; motion is off in the harness copy.
- The real `inject.js` posts its own render and init timings to the Botpress host from the page. With outside hosts blocked, that logged "Error sending perf metrics" on both `main` and the branch, so the harness answers it locally. On the live site the page's CSP allows that host.
- The header's history and eye icons are hidden by the page's CSS at 640 px and below. Checks that need them run at 1280 px.

## 7. Declined, and observations for Kano

Declined (out of scope by the brief): the parked branch; the consent flow; the bot; About/Privacy restructuring; S3/S4 UX polish; `index.html`. `dev.css` is untouched (deviation 13).

**Needs a ruling. Task C creates two gaps:**

1. **With history off, a client can no longer delete their conversations.** The sidebar is the only place with Delete and "Clear unpinned conversations". So for a client whose therapist has turned history off, three sentences are no longer true:
   - About, How memory works (228): "you can delete any conversation from your Alo account at any time";
   - the Privacy modal (4820): "...at any time from the sidebar";
   - the "What gets saved" Normal row (246): "(you can delete it)".

   Conversations are still saved (task C changes visibility, not persistence). The ruled wording for 228 and 4820 was applied exactly, and nothing else in those sentences was changed. Kano needs to choose one of three things:
   - a clause such as "unless your therapist has turned conversation history off";
   - a delete path that survives the setting;
   - accepting it.
2. **On phones, "Clear all memories" becomes unreachable with history off.** At 640 px and below the page's CSS hides the header eye icon. The sidebar's "Memory settings" link (358) was therefore the only way to the memory popover, and its "Clear all memories", on a phone. The menu keeps the memory switch and "Start private session". No sentence says clearing is always available on this surface (the popover's own tip, C-067, is frozen and shows only when the popover opens). This is a lost control, not a false claim.

**Found on the way, not changed:**

3. **C-003**, the menu's memory note: "You can start a private session anytime from the eye icon." On phones the eye icon is hidden by CSS. The inventory rated it TRUE from the markup alone. It is not in the ruled list.
4. **"Your therapist" on surfaces section 3 does not cover.** "How Alo works" screens 2 and 3 (1476, 1481; screen 3 now says "it will leave a note for your therapist") are shown to accounts with no link. So are the Terms item (C-091), the Privacy items (C-093, C-105) and S3. Section 3 names five places, and those five were done.
5. **S3 and journal edits.** The journal safety check (`checkJournalSafety`, a keyword list, local, sending nothing) runs when a new entry is saved, not when an entry is edited. "If you write about being in danger, Alo shows you where to get help" is true for new entries that match the list. Adding the check to the edit path is one line.
6. **"Saved" vocabulary next to "Pin".** The sidebar's pinned section is still headed "Saved" (2932), and the delete confirm (C-062, frozen) still says "you can save it instead".
7. **The sign-in modal's "Your conversations stay private."** It is unscoped, as C-008 was before its fix. It is not in the ruled list.
8. **A new client arriving by `?invite=` with no account has no way to make one on this page.** As before, the removed sign-up call would have been refused. The sign-in modal now says "New accounts are set up by invitation."
9. **The closed sidebar stays in the tab order** (it is moved off-screen, not made inert), which is a pre-existing accessibility issue. With history off, a keyboard user who reaches "Clear unpinned conversations" gets "No unpinned conversations to clear", because the list was never loaded. No history is shown. Setting `inert` on the closed sidebar is a small fix if wanted.
10. **C-065's pinned sentence** now shows even to a client with nothing pinned (deviation 9).

## 8. Kano's check on alowen.ai/dev.html (after merge)

1. **Sign in with a wrong password.** Expect "Authentication failed. Please try again.", the modal still open, and no "Forgot password?" anywhere. In DevTools, Network: no request to `/auth/v1/signup`.
2. **`?invite=<code>` in a signed-out tab.** Expect the "Link to Your Therapist" modal with the code filled in; "Link" opens "Sign In"; signing in with an existing account claims the code.
3. **A linked account: About > What gets saved** shows "A note for your therapist ..." / "Safety notes still" / the three private items. Start a private session: the banner reads "... Alo still leaves a note for your therapist that something happened — never your words." Menu: two private items while private, one otherwise.
4. **An account with no link: About > What gets saved** shows "If you seem to be in danger, Alo still records that something happened — never your words" in all three rows. "How Alo works", screen 4: "When you link with a therapist, you'll confirm this before your first conversation." A private session's banner ends "... Alo still records that something happened — never your words."
5. **History off** (dashboard: Client Settings > Conversation history off; then reload the client page). On a phone: no "Conversations" in the menu, and nothing opens the sidebar. Turn it back on and reload: it is back. Please also rule on section 7, points 1 and 2.
6. **Homework** for a client with an active card. In DevTools, Network, the `homework_cards` request carries `select=id,title,homework_type,goal,viewed_at`. The card shows, and "Mark complete" works.
7. **Privacy Policy and Terms**, read as a reviewer would, on a phone.
