# S11 client follow-ups report v1.0

Brief #7-client v1.0 (therapist name, three copy lines, delete-current-conversation bug, dark-theme contrast, the delete-history confirm; ledger D41 item 2). Branch `auto/s11-client-followups`, created from `main` at `a10ad6f` before any file was touched. Session ran 2026-10-02, 09:21 to 10:20 MDT (Claude Code, Claude Opus 5.5 (1M context), effort max). Nothing was pushed to `main`. `index.html` and `styles.css` are untouched. The change is in `dev.html` and `dev.css` (so `dev.css?v=17` became `?v=18`), plus this report. Code commit: `6320516`. Line numbers are `dev.html` on this branch (5,500 lines) unless marked `main:` (5,261 lines).

## 0. Session log

**Run settings** as the brief asks: Opus 5.5, effort max, Claude Code, bypass permissions, unattended. No interruptions, no questions, no restarts.

**Read order followed:** `CLAUDE.md`; `docs/reports/S9_client_fixes_report_v1_0.md`; `dev.html` (all 5,261 lines on `main`) and `dev.css` (all 3,975 lines) in full before the first edit. Also read, to rebuild their scenarios: the S8 and S7c reports. Read-only, outside this repo: the `my_therapist_name()` migration in `alo-supabase` (for the return type and grants: `returns text`, NULL for no active link or more than one, EXECUTE for `authenticated` only) and the ledger's record that a client's conversation delete cascades its messages and sets its summaries' link to null. Before touching anything that calls the webchat: the Botpress v3.3 bundles again (`webchat.js` connect routine, event names, composer DOM).

**No live contact.** No request reached the live Supabase API or Botpress Cloud. The harness answered every request locally and blocked every outside host at the browser's resolver. Fetched by anonymous GET: supabase-js 2.39.0 UMD and the Botpress v3.3 bundles (`inject.js` sha256 `bb1b4365c43c…`, `webchat.js` `ff66947745df…`, the same files S9 read).

**Deviations and interpretations**, each one a place where the brief left a choice:

1. **A, the old name read is gone.** The page read the therapist's `profiles` row (`main:2449`), which the client role cannot read (S9 F; the migration's own header says so), so the read always came back empty, and it was awaited in front of the identity handshake. The RPC replaces it rather than sitting beside it. How the link is read is unchanged.
2. **A, "after the link is established"** is past the consent gate: an unconsented link holds the page at the consent screens and makes no call (`s11_name_after_consent`).
3. **A, "anywhere else the page falls back to 'Your therapist'".** The page keeps the name in `connectedTherapistName`, which `main` set to "Your therapist" for every linked client. So the name also reaches the homework cards' "From …", the homework tip, the message modal ("Message …", "… will see this message"), and the Journal's share confirm and "Shared with …" badge. Things already on screen when the name arrives (the pill, the homework cards, a homework tip still showing) are updated in place. Things built later read the variable. No Journal code changed.
4. **A, a race the harness found.** My first version picked the name before two awaited reads and drew the pill after them, so an answer landing in between was overwritten by the fallback (`s11_name_ok` failed). The name is now read at the `showConnectedUI()` call itself, with no `await` before it (2535).
5. **A, unchanged:** the pill's old rule that a client whose name equals the therapist's sees "· connected" instead of "· with …".
6. **B, About: the example wording was not used.** The brief's example is "If you're connected with a therapist, you stay in control of what they see: …", with the list kept as it is. None of the list's three items changes what the therapist sees. They never see conversations or memory, and a private session still records that Alo was used. So "of what they see" would make the sentence untrue. I used the brief's other instruction, "the same sentence conditioned on a therapist link": "If you're connected with a therapist, you stay in control: turn memory off, …". **Kano's eye** (section 7, point 1).
7. **C, what "the current one" is.** It is the history row of the conversation on screen. That row is either the one the page is writing to or, for a conversation the page resumed and has not written to yet on this load, the row this browser mapped it to. The page learns which Botpress conversation is on screen from two SDK events: `message`, and `conversation`, which the SDK emits for a new conversation but not a resumed one. It keeps that in `localStorage` (`alo_onscreen_conv`) so a resumed load knows it before its first message. The key is removed at sign-out with the other per-account keys. On the first load after this ships there is no note yet: deleting the resumed conversation then starts no new conversation, but its mapping is forgotten, so nothing is lost and its next messages go to a new row (`s11_delete_current_resumed_nokey`).
8. **C, "identity re-verified".** An unchanged identity object is answered from the page's cache ("already verified") with no request. The delete's send passes a new option, `reverify`, so it is a real send and read-back, as at sign-in and in the private on/off transitions (2623, 2672).
9. **C, beyond the letter: the box reopens on a connected conversation.** On the real v3.3 bundles, a message sent in the first few tens of milliseconds after the restart reached Botpress before the new conversation's stream was open. The page therefore never saw it, and it was not saved (only the reply was). That breaks exactly the brief's check ("both must land in a new conversation row") for a fast "ok" on a slow connection. The box now reopens once the SDK's `conversation` event names the new conversation, which the SDK emits once its stream is open. The wait is capped at 3 s, then the box reopens anyway (3137-3142, 3156-3165). Sign-in and private on/off have the same gap (section 7, point 3).
10. **C, a late reply** to the deleted conversation (one already on its way at the delete) is written nowhere: not to the deleted row, not into a new row, not into the local backup queues (`s11_delete_late_reply`). The private-end transition does the same for a private reply.
11. **C, Clear unpinned reads the on-screen row back.** The server's own filter (`pinned=eq.false`) decides which rows go, so after the delete the page asks whether the on-screen row still exists. If that read fails, the conversation counts as gone unless the page knows it is pinned. A needless new conversation loses nothing; a missed one loses what is said next (`s11_clear_readback_fails`, `…_pinned`).
12. **C, "Delete my conversation history"** now forgets every mapping and, if the conversation on screen had a row, starts a new conversation. Before, that conversation carried on into a new row. With no row on screen (a private session, or nothing said yet) it starts nothing.
13. **D, new tokens.** `--btn-primary-bg`, `--btn-primary-hover`, `--btn-primary-text` in all three theme blocks. In the light theme they point at `--primary` and `--primary-hover`, so nothing there changes. In the dark blocks they hold the light theme's brand teals, `#3A7C86` and `#2D6B74`. `--primary` itself is unchanged, because the dark theme's text and accents use it and its contrast as text is 4.9:1 to 5.5:1.
14. **D, which buttons.** All `.btn-primary` buttons (dangerous confirms included: `.btn-danger` has no style of its own), the sidebar's "New conversation" and the install banner's "Install". **Also the Journal's two filled states**: its share toggle when shared, and the hover of "Bring this to Alo". The brief puts the Journal out of scope, but D says every primary button, and these render as one (white on `--primary`). It is CSS colour only: no Journal behaviour or copy changed, and two rules revert it.
15. **D, also measured:** the hover fill, at 2.54:1 on `main` in the dark themes. Disabled buttons (half opacity) are exempt under WCAG and were left as they are.
16. **`dev.css` changed**, so the cache buster moved to `?v=18` (63).
17. **This repo is public.** The report describes what the page does and did, and what the published SDK bundles show. About the database it says only what the page's source shows, what the one function the brief names returns, and that a conversation delete takes the conversation's messages with it.

**Checklist (brief sections 2-4):**
- Branch created from `main` at `a10ad6f` before any file was touched.
- Only `dev.html` and `dev.css` edited, plus this report.
- `scripts/scan-invisible.py dev.html dev.css`: CLEAN, exit 0, before each commit.
- Verification items 1 to 6 all pass (section 5).
- Report committed and pushed to `auto/s11-client-followups`; the push verified with `git status` and `git log`.
- Not pushed to `main`; `index.html` and `styles.css` unchanged.

## 1. Summary

| Task | What changed | Where | Harness |
|---|---|---|---|
| A | One `supabase.rpc('my_therapist_name')` per page load, on the linked path, fired beside the handshake and never awaited by it. The name replaces "Your therapist" in the pill, the homework cards and tip, the message modal and the Journal's share lines; the fallback stays for null or an error. The dead therapist-profile read is gone. | 1007-1057, 2518, 2535, 1295, 1355 | `s11_name_*` (10), `s11_handshake` |
| B | The three sentences, at their one location each | 2072, 232, 5335 | `s11_copy`, `s11_copy_linked`, static counts |
| C | After any delete, mappings to the deleted rows are forgotten. If the conversation on screen was deleted: stop writing to its row, hold the box, re-send and read back the identity, restart once the webchat is connected, and reopen the box on the connected new conversation. The same for Clear unpinned (on-screen row read back) and Delete my conversation history. | 3023-3165, 3670, 3738, 3787, 4217-4221, 5153-5180 | `s11_delete_*`, `s11_clear_*` (14) |
| D | Primary-button tokens; dark fill = brand teal | `dev.css` 34-38, 107-113, 169-172, 617-620, 1611-1613, 1648-1650, 1936-1940, 3534-3555, 3585-3592, 3943-3945, 3954 | `s11_contrast_out`, `s11_contrast_in` x 3 themes; screenshot pixels |
| E | The confirm adds "Memory summaries are cleared separately, under Memory settings." | 3754 | `s11_delete_all_confirm` |
| F | Scan CLEAN before each commit; nothing invisible in the diff | - | section 5 |

Harness (section 6): the branch passes all 344 runs (3,604 checks) of the final pass, with no page error and no retry. That is 36/36 Brief 7 scenarios in each tier, 180/180 regression runs (73 S7c/S8/S9 scenarios, both tiers), 72/72 at phone widths and 20/20 handshake runs. `main` passes the same 180 regression runs and 20 handshake runs, and 8 of the 36 Brief 7 scenarios in each tier; the 8 are controls.

## 2. Task by task

### A - the therapist's name

| | Before (`main`) | After |
|---|---|---|
| Source of the name | `GET /rest/v1/profiles?id=eq.<therapist_id>&select=display_name`, awaited (`main:2449`). The client role cannot read that row, so it returned `[]`. | `supabase.rpc('my_therapist_name')` (1023): the display name of the therapist on the caller's single active link, or null |
| Pill | always "Hi {name} · with Your therapist" | "Hi {name} · with {therapist}". "with Your therapist" for null, an error or no answer yet |
| When | in the critical path: the read ran before the client-profile read, the settings read, memory, homework and the `session_metadata` write, all ahead of the handshake | fired right after `_aloInitBotpress()` (2518) and never awaited. The pill is drawn with whatever has arrived by then (2535) and updated in place when the answer lands (`_aloShowTherapistName`, 1040) |
| How often | every `loadConnectedState()` (each SIGNED_IN re-entry) | once per page load (`_aloTherapistNameRequested`), and never on a signed-out page, a no-link page or behind the consent gate |
| Failure | n/a (the read never failed; it was empty) | null: the fallback, no log. An error or a network failure: the fallback and one console line, `[Alo] Therapist name unavailable: <code>` |

The places that name the therapist read `connectedTherapistName`. `main` set it to "Your therapist" for every linked client; it now holds the name once it arrives (deviation 3). Measured with the stand-in name "Kano Melvin" (`s11_name_ok`): the pill reads "Hi Sam · with Kano Melvin", with the "with" part visible at 1280 px (at 640 px and below S9 A hides it by design), and the message modal reads "Message Kano Melvin" / "Kano Melvin will see this message…". With the answer 3 s late (`s11_name_slow`): the box opens on the fallback, then the pill, the homework card's "From" and a homework tip still on screen all switch to the name.

### B - three sentences

Section 4. Each sentence has one location in `dev.html`, the same location S9 section 7 lists; the old sentences are at 0.

### C - deleting the conversation you're in

**Before** (`main`, reproduced: `s11_delete_current` on `main`, both tiers). Delete the conversation on screen from the sidebar: the row and its messages go, the page keeps `currentSupabaseConvId` pointing at it, and its mapping (`alo_conv_<botpress id>`) still points at it. Both later messages are sent to the deleted row and refused by its foreign key (409, `23503`). Neither is saved, and the client sees nothing (console only). A page that resumed the conversation without writing to it yet does the same through the mapping (`s11_delete_current_resumed` on `main`).

**After.** Every delete ends in `_aloAfterConversationsDeleted(removed)` (3094):

1. It works out the row of the conversation on screen (`_aloOnScreenConversationRow`, 3056; deviation 7).
2. It forgets every mapping that points at a removed row (`_aloForgetConversationRows`, 3076), so nothing resumes into a deleted row.
3. If the on-screen row was removed, it runs `_aloStartOverAfterDelete()` (3124), in this order:
   - Mark that Botpress conversation as deleted: nothing from it is written again.
   - Reset persistence state, so nothing more goes to the deleted row.
   - Hold the box ("Connecting…").
   - `sendIdentityToBot('conversation-deleted', { reverify: true })`: the complete object, sent and read back.
   - Once `webchat:ready`, the same `_aloRestartConversation()` sign-in and private on/off use.
   - Wait for the new conversation to be connected (at most 3 s).
   - Reopen the box; the constant toast if the identity was not verified.

   If the webchat is not connected, it starts no new conversation, and the conversation's next messages go to a new row.

| Delete | `removed` | When the on-screen row counts as removed |
|---|---|---|
| A row in the sidebar (`deleteThread`, 3641) | that row | it is that row |
| Clear unpinned conversations (`clearHistory`, 3698) | the unpinned rows the page had listed | the server no longer has it (read back; deviation 11) |
| Delete my conversation history (`deleteAllConversationHistory`, 3757) | every row | it had a row |

Console after a delete of the conversation on screen, in order: `[Alo] Identity verified with Botpress (conversation-deleted)`, `[Alo] The conversation on screen was deleted: starting a new conversation`, `[Alo] New conversation started via restartConversation()`, `[Alo] Auth bridge sent to Botpress`. The restart closes the sidebar, as it does for "New conversation"; the toast "Deleted from your account" (or "History cleared") shows as before.

### D - dark-theme primary buttons

| Token | Light (`:root`) | Dark (`[data-theme="dark"]` and system-dark) |
|---|---|---|
| `--btn-primary-bg` | `var(--primary)` = `#3A7C86` | `#3A7C86` (was `--primary` = `#5299A5`) |
| `--btn-primary-hover` | `var(--primary-hover)` = `#2D6B74` | `#2D6B74` (was `--primary-hover` = `#6AADB8`) |
| `--btn-primary-text` | `#FFFFFF` | `#FFFFFF` |

The fill stays visible on every dark surface: `#3A7C86` is 3.75:1 against the page background, 3.35:1 against cards and modals, 3.11:1 against raised surfaces. Measurements: section 6, contrast table.

### E - the delete-history confirm

"This will delete all your conversations from your Alo account. Alo will still remember themes from recent sessions. **Memory summaries are cleared separately, under Memory settings.** This can't be undone." The new sentence sits after the one about what Alo still remembers, before the last line. "Memory settings" is in the menu for every linked account (S9 E), and its popover has "Clear all memories".

### F - tidy

`scan-invisible.py dev.html dev.css`: CLEAN, exit 0, before each commit. The diff's added lines contain no U+200B/U+200C/U+200D/U+FEFF/U+2060, no NBSP and no smart quote.

## 3. The RPC call and where it sits

```js
// dev.html 1020-1033
function _aloRequestTherapistName() {
  if (_aloTherapistNameRequested) return;
  _aloTherapistNameRequested = true;
  supabase.rpc('my_therapist_name').then(function(res) {
    if (res && res.error) { console.error('[Alo] Therapist name unavailable:', ...); return; }
    var name = res && typeof res.data === 'string' ? res.data.trim() : '';
    if (name && therapistLink) _aloShowTherapistName(name);
  }, ...);
}
```

`loadConnectedState()` (2373). On the linked path, past the consent gate and once `therapistLink` is set:

1. Hold the composer.
2. `_aloInitBotpress()`.
3. **`_aloRequestTherapistName()`** (2518), not awaited.
4. The client-profile read, then the settings read.
5. **`showConnectedUI(_aloTherapistName || ALO_THERAPIST_NAME_FALLBACK, clientName)`** (2535).
6. Then, unchanged: memory, homework, the `session_metadata` write, the handshake.

The call goes through supabase-js with the session's token (EXECUTE is for `authenticated` only). It also works before the function exists: the error answer leaves the fallback in place.

## 4. Copy: before / after

| Where | Before (`main`) | After (branch) | Source |
|---|---|---|---|
| Sign-in modal body (`main:2003`; 2072) | Sign in to save your conversations and let Alo remember what you've discussed. New accounts are set up by invitation. | Sign in to talk with Alo and let it remember what you've discussed. New accounts are set up by invitation. | brief B, verbatim |
| About > Your privacy (232) | … If you're signed in, you stay in control: turn memory off, start a private session (nothing from it goes into your history or memory), or ask Alo to forget a specific topic. | … If you're connected with a therapist, you stay in control: turn memory off, start a private session (nothing from it goes into your history or memory), or ask Alo to forget a specific topic. | brief B; **the example's "of what they see" not used** (deviation 6) |
| Privacy modal > Your Alo conversations (`main:5096`; 5335) | You can delete any conversation from your Alo account at any time from the sidebar. Deletion from the chat platform Alo runs on isn't in place yet. | You can delete any conversation from your Alo account at any time from the sidebar — or, when history is turned off, from the menu. Deletion from the chat platform Alo runs on isn't in place yet. | brief B, verbatim |
| Delete-history confirm (`main:3526`; 3754) | This will delete all your conversations from your Alo account. Alo will still remember themes from recent sessions. This can't be undone. | … Alo will still remember themes from recent sessions. Memory summaries are cleared separately, under Memory settings. This can't be undone. | brief E, verbatim |
| Pill (1068) | Hi {name} · with Your therapist | Hi {name} · with {therapist name}; the fallback when there is none | brief A |
| Message modal, homework "From", homework tip, Journal share lines | "Your therapist" | the therapist's name once it arrives | brief A (deviation 3) |

No other user-facing string changed. The console lines added are `[Alo] Therapist name unavailable: …`, `[Alo] The conversation on screen was deleted: …` (and its not-connected variant) and `[Persistence] Not saved: its conversation was deleted from history`.

## 5. Verification (brief section 3)

| # | Item | How | Result |
|---|---|---|---|
| 1 | A: "Kano Melvin" → "Hi … · with Kano Melvin"; null or a 500 → "with Your therapist"; the handshake's console sequence unchanged; the box opens no later | `s11_name_ok`, `s11_name_null`, `s11_name_500`, `s11_name_network`, `s11_name_slow`, `s11_name_once`, `s11_name_none_nolink`, `s11_name_none_signedout`, `s11_name_after_consent`, `s11_name_twolinks`; `s11_handshake` x 5 runs x 2 latencies x 2 tiers on `main` and the branch | PASS. The handshake sequence is identical on `main` and the branch in all 40 runs. The box opens 50-60 ms **earlier** at 60 ms per request (stand-in median 555 vs 615 ms; real 615 vs 665 ms), because the empty profile read no longer sits in front of the handshake; equal within noise at 15 ms. With the answer 3 s late the box still opens at once |
| 2 | B: each ruled sentence at every listed location; the old ones at 0 | `s11_copy` (signed-out page: sign-in modal, About, Privacy), `s11_copy_linked` (menu path); a count over the source | PASS. Each new sentence: 1 occurrence, at 2072, 232 and 5335; each old one: 0 (`main`: 1 each) |
| 3 | C: delete current → two messages → both in a new row; the old row gone; the sidebar shows the new one; the same for both bulk deletes | `s11_delete_current`, `s11_delete_current_fast`, `s11_delete_current_resumed`, `s11_clear_unpinned_current`, `s11_delete_all_current`; controls and failure paths in section 6 | PASS, both tiers, and at 375, 390 and 375 px dark. The two messages land in one new row, in order with their replies (turns 1-4). The old row and its messages are gone. No write was aimed at the deleted row, and no foreign-key failure. The sidebar lists the new row and not the old one. `main`: neither message saved |
| 4 | D: contrast per theme, all ≥ 4.5:1 | `s11_contrast_out`, `s11_contrast_in` in light, dark, system-dark (computed colours); screenshot pixels | PASS: 4.76:1 for every primary button in every theme, hover 6.06:1. `main`: 3.25:1 (hover 2.54:1) in dark and system-dark. Light is unchanged at `#3A7C86` (section 6) |
| 5 | E: the confirm shows the sentence | `s11_delete_all_confirm` | PASS: the whole text matches, Keep deletes nothing |
| 6 | S7c/S8/S9 scenarios; `node --check`; scan; nothing invisible in the diff | section 6; `node --check` on both inline scripts; `scan-invisible.py`; a count over the diff's added lines | PASS: 180/180 regression runs on the branch, and on `main` (section 6). `node --check` exit 0 on both inline scripts (348 and 230,530 characters). CLEAN, exit 0. Among the diff's 323 added lines: 0 each of U+200B, U+200C, U+200D, U+FEFF and U+2060, 0 NBSP, 0 smart quotes |

## 6. Harness

**Method.** I rebuilt the S9 harness this session; scratchpads are not kept between sessions.

- Headless Google Chrome 154, a local `python3 -m http.server`, a fresh profile per run, every outside host blocked at the resolver, virtual time.
- The harness copy of `dev.html` keeps the page's own CSP. It replaces only the two CDN script tags and the stylesheet path.
- supabase-js is the real 2.39.0 UMD. `window.fetch` is answered in-page by an emulator:
  - GoTrue: password, refresh, user, logout, verify.
  - PostgREST, with row rules per table and the conversation foreign key: messages cascade, summaries are set null.
  - `redeem_invite_code`, and `my_therapist_name` with the function's own semantics (null for no active link or more than one), overridable per scenario (a name, null, a 500, a delay, a network failure).
  - The `?t=` exchange.
  - The Botpress Chat API as the v3.3 client calls it, including the fetch-based event stream.
- Its state survives reloads. Supabase answers at 60 ms per request by default.
- A driver works the real UI with hit-tested taps and samples the composer every 5 ms. It waits a person's 250 ms after the box opens before typing, except in scenarios that send at the first instant on purpose.
- `window.botpress` is instrumented the same way in both tiers.

Botpress, two ways:

- **Stand-in**, modelled on the v3.3 bundles:
  - pre-init stubs;
  - `webchat:initialized`, then `initialized = true`;
  - a restored or created user;
  - resume (no `conversation` event) or create (event);
  - `webchat:ready` once connected;
  - `restartConversation` = a new conversation;
  - events posted as `{type: 'custom', data}`.
- **The real v3.3 `inject.js` and `webchat.js`**, unmodified apart from their three script URLs, with a fetch shim prepended inside the webchat's iframe.

**Brief 7 scenarios** (stand-in and real bundles; `main` fail counts are failed checks):

| Scenario | What it encodes | `main` | Branch | `main`, real | Branch, real |
|---|---|---|---|---|---|
| `s11_name_ok` | A, item 1: "Kano Melvin" in the pill and the message modal; one call, signed-in token, after the link read; no profile read | FAIL (6) | PASS | FAIL (6) | PASS |
| `s11_name_null` | A, item 1: null → "with Your therapist", no log | FAIL (2) | PASS | FAIL (2) | PASS |
| `s11_name_500` | A, item 1: a 500 → the fallback, one console line | FAIL (3) | PASS | FAIL (3) | PASS |
| `s11_name_network` | A: a network failure → the fallback | FAIL (1) | PASS | FAIL (1) | PASS |
| `s11_name_slow` | A: the answer 3 s late: the box opens first; pill, homework "From" and the tip then switch to the name | FAIL (7) | PASS | FAIL (7) | PASS |
| `s11_name_once` | A: SIGNED_IN re-entries make no second call | FAIL (3) | PASS | FAIL (3) | PASS |
| `s11_name_none_nolink` | A: no call on a no-link page (control) | PASS | PASS | PASS | PASS |
| `s11_name_none_signedout` | A: no call on a signed-out page (control) | PASS | PASS | PASS | PASS |
| `s11_name_after_consent` | A: no call behind the consent gate; one after consent | FAIL (3) | PASS | FAIL (3) | PASS |
| `s11_name_twolinks` | A: two active links → the function says null → the fallback | FAIL (2) | PASS | FAIL (2) | PASS |
| `s11_handshake` | A, item 1: handshake sequence and box-open time (compared across pages, section 5) (control) | PASS | PASS | PASS | PASS |
| `s11_copy` | B, item 2: the three sentences on a signed-out page; the old ones gone | FAIL (6) | PASS | FAIL (6) | PASS |
| `s11_copy_linked` | B: About and Privacy from a linked account's menu | FAIL (3) | PASS | FAIL (3) | PASS |
| `s11_delete_all_confirm` | E, item 5: the confirm's whole text; Keep deletes nothing | FAIL (2) | PASS | FAIL (2) | PASS |
| `s11_delete_current` | C, item 3: delete on screen → re-verified, restart, box held then reopened → two messages in one new row; old row gone; sidebar | FAIL (17) | PASS | FAIL (17) | PASS |
| `s11_delete_current_resumed` | C: a resumed conversation deleted before anything is said on this load | FAIL (16) | PASS | FAIL (16) | PASS |
| `s11_delete_current_resumed_nokey` | C: the same on the first load after this ships (no note): no restart, nothing lost | FAIL (3) | PASS | FAIL (3) | PASS |
| `s11_delete_other` | C: deleting another conversation restarts nothing; the chat goes on in its row | FAIL (1) | PASS | FAIL (1) | PASS |
| `s11_clear_unpinned_current` | C, item 3: Clear unpinned with the current one unpinned → new row; pinned kept | FAIL (17) | PASS | FAIL (17) | PASS |
| `s11_clear_unpinned_pinned_current` | C: only the pinned current one: nothing to clear (control) | PASS | PASS | PASS | PASS |
| `s11_clear_unpinned_keeps_pinned_current` | C: current pinned, an older one unpinned: the older goes, no restart | FAIL (1) | PASS | FAIL (1) | PASS |
| `s11_delete_all_current` | C, item 3: Delete my conversation history → new row; other account untouched | FAIL (7) | PASS | FAIL (7) | PASS |
| `s11_delete_late_reply` | C: a reply arriving mid-transition is written nowhere | FAIL (3) | PASS | FAIL (3) | PASS |
| `s11_delete_current_fails` | C: the DELETE fails → toast, no restart, same row (control) | PASS | PASS | PASS | PASS |
| `s11_delete_identity_fails` | C: the re-verification fails twice → restart anyway, the constant toast, saved | FAIL (4) | PASS | FAIL (4) | PASS |
| `s11_delete_during_private` | C: deleting the earlier conversation while private restarts nothing (control) | PASS | PASS | PASS | PASS |
| `s11_contrast_out` (light) | D, item 4: header, card and modal primary buttons (signed out) — light (control) | PASS | PASS | PASS | PASS |
| `s11_contrast_out` (dark) | D, item 4: header, card and modal primary buttons (signed out) — dark | FAIL (4) | PASS | FAIL (4) | PASS |
| `s11_contrast_out` (system) | D, item 4: header, card and modal primary buttons (signed out) — system | FAIL (4) | PASS | FAIL (4) | PASS |
| `s11_contrast_in` (light) | D, item 4: every other primary button and hover (linked) — light (control) | PASS | PASS | PASS | PASS |
| `s11_contrast_in` (dark) | D, item 4: every other primary button and hover (linked) — dark | FAIL (10) | PASS | FAIL (10) | PASS |
| `s11_contrast_in` (system) | D, item 4: every other primary button and hover (linked) — system | FAIL (10) | PASS | FAIL (10) | PASS |
| `s11_delete_current_fast` | C: the same, first message sent the instant the box reopens | FAIL (8) | PASS | FAIL (8) | PASS |
| `s11_clear_readback_fails` | C: Clear unpinned, read-back fails → treated as gone → new row | FAIL (4) | PASS | FAIL (4) | PASS |
| `s11_clear_readback_fails_pinned` | C: the same, current pinned → kept, no restart | FAIL (1) | PASS | FAIL (1) | PASS |
| `s11_delete_nolink` | C: a no-link account (no chat) deletes a conversation a stale note points to: no restart | FAIL (1) | PASS | FAIL (1) | PASS |

**Contrast, computed from the rendered buttons** (`s11_contrast_out` signed out, `s11_contrast_in` linked; label `#FFFFFF` everywhere):

| Button | Light, `main` | Light, branch | Dark, `main` | Dark, branch | System-dark, `main` | System-dark, branch |
|---|---|---|---|---|---|---|
| Header Sign In | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Signed-out card Sign In | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Sign-in modal Continue | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Confirm (e.g. Start fresh, Clear History, Delete) | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Homework Mark complete | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Memory card Got it | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Sidebar New conversation | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Share Copy Message | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| How Alo works Next | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Install banner Install | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Journal Save | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Journal share toggle (shared) | 4.76 | 4.76 | 3.25 | 4.76 | 3.25 | 4.76 |
| Any primary button, hover (desktop) | 6.06 | 6.06 | 2.54 | 6.06 | 2.54 | 6.06 |

Fill: `#3A7C86` in every theme on the branch (`main`: `#5299A5` in dark and system-dark). Cross-checked on screenshot pixels (real bundles, 500 px): the header Sign In, the card's Sign In and a confirm's primary button each measure fill `#3A7C86` / label `#FFFFFF` = 4.76:1 in all three themes on the branch, and `#5299A5` / `#FFFFFF` = 3.25:1 in dark and system-dark on `main`.

**S7c, S8 and S9 regressions** (73 scenarios, rebuilt from the three reports; each on `main` and the branch, stand-in and real bundles: 96 runs per page on the stand-in, 84 on the real bundles):

| Group | Scenarios | `main` | Branch |
|---|---|---|---|
| Startup handshake (S7c A, B) | `load_linked` (= S7c `startup_verified`), `startup_new_bp_user`, `startup_stale_once`, `startup_fails_twice`, `startup_getuser_fails_twice`, `startup_nodata`, `startup_hangs`, `startup_update_timeout_once`, `startup_metadata_write_fails`, `startup_profile_read_throws`, `fast_supabase_cold_webchat`, `bridge_order`, `refresh_reentry`, `refresh_during_private`, `concurrent_entries`, `homework_identity` | PASS, both tiers | PASS, both tiers |
| Private sessions (S7c C-F, S8 E) | `private_start_menu`, `private_start_popover`, `private_end_x`, `private_end_menu`, `new_private_while_private`, `new_conversation_while_private`, `private_start_fails`, `private_start_lands_but_times_out`, `private_end_fails`, `memory_off_private`, `private_end_late_reply`, `stuck_private_no_marker`, `reload_private_marker`, `private_reload`, `task_e_menu`, `f_banner_x_overlay` | PASS | PASS |
| Gates and sign-in (S7c, S8 A, B) | `gate_consent`, `signin_without_reload`, `task_a_wrong_password`, `task_a_unknown_email`, `task_b_no_reset`, `task_a_dormant` | PASS | PASS |
| History setting (S8 C) | `task_c_history_off`, `task_c_history_off_desktop`, `task_c_history_on`, `task_c_history_on_desktop`, `task_c_history_live` | PASS | PASS |
| Homework (S8 D) | `task_d_homework` | PASS | PASS |
| No-link copy (S8 section 3) | `classd_linked`, `classd_unlinked`, `classd_guest`, `about_table` (375, 390 px) | PASS | PASS |
| Pages without identity | `guest_unaffected`, `nolink_unaffected` | PASS | PASS |
| S9: header, history off, contrast, names, copy | `s9_header` (6 widths x light, dark, system-dark; 6 of them on the real bundles), `s9_header_states`, `s9_header_guest`, `s9_history_off` (500, 1280 px), `s9_history_off_delete_blocked`, `s9_history_on`, `s9_clear_memories_contrast` (light, system-dark), `s9_name_readable`, `s9_name_withheld`, `s9_contrast` (1280 light, dark, system-dark; 500 system-dark), `s9_copy` | PASS | PASS |
| S9: identity boundaries | `s9_nolink`, `s9_nolink_claim`, `s9_link_ended`, `s9_signedout`, `s9_invite_guest`, `s9_token_failed`, `s9_token_ok`, `s9_signin_stale`, `s9_signin_consent`, `s9_signout`, `s9_signout_other_tab`, `s9_account_switch` | PASS | PASS |

Re-cast for Brief 7, without weakening a check:
- `startup_profile_read_throws` fails the first profile read. On `main` that is the therapist's read; on the branch, where that read is gone, it is the client's. The outcome checked is the same.
- `s9_name_readable` and `s9_name_withheld` take the name from the profile on `main` and from the function on the branch. Both must show "Dr. Lee", and the exact fallback.
- `s9_history_off`: "AFTER-DELETE" must be saved to a row that exists and is not a deleted one. On the branch that row belongs to the new conversation.
- `s9_copy` checks S9's own copy only.
- `s9_signout` has one more check on the branch: `alo_onscreen_conv` is set before sign-out and gone at unload.

The measured values reproduce S9's: at 320 px the menu button sits at 264-308 with a 106 px pill; the menu icon is 4.86:1 light and 4.69:1 dark (S9: 4.84, 4.70); "Clear all memories" is 7.04:1 and 7.54:1 (S9: 7.0, 7.5).

**Totals.** Branch: 344 runs, 3,604 checks, all pass, no page error, no retry. The only console errors in branch runs are the expected ones inside failure-injection scenarios. `main`: all 180 regression runs and 20 handshake runs pass. Of its 72 Brief 7 runs, 16 pass: the controls marked above.

**Phone widths** (`CLAUDE.md`: 375 and 390): 12 Brief 7 scenarios at 375 px, 390 px and 375 px dark, on both tiers (72 runs). The 12 are the name (ok, slow), both copy scenarios, the confirm, the delete of the current conversation (fresh, resumed, late reply), both bulk deletes and both contrast scenarios. 72/72 pass (964 checks). Screenshots checked by eye: the dark buttons against card and page, the pill with the name at 1280 px, the delete-history confirm as a bottom sheet with the new sentence, the screen after a delete (only the new conversation), the sign-in modal.

**Harness artefacts**, fixed in the harness and not in the page:
- The dump and screenshot modes differ in viewport height by about 142 px, so pixel samples locate each button by its fill colour.
- A Share sheet's Close button is below the fold at 375×812; the driver scrolls it into view, as a person would.
- With 5 ms samples, the box's hold and the identity send fall in one task, so "held" is checked from the send onward.
- `s9_signout_other_tab` simulates the other tab with a `BroadcastChannel` message, which crosses the browser process. Under 8 parallel runs, virtual time outran it on `main` and the branch alike: 1 failure in the first final pass. Its wait is now in real time (a request to the local server pauses virtual time): 40/40 at 8 workers, then the whole regression set again, 360/360.

## 7. Declined, rulings needed, observations

Declined (out of scope by the brief): the bot; `index.html`; the parked branch; the consent flow; the Journal (apart from deviation 14's CSS); anything not named.

**Needs a ruling:**

1. **About, the example wording** (deviation 6). If Kano wants "of what they see", the list has to change too. For example: "If you're connected with a therapist, you stay in control of what they see: they see only what you share with them, when you use Alo, homework you view or complete, and a note if Alo thinks you may be in danger."
2. **Privacy, "delete any conversation … from the menu".** With history off the menu deletes all conversations at once, not one at a time. The sentence is ruled copy and applied verbatim; it is true of each conversation, done together.

**Found on the way, not changed:**

3. **The restart gap on the other paths.** Sign-in (S9 D), private on and private off restart the conversation and reopen or keep the box without waiting for the new conversation's stream. A message sent in that window reaches Botpress but is not saved (the reply is). Measured on the real bundles: after a sign-in from the signed-out card, a message sent the instant the box opened was not saved in 3 of 6 runs (2 on the branch, 1 on `main`); the reply was saved every time. A person needs longer than that to type, but a slow connection widens the window. The delete path now waits (deviation 9). The same wait in `_aloRunIdentityHandshake()` and the private transitions would close it; they are S7c/S9 code and not named here.
4. **The "Copied!" flash** in the Share modal turns a primary button `var(--success)` for 2 s: white on it is 3.17:1 in light and 2.36:1 in dark. It is a separate token, set inline by the script.
5. **Saved transcripts**: the client's own words are white on `--primary` (`.transcript-message.user`), 3.25:1 in the dark themes. It is text, not a button.
6. **About > How memory works**, "You're always in control: turn memory off, go private for a session, or ask Alo to forget something.", is untrue for a signed-in account with no link, which has neither. It is the same class as B's About sentence and not named.
7. **Two tabs.** Deleting in one tab the conversation another tab of the same account has on screen is not covered: that tab does not know about the delete. It was already so.
8. **S7c's `startup_hangs` figure.** When `updateUser` never answers, the box is released at 16 s (two 8 s attempts; `getUser` is never reached), not the 32 s the S7c report gives. 32 s is the worst case only when `updateUser` answers and `getUser` hangs.

**Not verifiable here** (the harness emulates these; the live site settles them, section 8):

9. **The function, live.** Whether `my_therapist_name()` is deployed and answers with the name for zztest1. The page is safe either way: an error leaves the fallback in place (check 1).
10. **The `conversation` event after a restart, live.** The v3.3 bundle emits it when Botpress's `conversation_started` answer marks the conversation as new (`isInitial`). That is what reopens the box after a delete. If live Botpress did not mark a restarted conversation as new, the box would reopen after the 3 s cap instead, safe but slow (check 2: "Connecting…" should be brief).
11. **The darker buttons on iOS Safari.** Verified in Chrome by computed colour and by screen pixels; Safari draws the same CSS colours.

## 8. Kano's five-minute check (alowen.ai/dev.html, after merge)

1. **The name** (zztest1, desktop width, console open). Reload. The pill reads "Hi … · with {the therapist's display name}" (on a phone the "with" part is hidden, as since S9). The console order is unchanged: `Identity verified with Botpress (startup)`, then `Auth bridge sent to Botpress`. The Network tab shows one `rpc/my_therapist_name`, and no `profiles?id=eq.<therapist id>`. ☰ → Message Therapist: "Message {the therapist's name}". If the pill still says "with Your therapist", the console has a `[Alo] Therapist name unavailable: <code>` line: `PGRST202` means the function is not in the database yet (the migration file's header says "not yet applied"; the brief says it is deployed).
2. **Delete the conversation you're in.** Send "one", wait for the reply, open Conversations, delete that conversation. The sidebar closes, the chat clears and shows "Connecting…" briefly, then an empty conversation; the toast "Deleted from your account". (If "Connecting…" lasts about 3 s every time, note it: section 7, point 10.) Send "two" and "three". Open Conversations: one new entry with both messages, and the deleted one gone.
3. **The same with Clear unpinned conversations** (the current one unpinned): a new conversation; pinned ones stay.
4. **Dark mode from the phone's own setting:** Sign In and every primary button are a deeper teal with crisp white labels.
5. **Copy:** the sign-in modal ("Sign in to talk with Alo…"), About > Your privacy ("If you're connected with a therapist…"), Privacy ("…from the sidebar — or, when history is turned off, from the menu."). With history off on a test account: ☰ → Delete my conversation history shows "Memory summaries are cleared separately, under Memory settings."
6. **For your review:** section 7, points 1 and 2.
