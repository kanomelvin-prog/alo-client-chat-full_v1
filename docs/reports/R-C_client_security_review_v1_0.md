# R-C -- Client App Security Re-read v1.0 (findings-only)

**Repo:** `kanomelvin-prog/alo-client-chat-full_v1` -- branch `auto/r-c-review` off `main` @ `64acefc` (the Brief 1a-min merge).
**Date:** 2026-09-16. **Brief:** `claude_Brief_R-C_Client_Security_Review_v1_0.md`.
**Deliverable:** this file only. No app file, CSS file, or `CLAUDE.md` was modified. No call was made to the live Supabase API or to Botpress. Nothing was pushed to `main`.

---

## Session Log

1. **Model.** Claude Opus 5 (`claude-opus-5`), effort max, bypass permissions, unattended. The brief names "Fable 5.1 (or highest available)"; this session ran on Opus 5.
2. **Interruptions and restarts.** None. One harness orchestration bug (reload detection) was fixed and that one scenario re-run; the first run's phase-2 data matched the re-run.
3. **Deviations from the brief, each with a reason.**
   - **Plan v1.9.2 is not on this machine** (same as R-B). A-nn definitions come from `claude_Alo_Pilot_Fix_and_Improve_Plan_v1_5_EXT.md`, `claude_Alo_Bot_Logic_Review_v1_0_EXT.md`, `claude_Alo_Client_UX_Review_v1_0_EXT.md`; RLS text from `claude_Supabase_RLS_Lockdown_Migration_v1_2_EXT.md` (Phase 1 is recorded as run from v1.4, which is not local).
   - **Ledger D36, D37, D38** were read from Appendix A of `claude_Brief_R-A_Supabase_Review_v1_0.md`, which carries D34-D38 verbatim; `alo-supabase/docs/decisions.md` does not contain them yet.
   - **A7-C definitions.** The March 31 audit and the A7 tracker are not local (R-B found the same). A7-C1/C2/C3/C4/C5/C19 were checked against the in-code markers and D36's list.
   - **Bot-side facts** come from `~/Downloads/Alo - 2026 Sep 13.bpz`, unpacked in the session scratchpad. Its revision metadata says it was saved **2026-09-08**, so any Studio change after that (Session 2: A-15, A-20, identity) is not reflected. Config variables in the export were not printed or copied. Line numbers cited as "Init_State 66" are lines inside that node's code card.
   - **Third-party library code** was read from the public CDNs into the scratchpad (anonymous GET, no credentials): supabase-js 2.39.0 UMD (bundles gotrue-js 2.56.0) and Botpress webchat v3.3 `inject.js` and `webchat.js`.
   - **Read-only network probes:** HTTP status of the three GitHub repo pages (to learn visibility) and `curl -I` / content-type of `https://alowen.ai/`, `/backup.html` and the stray file. No Supabase or Botpress API endpoint was contacted.
   - **Both client repos are public** (GitHub returns 200 anonymously; `alo-supabase` returns 404). This report is therefore readable by anyone once pushed. Findings describe vectors precisely enough to triage and fix, but no ready-to-paste payloads or token-harvesting steps are included.
4. **Checklist.** R-C.1 COMPLETED. R-C.2 COMPLETED (path enumeration in section 4). R-C.3 COMPLETED. R-C.4 COMPLETED. R-C.5 COMPLETED. R-C.6 COMPLETED. R-C.7 COMPLETED. R-C.8 COMPLETED. R-C.9 COMPLETED (section 5). R-C.10 COMPLETED (claims table in section 3). Report sections 1-7 COMPLETED.

**What was read.** `dev.html` in full (4,308 lines, every line, first); `index.html`, `dev.css`, `styles.css` via full `diff` plus targeted reads; `scripts/scan-invisible.py`; `manifest.json`; both `CLAUDE.md` files; `docs/reports/S4A-min_session_report_v1_0.md`; the R-B report and brief; the R-A brief (for D34-D38); Brief 1a-min v1.1; Plan v1.5; Bot Logic Review; Client UX Review; RLS Lockdown v1.2; `alo-supabase` `exchange-client-token/index.ts`, `_shared/tokens.ts`, `_shared/cors.ts`, the `client_session_tokens` migrations and the trigger-v3 reduction (role source); the bot export's Main flow (Init_State, Silent_Auth_Handler, Safety_Check, Check_And_Route, Validate_And_Send, Call_Claude memory-forget section); the supabase-js auth initialisation, URL-session and refresh code; the webchat persistence store, `updateUser` implementation and markdown renderer.

**Checks run.** `python3 scripts/scan-invisible.py dev.html dev.css index.html styles.css`: CLEAN on all four, exit 0. `node --check` on both inline scripts of each HTML file: all pass. `diff dev.html index.html`: 1,156 differing lines in 116 hunks; `diff dev.css styles.css`: 238 lines in 4 hunks. `grep -c alo_consent_acknowledged_fallback`: 0 in both HTML files. Headless Chrome 153 harness, 22 scenarios, no network (section 6).

---

## 1. Summary table

Severity per the brief's scale. "Regr." = regression or reopening of an existing A-, A7- or R-B finding. Line numbers are `dev.html` unless another file is named.

| ID | Sev | Angle | file:line | Title | Regr. |
|---|---|---|---|---|---|
| R-C-01 | S1 | R-C.1 / .3 / .8 | 1214-1228, 4189-4192, 814-849, 3838-3857; webchat v3.3 store; bot Init_State 66, 186, 621 | Sign-out leaves the Botpress user, its `clientId` data and the open conversation in the browser; the next person (guest or an unlinked account) sees the previous client's conversation and is served that client's memory and journal | A-21 (new client-side path) |
| R-C-02 | S1 | R-C.2 | 1973, 2033-2034, 3783-3797, 3815, 1461-1464 | The consent gate checks only `links[0]`; a second therapist link claimed through `?invite=` while connected goes active and is never gated | A-11 |
| R-C-03 | S1 | R-C.7 | 970-977, 732-734, 1459-1475, 2054-2056; index.html:809 | Therapist-set client display name is interpolated raw into an `<input value="...">` attribute; injected handlers run when the client taps their name | -- |
| R-C-04 | S1 | R-C.4 | 4040-4045, 2164-2175, 2336, 479, 573, 2137-2154, 2193-2195 | Private sessions write to history: every private conversation creates a listed `conversations` row, and after any reload the rest of that private conversation is saved to `conversation_messages` | -- |
| R-C-05 | S1 | R-C.5 | 2930-2955, 2697, 1909-1938; RLS v1.2:21-34; bot Init_State 222-372, Check_And_Route 40-43, 210-213 | "Clear all memories" and "forget" do not make Alo forget: success is a bare 204 (no client DELETE policy in the documented Phase 1 set), and the bot rebuilds deleted summaries from stored transcripts on the next conversation | -- |
| R-C-06 | S1 | R-C.1 | 450-457; supabase-js 2.39.0 `_initialize`, `_getSessionFromURL` | `detectSessionInUrl: true` on the implicit flow: a link carrying another account's tokens silently replaces the client's session, so what the client writes next lands in that account | -- |
| R-C-07 | S2 | R-C.4 | 2958-2979, 2981-2992 | Private mode is shown to the client before the bot is told, and the `updateUser` that tells it is not awaited, retried or confirmed (fails open) | A-20 dependency |
| R-C-08 | S2 | R-C.5 / .6 | 2697-2702, 2762-2772, 3544-3547, 3585-3591, 3605-3610, 1461-1477, 1167-1187, 992-998 | Every other delete, unshare, share, claim and completion is toasted as success on a bare 204 | R-B-06 class |
| R-C-09 | S2 | R-C.7 | 1073-1091, 1735-1739, 3597-3598 (via 797, 713, 717); index.html:911, 1364, 3069 | Homework title/goal/type and the therapist's display name go into `innerHTML` unescaped; handlers run on page load | -- |
| R-C-10 | S2 | R-C.3 | 2076-2110, 2246-2275; bot Init_State 63-104, Safety_Check 239-242 | The session nonce the client registers is never read by the bot (the client puts it where the bot does not look); identity is a bare `clientId` any page script can assert, and it is sent even when the nonce write fails | A-21; A7-C1 catch path |
| R-C-11 | S2 | R-C.2 | 1525-1528, 2000-2006, 1466-1475, 1214-1228 | A stored invite code outlives the sign-in attempt that stored it; the next account without a link on that browser auto-claims it and is renamed to the invitee | -- |
| R-C-12 | S2 | R-C.8 | 3840, 3993-3996; bot Safety_Check 234-274 | Guests (and anyone scripting the public webchat client id) create therapist-visible `crisis_events` rows with no authentication and no rate limit | R-B-01, R-B-07 |
| R-C-13 | S2 | R-C.10 | 1243, 1341, 1498, 215, 4158 vs 2081-2085, 1097-1103 | "Nothing is shared unless you share it", "Signing in does not share anything", "That's it." and the Privacy modal's therapist list omit the activity records and homework-viewed times every linked load sends | R-B-11 (client side) |
| R-C-14 | S2 | R-C.10 / .4 | 3000-3003, 3020-3022, 2879, 2193-2195 | "Memory is already off -- nothing is being remembered": history is still saved and private sessions are refused | -- |
| R-C-15 | S2 | R-C.10 / .4 | 2967-2968, 277, 3070; bot Init_State 225, 233 | Private-session copy ("Nothing from this conversation goes into your history or memory") is false for a conversation made private midway: earlier turns stay in history and are summarized | -- |
| R-C-16 | S2 | R-C.10 | 231, 3838-3857; webchat v3.3 store | "Guests start fresh every visit." The webchat restores a returning guest's conversation from `localStorage` | -- |
| R-C-17 | S3 | R-C.1 / .2 | 4189-4192, 1021-1050, 1379-1394, 3427 | A sign-out without reload keeps the previous account's `clientId`, `therapistLink`, settings and therapist name; the next account's consent write targets the wrong row; the share toggle is offered to an unlinked account | -- |
| R-C-18 | S3 | R-C.1 | index.html:1-46; dev.html:10-21 | Production has no CSP at all; the dev CSP allows `'unsafe-inline'` and wide CDN/connect hosts, so it contains none of R-C-03/R-C-09; the site is framable | A7-D9 precondition |
| R-C-19 | S3 | R-C.1 | 4207-4216 | A failed `?t=` link in a browser that already has a session leaves the page stuck: no chat, guest header, spinner, no timeout | -- |
| R-C-20 | S3 | R-C.1 | 4182-4186, 1630-1632; supabase-js `_getSessionFromURL` | A password-reset link never shows "Set New Password": the library clears the hash before `PASSWORD_RECOVERY`, so the `type=recovery` check always fails | -- |
| R-C-21 | S3 | R-C.3 / .10 | 814-849, 2246-2247, 3104-3105; claims 229, 304, 378, 3209 | Signed-in accounts with no link send no identity to the bot until "New conversation"; the memory and journal claims shown to them are false until then | -- |
| R-C-22 | S3 | R-C.4 / .5 | 4015-4019, 4061-4065, 2187 | Message content sits in plaintext `localStorage` queues (`alo_unsent_messages`, `alo_dropped_messages`) that are never replayed and never cleared, including after Log Out | A7-C2 / C19 side effect |
| R-C-23 | S3 | R-C.9 | 2202-2211, 2240-2244, 3084 | The A7-C3 write queue reads `currentSupabaseConvId` when the write runs, not when it was queued; a new conversation started while a write is pending writes that message with a null conversation (silent loss) | A7-C3 (introduced by the fix) |
| R-C-24 | S3 | R-C.5 | 2731-2767 | "Clear unpinned conversations" counts only loaded threads but deletes every unpinned row; `source_expired` marking covers only loaded ids | -- |
| R-C-25 | S3 | R-C.6 / .4 | 3620-3641, 3081-3083 | "Bring this to Alo" silently ends a private session and sends the entry into a remembered conversation | -- |
| R-C-26 | S4 | R-C.1 | 50, 442-457, 3813 | `?t=` is stripped after two third-party scripts have run; no referrer policy | -- |
| R-C-27 | S4 | R-C.1 | 456 | A link carrying `error_description` in the fragment signs the client out | -- |
| R-C-28 | S4 | R-C.2 | 1594-1600, 4187-4188 | Modal sign-in runs the connected path twice: two `session_metadata` rows and two nonces | S4A-min section 9 |
| R-C-29 | S4 | R-C.7 | 1451 | Invite code is interpolated unencoded into the PostgREST filter (`#` drops `&status=eq.pending`) | -- |
| R-C-30 | S4 | R-C.7 | 1566 | `escAttr()` inside a JS string inside an HTML attribute: the user's own email re-opens the string (self-XSS) | -- |
| R-C-31 | S4 | R-C.2 | 1368-1369, 1385-1407 | Consent failure copy says "Nothing was changed" also when the PATCH succeeded and only the re-read failed | -- |
| R-C-32 | S4 | R-C.9 | `backup.html`, `padding: 8px 12px;`, manifest.json:5 | Stray files on the production origin (a bare Botpress embed without CSP; an old app copy) and a `start_url` of `./dev.html` | R-B-38 sibling |

Counts: S1 x6, S2 x10, S3 x9, S4 x7.

---

## 2. Findings

### R-C-01 -- S1 -- Sign-out leaves the Botpress identity and conversation for the next person (R-C.1, R-C.3, R-C.8)

**What.** Log Out does three things and none of them touches Botpress:

```
dev.html:1215  const { error } = await supabase.auth.signOut();
dev.html:1222-1225  clientId = null; therapistLink = null; chatSettings = {}; currentHomeworkId = null;
dev.html:1227  location.reload();
```

The SIGNED_OUT listener (`4189-4192`) runs `resetPersistenceState(); authBridgeSent = false; resetToGuestUI();`, and `resetToGuestUI()` (`1021-1050`) only re-skins the header and calls `_aloInitBotpress()`.

Botpress webchat v3.3 keeps its user credential and conversation in **this site's** storage:

```
inject.js   Af = Sn.template("iframe", ...).onLoad(a => { a.contentDocument ... innerHTML = `<!DOCTYPE html>...`; <script src=webchat.js> })   // iframe has no src: about:blank, same origin as alowen.ai
webchat.js  i = Xk(`bp-webchat-${be.clientId}`, r?.storageLocation)    // zustand persist {user:{userId,userToken}, conversationId}; localStorage unless storageLocation is 'sessionStorage'
webchat.js  let X = a.conversationId || l; if (!X || !D) { createConversation } else { const le = await m({client:V, conversationId:X}); w(le); ... }   // on load: fetch and render the stored conversation
```

`dev.html:3842-3856` sets no `storageLocation`, and nothing in the file removes `bp-webchat-fc13c6c1-...` or resets user data. The Botpress user's server-side data keeps whatever the page last sent (`clientId`, `sessionNonce`, `privateSession`). The bot trusts that data first:

```
Init_State 66    const bridgeClientId = fetchedData?.userData?.clientId || fetchedData?.data?.clientId || fetchedData?.clientId || null;
Init_State 186   if (conversation.turnCount === 1 && resolvedClientId) {   // memory: summaries of the latest 3 non-private conversations
Init_State 621   journal_entries?client_id=eq.<resolvedClientId>&order=created_at.desc&limit=5   // content up to 400 chars each, into the LLM context
Validate_And_Send 27   if (journalSaveContent.length > 0 && conversation.boundClientId) {   // Alo-generated journal writes
Safety_Check 239-256   const userDataClientId = event.state.user?.data?.clientId ... crisisPayload.client_id = resolvedClientId
```

A signed-in account with no link never overwrites that data: `showLoggedInNoConnection()` (`814-849`) sends no identity (see R-C-21).

**Harness.** `logout_botpress_residue`: connected client C, Log Out, reload. Result: guest header; Botpress `init` restored conversation `bpconv-1`; Botpress user data still `{clientId: <C>, sessionNonce: ...}`; the `bp-webchat-*` store (user key) still in `localStorage`; the page made no Botpress call other than `init` and `open`. `stale_after_signout_B_nolink`: A connected, signed out, B (no link) signed in in the same tab. Zero identity calls for B, and user data still A's. (The Botpress side is emulated from the v3.3 source; see section 7.)

**Why it matters.** On a shared device (a family iPad, a shared laptop, a clinic kiosk), the next person on that browser sees the previous client's last conversation in the chat window. On the first turn of any new conversation, Alo is primed with the previous client's session summaries, five most recent journal entries, homework and therapist name, and told to act as "an ongoing confidant who already knows this background". What the new person says can be saved into the previous client's journal (`[JOURNAL_SAVE:]`). A crisis phrase raises an alert on the previous client's record, so that client's therapist sees their name and emergency panel. This is data exposure across clients (S1), and the same class the dashboard review rated S1 for shared devices (R-B-03).

**Fix.** On Log Out and on every SIGNED_OUT or account change, discard the Botpress identity before the reload. Remove the `bp-webchat-<clientId>` store, or set `storageLocation: 'sessionStorage'` and start a new user per sign-in, and send a user-data wipe first. The bot's A-21 hardening must also stop trusting a stale user-data `clientId`.

**Regression.** A-21 names the bot trusting a client-asserted id. The sign-out persistence path is new.

### R-C-02 -- S1 -- A second link is never gated (R-C.2, A-11)

**What.**

```
dev.html:1973  const links = await api(`/rest/v1/therapist_clients?client_id=eq.${user.id}&status=eq.active&select=id,therapist_id,client_id,display_name,status,consent_acknowledged_at`);
dev.html:2033  const link = links[0];
dev.html:2034  if (aloConsentRequired(link)) {
```

The query has no `order=`, so `links[0]` is whichever active row PostgREST returns first. The consent write's own re-read checks every row (`1393-1394`, `rows.every(...)`); the gate does not. The route to a second active row is ordinary: `_aloHandleInviteParam()` runs on every page load (`3815`) and opens the connect modal whether or not the client is already connected (`3794`). The claim PATCH (`1461-1464`) then activates the new row, and `loadConnectedState()` (`1483`) evaluates only `links[0]`.

**Harness.** `invite_while_connected`: client C connected to T1 (consented) opens `?invite=<T2 code>`. The connect modal opens over the chat, prefilled. Link: T2's row becomes `status: active` with `consent_acknowledged_at: null`; the page stays "Hi Casey · with Dr. One"; no screens; toast "Connected successfully!"; a second `session_metadata` row is written. `gate_multilink_consented_first` (consented row returned first): no gate, connected. `gate_multilink_unconsented_first` (unconsented row first): gate. The outcome depends on row order.

**Why it matters.** T2 now has an active client who never saw the consent screens for that relationship. T2's dashboard gets the client's activity, homework status and crisis alerts, since `crisis_events` has no therapist column (R-B-07). The bot's Init_State picks `settingsRes.data[0]` of the same unordered query for therapist name and homework. This is the A-11 property Pilot Gate 5 tests ("no consent bypass path"), reopened for any client with more than one link: switching therapists, or seeing a couples and an individual therapist.

**Fix.** Hold the screens when `links.some(aloConsentRequired)`, write consent to the unconsented row(s), and do not open the connect modal for an already-connected account without an explicit add/switch step.

**Regression.** A-11, closed by Brief 1a-min for the single-link case only.

### R-C-03 -- S1 -- Therapist-set display name into an HTML attribute (R-C.7)

**What.**

```
dev.html:880   badge.innerHTML = ... '<span class="editable-name" id="clientNameEditable" ...>' + safeClient + '</span>' ...   // escaped here
dev.html:970   const currentName = document.getElementById('clientNameEditable')?.textContent || '';   // textContent decodes it again
dev.html:974   <input type="text" id="nameEditInput" value="${currentName}"
dev.html:732   const firstInput = modal.querySelector('input, textarea, select');
dev.html:734   setTimeout(() => firstInput.focus(), 100);
```

The name's origin is the therapist. The invite's "friendly name" (`therapist_clients.display_name`) is copied into the client's own profile at claim (`1459`, `1466-1475`) and is the badge fallback (`2055-2056`). The dashboard tells the therapist that name is "visible only to you" (R-B-09).

**Harness.** `xss_therapist_strings`: a link display name that closes the `value` attribute and adds an event-handler attribute. The rendered input's attribute list became `type, id, value, autofocus, onfocus, x, placeholder, ...`, and the handler ran as soon as the "What should we call you?" modal opened (one tap on the name). This ran under the page's own CSP meta, because `script-src` includes `'unsafe-inline'`. `index.html:809` has the same line. A client's self-typed name reaches the same sink.

**Why it matters.** Script running in the client's origin can read `localStorage['alo_client_session']` (including the refresh token) and the Botpress user key (R-C-01). With those it can read the client's stored transcripts, journal and summaries. That defeats the "your therapist never sees what you say" posture from the one party the product promises it to. The brief's rule: a therapist-supplied string into an attribute is S1.

**Fix.** Create the input without interpolation and set `input.value = currentName` after insertion, or pass every template value through `escAttr()`.

### R-C-04 -- S1 -- Private sessions write to history (R-C.4)

**What.** Two paths.

(a) The private conversation's own row. The message handler creates the Supabase conversation for any first message with no private check, and records the flag in the row it creates:

```
dev.html:4040-4045  if (!currentSupabaseConvId) { ... ensureConversation(bpConvId || 'conv_' + Date.now()) ... }
dev.html:2171       is_private: isPrivateSession || false,
dev.html:2336       conversations?client_id=eq.${user.id}&select=id,title,turn_count,created_at,updated_at,pinned,pinned_at&order=pinned.desc,created_at.desc   // no is_private filter
```

(b) Content after a reload. The private flag is page memory only (`479`), and only `saveMessage` checks it (`2194`). Any reload clears it, including the menu's Dark/Light Mode item, whose `toggleTheme()` calls `window.location.reload()` (`573`). Botpress then restores the same conversation, and the `alo_conv_<botpress id>` mapping resumes the private row:

```
dev.html:2137-2141  var storageKey = 'alo_conv_' + botpressConvId; var existingId = localStorage.getItem(storageKey); if (existingId) { currentSupabaseConvId = existingId;
```

**Harness.** `private_new_conv_and_reload`, phase 1: "Start new private conversation", then the first message, gives `POST conversations {is_private: true, title: "Sep 16, 2026 · 10:32 AM", botpress_conversation_id}`. The sidebar lists "Sep 16, 2026 · 10:32 AM / 0 turns" while the tip reads "Nothing from this conversation goes into your history or memory." Phase 2 (reload): banner gone, `isPrivateSession: false`, Botpress restored the same conversation, and bot user data still `privateSession: "true"`. The next message gives `POST conversation_messages` into the private row, then `PATCH conversations {turn_count: 1}`.

**Why it matters.** Every private conversation leaves a dated, listed history entry holding the Botpress conversation id (a pointer to the transcript the platform still stores). A theme switch, an iOS PWA eviction or a pull-to-refresh silently turns the rest of a private conversation into saved history, on a surface the client was told "won't be remembered". The bot's memory query excludes `is_private=true` rows (Init_State 225, 233), so these turns are not summarized, but they are history. The brief rates any private-session write to history S1.

**Fix.** Skip `ensureConversation`/`saveMessage` while private, keep the private flag per Botpress conversation id so a reload restores it, and filter `is_private` out of the thread list.

**Regression.** Path (a) was noted as pre-existing in the S4A-min report (section 9) but not triaged.

### R-C-05 -- S1 -- "Clear all memories" and "forget" do not make Alo forget (R-C.5)

**What.** The client:

```
dev.html:2933-2934  'This permanently deletes all conversation summaries Alo has stored. ' + 'Future conversations will start fresh with no context from past sessions.\n\n'
dev.html:2948       await api('/rest/v1/conversation_summaries?client_id=eq.' + user.id, 'DELETE');
dev.html:2949       showToast('All memories cleared');
dev.html:1926-1928  if (method === 'POST') { options.headers['Prefer'] = 'return=minimal'; }   // DELETE/PATCH: no Prefer; PostgREST answers 204, no body
dev.html:1936-1937  const text = await response.text(); return text ? JSON.parse(text) : null;
```

Per-conversation delete issues the same kind of request (`2697`).

The policy text: RLS Lockdown v1.2 Phase 1 drops the public ALL policy on `conversation_summaries` and creates `client_update_own_summaries` (UPDATE) and `client_select_own_summaries` (SELECT). It creates no DELETE policy for `authenticated`. Under that text both client deletes match zero rows and return 204. The live policy set (run from v1.4) is not verifiable here.

The bot, even when rows are deleted:

```
Init_State 225   conversations?client_id=eq.<id>&turn_count=gte.4&is_private=neq.true&order=created_at.desc&limit=4
Init_State 262   var needMsgIds = pastConvs.filter(function(c) { if (!summaryMap[c.id]) return true; ...
Init_State 266   conversation_messages?conversation_id=in.(<needMsgIds>)&order=turn_number.asc,created_at.asc&select=conversation_id,role,content,turn_number
Init_State 345   axios.post(MEM_URL + '/rest/v1/conversation_summaries', { conversation_id, client_id, topic_label, summary_text, ... })
Check_And_Route 40-43    axios.delete(... '/rest/v1/conversation_summaries?client_id=eq.' + conversation.boundClientId ...)   // "forget everything"
Check_And_Route 210-213  axios.delete(FORGET_URL + '/rest/v1/conversation_summaries?id=in.(' + deleteIds + ')' ...)   // "forget the conversation about X"
```

Neither the client nor the bot's forget path touches `conversation_messages`. The first turn of the next conversation regenerates summaries for the latest three non-private conversations that lack one, and loads up to five journal entries regardless.

**Harness.** `delete_zero_rows`: "All memories cleared" was toasted with zero rows changed; no verification read followed.

**Why it matters.** The client is told "Future conversations will start fresh with no context from past sessions". The About modal offers "ask Alo to forget a specific topic" (`216`, `230`). With memory on, for any of the three most recent conversations, both are undone by the next conversation's first turn, and neither result is checked. Deletion that silently does not delete is S1.

**Fix.** Verify every delete with `Prefer: return=representation` and treat an empty result as failure, and make clear/forget exclude the source conversations from regeneration (a flag Init_State honours, or deleting their transcripts). Until then the copy must say what happens.

### R-C-06 -- S1 -- URL tokens replace the client's session (R-C.1)

**What.**

```
dev.html:450-457  window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, { auth: { persistSession: true, storage: window.localStorage, storageKey: 'alo_client_session', autoRefreshToken: true, detectSessionInUrl: true } })
```

supabase-js 2.39.0 defaults `flowType` to `"implicit"`. Its initialisation:

```
_initialize()         if (e || this.detectSessionInUrl && this._isImplicitGrantFlow()) { const {data:t, error:s} = await this._getSessionFromURL(e); if (s) ... await this._removeSession() ...; await this._saveSession(r) ...
_isImplicitGrantFlow()  const e = o(window.location.href); return !(!r() || !e.access_token && !e.error_description)
o(url)                reads parameters from the fragment and from the query string
_getSessionFromURL()  const {access_token, refresh_token, expires_in, token_type} = t; ... await this._getUser(n) ... window.location.hash = ""
```

The in-file comment (`3709-3713`) notes this only to say it does not interfere with `?t=`.

**Harness (real library, fetch answered locally).** `real_implicit_hash_injection`: the browser holds client V's session; the page is opened with another account's access token, refresh token, expiry and token type in the fragment. After load, `alo_client_session` belongs to the other account; the page shows the connected UI ("Hi Victim · with Dr. One", because the sending account had chosen those names); `updateUser` sent the other account's id to Botpress. `real_implicit_query_injection`: the same via the query string, and the tokens stay in the address bar and history.

**Why it matters.** Anyone holding a live session for any account can send a client a link that silently swaps the client's login. A therapist holds their own test client's session after "Open as client". Everything the client writes afterwards is saved into the sender's account and readable by the sender: transcript rows, journal entries, and summaries built from them. The badge text belongs to the sending account, so it can be made to match. No OAuth provider is used on this build; the only URL-borne sessions it needs are the email links, which already misbehave (R-C-20).

**Fix.** Set `detectSessionInUrl: false` and handle recovery and confirmation explicitly, or switch to `flowType: 'pkce'` so a session can only come from a code this browser started.

### R-C-07 -- S2 -- Private mode is announced before the bot is told (R-C.4)

**What.**

```
dev.html:2959-2968  isPrivateSession = true; updateMemoryUI(); updatePrivateChatBtn(); ... showToast('Private session — this conversation won\'t be remembered'); _aloShowTip('privateSession', 'Nothing from this conversation goes into your history or memory.');
dev.html:2974-2978  if (window.botpress) { window.botpress.updateUser({ data: { privateSession: 'true' } }); }   // not awaited, no catch, no retry
```

`endPrivateSession()` (`2987-2991`) is the same. On the exported bot revision, the flag is read once, at turn 1, for memory and journal context (Init_State 213-222, 612). `JOURNAL_SAVE` never checks it (Validate_And_Send 27; A-20 open). A mid-conversation toggle therefore changes nothing bot-side.

**Harness.** `private_flag_delivery_fails`: the `updateUser` promise rejects. The banner, toast and tip are all shown; bot user data has no `privateSession`; the only trace is an `unhandledrejection` in the console.

**Why it matters.** The client is told the session is private on the strength of a request that may never have landed. Every bot-side protection keys on this flag, including A-20's gate once it ships. A path that fails open (S2); when it fails and the bot writes, the result is a private-session write to memory or journal.

**Fix.** Await `updateUser` and show the private state only once it resolves, or show a failure state.

**Regression.** Depends on A-20 (bot side, Gate A).

### R-C-08 -- S2 -- Other destructive and privacy writes are toasted on a bare 204 (R-C.5, R-C.6)

**What.** None of these requests asks for `return=representation` or re-reads the row. PostgREST returns 204 for a write filtered to zero rows exactly as for a real one (the consent write at `1388-1394` already handles this correctly).

| Action | Request (line) | Toast | Verified? |
|---|---|---|---|
| Delete conversation | DELETE `conversation_summaries?conversation_id=eq.<id>`, DELETE `conversations?id=eq.<id>` (2697-2698) | "Conversation deleted" | No; the row is removed from the local list |
| Clear unpinned | PATCH `conversation_summaries ... source_expired`, DELETE `conversations?client_id=eq.<uid>&pinned=eq.false` (2762-2767) | "History cleared" | No |
| Delete journal entry | DELETE `journal_entries?id=eq.<id>` (3544) | "Entry deleted" | No (the list refresh would show it again) |
| Revoke share | PATCH `journal_entries?id=eq.<id>` `{shared_with_therapist:false}` (3585) | "Share revoked" | No; the button flips locally |
| Share | PATCH `{shared_with_therapist:true}` (3605) | "Entry shared" | No |
| Claim invite | PATCH `therapist_clients?id=eq.<id>` `{client_id, status:'active'}` (1461-1464) | "Connected successfully!" (1477) | No; shown before the gate re-read |
| Mark homework complete | PATCH `homework_cards?id=eq.<id>` (1167-1170) | "Marked complete -- nice work!" | No |
| Rename self | PATCH `profiles?id=eq.<uid>` (992-994) | "Name updated" | No |

Removing a conversation's transcript depends on an `ON DELETE CASCADE` from `conversation_messages` to `conversations` that no repo defines. If it is absent, the DELETE fails with a foreign-key error (visible) or the messages are orphaned (silent).

**Harness.** `delete_zero_rows`: all five client-visible actions toasted success with `rowsChanged: 0`. After "Share revoked" the server row still had `shared_with_therapist: true`.

**Why it matters.** If a policy is missing or tightened, the client is told a conversation or journal entry is gone, or a share withdrawn, while the server still has it and a therapist may still read it. S2 as a fail-open pattern (the same class as R-B-06). Any of these becomes S1 (silent non-deletion, or a revoke that leaves an entry visible) if the live policies filter the write; see section 7.

**Fix.** Send `Prefer: return=representation` on these mutations, treat an empty array as failure, and toast accordingly.

### R-C-09 -- S2 -- Therapist-supplied strings into `innerHTML` (R-C.7)

**What.**

```
dev.html:1077  '<div class="homework-from">From ' + therapistName + '</div>' +
dev.html:1078  '<h3 class="homework-title">' + (hw.title || 'Practice exercise') + '</h3>' +
dev.html:1083  (hw.homework_type ? '<span class="homework-type-tag">' + hw.homework_type + '</span>' : '') +
dev.html:1084  '<p class="homework-goal">' + (hw.goal || '') + '</p>' +
dev.html:1737  createModal(`Message ${therapistName}`, `
dev.html:1739      ${therapistName} will see this message in their dashboard.
dev.html:3598  showConfirm('Share this entry?', therapistName + ' will be able to see this entry. You can revoke anytime.', {
dev.html:797   `<p>${message}</p>`          // showConfirm
dev.html:713   <h2 id="${modalId}-title">${title}</h2>   // createModal; 717 inserts bodyHTML; 725 insertAdjacentHTML
```

`therapistName` / `connectedTherapistName` is the therapist's `profiles.display_name` (`2049-2052`). The badge (`877`) and the journal badge (`3372`) escape it; these sites do not.

**Harness.** `xss_therapist_strings`: handlers in the homework title, goal and type, and in the therapist name, ran at page load. Opening "Message Therapist" ran the name twice more, and the share confirm once more. Production has the same sinks (`index.html:911`, `1364`, `3069`).

**Why it matters.** The impact is as for R-C-03 (the client's session and transcripts), from homework a therapist assigns or a name a therapist sets. By the brief's rule, innerHTML is S2.

**Fix.** Pass each value through `esc()` at the concatenation, or build these nodes with `textContent`.

### R-C-10 -- S2 -- The nonce is never checked; identity is a bare assertion (R-C.3, A-21)

**What.** The client registers a nonce and then sends identity:

```
dev.html:2077        sessionNonce = crypto.randomUUID();
dev.html:2081-2085   await api('/rest/v1/session_metadata', 'POST', { client_id: clientId, session_id: sessionId, nonce: sessionNonce });
dev.html:2090-2097   window.botpress.updateUser({ data: { sessionNonce, clientId, homeworkActive: JSON.stringify(hwSummary), timeZone } });
dev.html:2104-2110   } catch (err) { console.error('Session metadata write failed:', err); sendAuthBridge(); }   // bridge still sent
dev.html:2254-2257   window.botpress.sendEvent({ bp_event: 'alo_auth_bridge_v1', clientId: clientId });
```

The bot:

```
Init_State 66      const bridgeClientId = fetchedData?.userData?.clientId || ...        // trusted first, unverified
Init_State 75      const sessionNonce = event.payload?.sessionNonce || null;            // only if no user-data clientId; this client never sends a nonce in an event payload
Silent_Auth_Handler   if (typeof p.clientId === 'string' && p.clientId.length > 10) { conversation.authClientId = p.clientId; ...   // read by nothing else in the export
Safety_Check 239   const userDataClientId = event.state.user?.data?.clientId || null;
```

**Why it matters.** Any script on the page, or the console, can call `window.botpress.updateUser({data:{clientId: '<any uuid>'}})` or `sendEvent(...)`. Nothing client-side prevents or signs it, and the bot then loads that client's memory, journal and homework, writes journal entries and attributes crisis events to them. The `session_metadata` nonce write authenticates nothing on this build, because the value is placed in user data while the bot's verifier reads the event payload. A-21's "minimum" fix (make the verified nonce primary) will not work with this client unless both sides agree on where the nonce travels. The catch path sends a bare `clientId` even when the nonce row was never written. The consequence is A-21 (open, Gate A); the client-side defects are the mismatch and the fail-open catch.

**Fix.** Send the nonce where the bot verifies it, have the bot resolve identity only from a nonce it finds in `session_metadata` (bound to `client_id`), and do not send the bridge when the nonce write failed.

**Regression.** A-21 (open). The catch path has been in place since the A7-C1 commit `1be5fa7`, by design ("better a degraded session than no conversation at all").

### R-C-11 -- S2 -- A stored invite code is claimed by the next account (R-C.2)

**What.**

```
dev.html:1526-1528  if (inviteCode) { localStorage.setItem('alo_pending_invite', inviteCode); }   // before the sign-in attempt at 1536
dev.html:2000-2003  var pendingInvite = user.user_metadata?.invite_code || localStorage.getItem('alo_pending_invite'); if (pendingInvite && !_aloPendingInviteHandled) { ... localStorage.removeItem('alo_pending_invite');
dev.html:1470-1473  if (!currentName || currentName === user.email?.split('@')[0]) { await api(`/rest/v1/profiles?id=eq.${user.id}`, 'PATCH', { display_name: therapistDisplayName }); }
```

The key is set before sign-in is attempted, survives a wrong password, an abandoned modal or "Account created! Check your email to confirm." (`1576-1579`), and is not cleared by Log Out.

**Harness.** `pending_invite_residue`: `alo_pending_invite` left from an earlier attempt; account B (no link) signs in. Requests: `GET therapist_clients?invite_code=eq.<code>&status=eq.pending`, `PATCH therapist_clients {client_id: <B>, status: 'active'}`, `PATCH profiles {display_name: 'Jordan'}`. Toast "Connected successfully!", then the consent screens.

**Why it matters.** On a shared browser, person B is linked to the therapist who invited person A, under A's name. The code is spent, so A cannot claim it. If B taps through consent, the therapist's dashboard shows "Jordan" active and receives B's activity and crisis alerts as Jordan's, with Jordan's emergency contact. This is identity confusion with a therapist-visible outcome. S2 because it needs a shared browser and an abandoned or unconfirmed sign-in.

**Fix.** Keep the code in `sessionStorage` for the attempt only, clear it on failure and on Log Out, and only claim it for the email that started the attempt.

### R-C-12 -- S2 -- Guests create therapist-visible crisis events (R-C.8, feeds R-B-01)

**What.** Guest chat opens without an account (`4224-4225`, `1048-1049`, `4214`); the webchat client id is in the page source (`3840`). For a guest the page writes nothing to Supabase (`3993-3996` returns before persistence), but the bot does:

```
Safety_Check 245-274   crisisPayload = { severity:'high', category, alo_response_action:'provided_988_resources', action_notes: `Tier ${crisisTier}: ${userMessage.substring(0, 200)}`, acknowledged:false };
                       if (resolvedClientId) { crisisPayload.client_id = resolvedClientId; }   // absent for a guest -> client_id null
                       await axios.post(`${SUPABASE_URL}/rest/v1/crisis_events`, crisisPayload, { headers: { apikey: SUPABASE_KEY /* service role */ ...
```

No rate limit exists in the page, in the node, or in any Supabase object in the repos. The Chat API can be driven directly with the public client id, creating a fresh Botpress user per request.

**Why it matters.** R-B-01 (S1) showed that fifty newer null-client events push a therapist's own clients' open alerts out of Needs Attention, and R-B-07 that every therapist receives every guest event. Both were described as organic accumulation. On this build anyone on the internet can produce them on demand, and each row also stores up to 200 characters of what was typed (A-15). S2 here because the root causes are R-B-01/R-B-07 and bot-side; see the R-C.8 answer for the smallest fix.

**Fix.** Write `crisis_events` only for an identity the bot has verified, and route unidentified events elsewhere (details in R-C.8).

**Regression.** R-B-01, R-B-07.

### R-C-13 -- S2 -- Sharing and visibility claims omit what flows without the client's action (R-C.10)

**What.** The sentences:

```
dev.html:1243  onboarding screen 2: "If you want to share something ... you choose that, one thing at a time. Nothing is shared unless you share it."
dev.html:1341  consent screen 4:    "Your conversations are yours — nothing is shared unless you choose to."
dev.html:1498  login modal:         "Your conversations stay private. Signing in does not share anything."
dev.html:215   About:               "... they can see general patterns across your sessions and whether you've completed any reflections they've assigned. That's it."
dev.html:4158  Privacy modal:       "Your therapist sees homework status, messages you send them, and any journal entries you explicitly share"
```

What every signed-in, linked load does without being asked:

```
dev.html:2081-2085  POST session_metadata { client_id, session_id, nonce }        // dashboard: "last active", "Used Alo N times this week" (R-B-11)
dev.html:1097-1103  PATCH homework_cards { viewed_at }                             // when a card first renders
```

Crisis alerts also reach the therapist without an action. Screens 3/4 and the Privacy modal disclose this; the About modal's "That's it." does not. The homework tip (`1095`, "they'll see that, not what you wrote") does not mention `viewed_at` either.

**Why it matters.** These are the sentences a client reads before consenting and before signing in. Signing in does share something: the fact and frequency of use. The old production Privacy modal said so ("How often you use Alo (not what you discuss)", `index.html:1409`); that disclosure did not survive into dev. Client-visible claims false on this build (S2). This is the client-side twin of R-B-11.

**Fix.** Say it once, consistently: "Your therapist can see that you've used Alo and when you opened or finished homework, never what you said", and drop "That's it" and "does not share anything".

**Regression.** R-B-11 (dashboard copy of the same screen).

### R-C-14 -- S2 -- "Nothing is being remembered" while history is saved (R-C.10, R-C.4)

**What.**

```
dev.html:3000-3003  if (!memoryGlobalEnabled) { showToast('Memory is already off — nothing is being remembered'); return; }   // "Make this conversation private"
dev.html:3020-3022  (same for "Start new private conversation")
dev.html:2879       privateBtn.style.display = memoryGlobalEnabled ? '' : 'none';
dev.html:2194       if (isPrivateSession) return;   // the only guard on saveMessage; memory setting not consulted
```

**Harness.** `memory_off_private_refused`: both private entry points were refused with that toast, the popover's private button was hidden, and the next message was written to `conversation_messages`.

**Why it matters.** A client who turned memory off is told nothing is kept, is denied the only control that keeps a conversation out of history, and their words are saved. S2.

**Fix.** Allow private sessions regardless of the memory setting, and change the toast to say history is still kept.

### R-C-15 -- S2 -- Private-session copy is false for a conversation made private midway (R-C.10, R-C.4)

**What.** "Make this conversation private" (`159-162`, `2996-3006`) switches the flag without touching the conversation's row or the turns already saved. The banner (`277`) says "Alo won't remember this conversation", the toast (`2967`) "this conversation won't be remembered", the tip (`2968`) "Nothing from this conversation goes into your history or memory", and the new-conversation confirm (`3070`) "This private conversation is not kept in your history."

**Harness.** `private_toggle_midconv`: two turns saved before the toggle; the row stays `is_private: false` with `turn_count: 2`; the copy above is shown.

**Why it matters.** Those earlier turns stay in the history list, and at the next conversation's first turn the bot summarizes them, because the row is not private (Init_State 225, 233; R-C-05). S2 claim.

**Fix.** Either scope the copy to "from now on" or make the toggle retroactive for the conversation (mark the row private and remove its earlier turns).

### R-C-16 -- S2 -- "Guests start fresh every visit." (R-C.10)

**What.** `dev.html:231`: "Memory and history are for signed-in accounts. Guests start fresh every visit." The webchat store in R-C-01 persists the guest's Botpress user and conversation in `localStorage`. `dev.html:3842-3856` sets no `storageLocation` and never restarts a guest's conversation, and the webchat fetches and renders the stored conversation on load. The bot's `conversation.conversationHistory` continues with it.

**Why it matters.** A returning guest sees their previous conversation, and Alo continues it; on a shared device the next guest sees it too. The sentence was written in the S4A-min demo copy pass. S2 claim.

**Fix.** For guests, set `storageLocation: 'sessionStorage'` or restart the conversation on load, or change the copy.

### R-C-17 -- S3 -- Previous account's page state survives a sign-out without reload (R-C.1, R-C.2)

SIGNED_OUT (`4189-4192`) can arrive without Log Out: a refresh-token failure, Log Out in another tab (supabase-js broadcasts auth events across tabs), or R-C-27. `resetToGuestUI()` (`1021-1050`) leaves `clientId`, `therapistLink`, `chatSettings`, `connectedTherapistName`, `sessionNonce` and `activeHomework` set. **Harness** `stale_after_signout_B_unconsented`: after sign-out, `clientId` and `therapistLink` were still A's, and a pending auth-bridge retry re-sent A's `clientId` to Botpress after the sign-out. B then signed in with an unconsented link and ticked consent. The PATCH went to `therapist_clients?client_id=eq.<A>` (`uid = clientId` at `1379`), changed nothing, and the re-read returned nothing, so B saw the constant error and cannot consent in that tab until a reload. With a broader SELECT policy the re-read would have returned A's consented row and reported success, but `loadConnectedState()` re-reads with B's authenticated id and re-gates, so nothing unlocks either way. `stale_after_signout_B_nolink`: B (no link) was offered "Share with therapist" on B's own entry, with the confirm naming A's therapist (`3427`). Fix: clear every per-account global in the SIGNED_OUT path, or reload on SIGNED_OUT.

### R-C-18 -- S3 -- No CSP on production; dev CSP does not contain script injection (R-C.1)

`index.html` has no Content-Security-Policy meta tag (its head, lines 1-46, and the diff's first hunk `9a10,21`). GitHub Pages sends no CSP, `X-Frame-Options` or `Referrer-Policy` header (`curl -I https://alowen.ai/`). `dev.html:10-21` has a CSP, but `script-src` includes `'unsafe-inline'` (injected handlers ran in R-C-03/R-C-09) and `https://cdn.jsdelivr.net` (any npm package). `connect-src https://*.botpress.cloud` and `img-src https://*.supabase.co` are open to any tenant, so an injected script can still send data out. With no `frame-ancestors`, which a meta tag cannot set, any site can frame the app over its consent, share and delete buttons. D34 rules localStorage plus CSP as the A7-D9 posture; on the client's production build (the demo URL, D35 section 7) the CSP half is absent. Fix: promote the CSP, and before relying on it remove `'unsafe-inline'` for scripts (inline handlers exist throughout) and narrow the host lists; framing protection needs a header, which GitHub Pages cannot send.

### R-C-19 -- S3 -- Failed `?t=` with an existing session leaves the page stuck (R-C.1)

`dev.html:4207-4216`: after a failed exchange, `if (!tokenSession) _aloInitBotpress(); return;`. With a session already stored, neither `_aloInitBotpress()` nor `loadConnectedState()` runs, and the 15-second fallback is armed only inside `_aloInitBotpress()`. **Harness** `real_token_fail_existing_session` (real library): constant toast, then a guest-looking header with Sign In while a session exists, "Loading Alo..." with no end, Botpress `init` 0, link reads 0. A therapist whose browser already holds the test client's session and who opens an expired or already-used link hits this, as does every attempt if the exchange itself fails (for example the D32 CORS redeploy question in R-B section 6). Reloading recovers, because `t` is already stripped. Fix: on failure, fall through to the normal `getSession()` path instead of returning.

### R-C-20 -- S3 -- Password reset never reaches "Set New Password" (R-C.1)

`4183-4185`: `if (window.location.hash.includes('type=recovery')) { setTimeout(... showSetNewPasswordModal() ...) }`. The library clears the fragment inside `_getSessionFromURL()` (`window.location.hash = ""`) before it notifies `PASSWORD_RECOVERY` from a `setTimeout`, so the check can never be true. **Harness** `real_recovery_modal`: the recovery session was saved and the page loaded connected; no "Set New Password" modal. The reset email lands a signed-in user with no way to set a password, and the next forgotten-password cycle repeats. `redirectTo: window.location.origin` (`1631`) and `emailRedirectTo` (`1550`) also send dev.html users to production. Fix: capture `type=recovery` from the URL before `createClient()` runs, or use the event alone.

### R-C-21 -- S3 -- Signed-in accounts with no link are anonymous to the bot until "New conversation" (R-C.3, R-C.10)

`showLoggedInNoConnection()` (`814-849`) starts the chat and loads memory settings but sends no identity; `sendAuthBridge()` runs only past the gate (`2103`, `2109`) and after `startNewConversation()` (`3105`). For a fresh unlinked account the bot sees a guest: no memory context, no journal context, no summaries generated. Shown to that account meanwhile: the memory card "Alo remembers context" (`304`), About "When memory is on, Alo also keeps brief summaries..." (`229`), the journal empty state "so Alo picks up where you left off" (`378`, `3209`), and the login modal's "let Alo remember what you've discussed" (`1497`). After the first "New conversation" the Botpress user carries the id permanently (with R-C-01's consequences). Not the demo path (demo clients are linked), hence S3. Fix: send the identity from the no-link path too, once R-C-10's verified handoff exists.

### R-C-22 -- S3 -- Message content kept in plaintext local queues (R-C.4, R-C.5)

`4061-4065` appends `{role, content, msgId, ts}` to `localStorage['alo_unsent_messages']` (last 20) when persistence fails twice. `4015-4019` stores the raw Botpress message object in `alo_dropped_messages` (last 20) for any format the extractor misses, including during private sessions. Nothing reads either key back (S4A-min changed the toast accordingly), and Log Out clears neither, nor `alo_conv_*` (`2187`). The content outlives deletion ("Clear unpinned", "Delete conversation") and survives into the next person's session on that browser, and the Privacy modal's "All stored data is encrypted at rest" does not describe it. Fix: stop writing content to these keys (store ids only) and clear all `alo_*` keys on Log Out.

### R-C-23 -- S3 -- A7-C3 queue attributes a pending write to whatever conversation is current when it runs (R-C.9)

`2202-2211`: the queued closure builds `insertData` with `conversation_id: currentSupabaseConvId` and `turn_number: ++persistenceTurnCounter` when it executes, not when `saveMessage()` was called (the only check at call time is `2195`). `startNewConversation()` calls `resetPersistenceState()` (`3084`, `2240-2244`) without draining the queue. **Harness** `c3_queue_reset_race`: the user message's write was in flight; Alo's reply was queued behind it; a reset followed. The reply was written with `conversation_id: null, turn_number: 1`. A real `NOT NULL`/foreign key rejects it and the error is console-only (`2221-2227`), so the message silently disappears from history (A7-C2 class). If the next conversation's row already exists, the message lands in the wrong conversation. The window is one write's round trip; the no-confirm paths ("Start new private conversation", "Bring this to Alo") make it easiest to hit. D35 section 8 puts adversarial race verification of A7-C3/C4 in Gate B at severity one; this is one concrete race. Fix: capture the conversation id and turn number at call time, and await the queue before resetting.

### R-C-24 -- S3 -- "Clear unpinned conversations" count and scope differ (R-C.5)

`2731-2745` counts `allThreads` (at most the fetched batches, 50 at a time, and already minus locally removed rows) for "This will delete N unpinned conversation(s)". `2762-2765` marks `source_expired` only for those ids. `2767` deletes every unpinned row server-side. **Harness** `delete_zero_rows`: the confirm said "1 unpinned conversation" while the DELETE filter matched 2. With more than 50 unpinned conversations, the client is told a smaller number, and summaries for the unloaded conversations are not marked (depending on the foreign key they are orphaned or deleted, contradicting "Alo will still remember themes from recent sessions"). Fix: count and mark server-side with the same filter the DELETE uses.

### R-C-25 -- S3 -- "Bring this to Alo" ends a private session without asking (R-C.6, R-C.4)

`3620-3641`: `startNewConversation(true)` then `sendMessage(entryContent)`; `startNewConversation` ends private mode first (`3081-3083`). The entry is sent into a normal conversation, saved to history and later summarized. The only signals are two toasts ("Private session ended", "Starting a new conversation..."). The action is the client's, but the private state is dropped silently. Fix: keep private state across this action, or ask first.

### R-C-26 -- S4 -- `?t=` stripped after third-party scripts ran (R-C.1)

The strip is synchronous and the first statement of DOMContentLoaded (`3813`), before any of the file's own async work, as the comment says. It is not before every script. Botpress `inject.js` (`50`, parser-blocking, third-party) and the supabase-js UMD (`442`, plus `createClient` at `450`, which reads `window.location.href`) execute with `t` in the URL. **Harness** `token_strip_order`: the first head script and the inject.js stand-in both saw `t=`. There is no `<meta name="referrer">` and no header, so the browser default applies: cross-origin requests made during parsing send only the origin, and same-origin requests (`dev.css`, `manifest.json`, icons) send the full URL to the same host. The residual risk is small: the token is single-use, expires in 60 s and is consumed in the same load, and anything that can read the URL can also read the session the exchange creates. Fix: move the strip into an inline script at the top of `<head>` and add `<meta name="referrer" content="no-referrer">`.

### R-C-27 -- S4 -- A crafted link signs the client out (R-C.1)

Same library path as R-C-06. A URL whose fragment or query contains `error_description` makes `_initialize()` call `_removeSession()`. **Harness** `real_error_description_logout`: the stored session was removed and the guest page loaded. The server-side refresh token is not revoked. Nuisance only, but it is also a no-reload route into R-C-17 for other open tabs. Fix: as R-C-06.

### R-C-28 -- S4 -- Duplicate connected-path side effects on modal sign-in (R-C.2)

The explicit call (`1599` / `1597`) and the SIGNED_IN listener (`4188`) both pass the gate. **Harness** `double_entry_consented`: two extra `session_metadata` rows. Each run generates its own nonce, and the last `updateUser` wins. The real library on a plain page load produced one entry only (`real_pageload_double_entry`). Known (S4A-min section 9); no gate impact. Fix: a single in-flight promise for `loadConnectedState()`.

### R-C-29 -- S4 -- Invite code unencoded in the PostgREST URL (R-C.7)

`1451`: `therapist_clients?invite_code=eq.${inviteCode}&status=eq.pending`. A `#` in the typed or deep-linked code truncates the URL and drops the status filter; `&` adds parameters. PostgREST ANDs filters, so this cannot widen beyond the typed code. Under the Phase 1 claim policy (`status = 'pending' and client_id is null`) the PATCH on a non-pending row matches nothing, but the toast still says "Connected successfully!" (R-C-08). Fix: `encodeURIComponent(inviteCode)`.

### R-C-30 -- S4 -- Self-XSS in the wrong-password message (R-C.7)

`1566`: `onclick="handleForgotPassword(\'' + escAttr(email) + '\')"`. `escAttr()` turns `'` into `&#39;`, which the HTML parser decodes back into `'` before the handler's JavaScript is compiled, so a quote in the typed email closes the string. The input is the user's own. Fix: attach the listener in script with the email captured in a closure.

### R-C-31 -- S4 -- Consent failure copy can be untrue (R-C.2)

`1368-1369` "Something didn't go through. Nothing was changed. Try again in a moment." is shown for every failure, including a successful PATCH followed by a failed re-read (`1391-1394` throws on a network error). The server then has `consent_acknowledged_at`, and the retry overwrites it with a later time. The copy is mandated verbatim by Brief 1a-min (D31 pattern); noted for the record. Fix, if the copy may change: "Something didn't go through. Try again in a moment."

### R-C-32 -- S4 -- Stray files and the dev manifest on the production origin (R-C.9)

`backup.html` (tracked) serves `text/html` at `https://alowen.ai/backup.html`: a bare Botpress embed with the same webchat client id and no CSP. It shares the stored Botpress user (R-C-01) and its user data with the real app. `padding: 8px 12px;` (tracked, 103 KB) is a February copy of the app, served as `application/octet-stream`, so it is not rendered. `manifest.json:5` has `"start_url": "./dev.html"` and is linked only from `dev.html:30`; a promotion that copies the head of dev.html ships an installable production app that opens dev (the same hazard as R-B-38). Fix: delete both stray files; point `start_url` at `./` at promotion.

---

## 3. Angle-by-angle answers

### R-C.1 Session and token handling

- **Where the session lives.** The full GoTrue session JSON (access token, refresh token, user) in `localStorage['alo_client_session']`, managed by the supabase-js SDK (`450-458`). The brief's `alo_session` is the dashboard's key. No in-memory copy of the token is kept by the page; `api()` asks the SDK for it on every call (`1910`).
- **Lifetime and refresh.** `persistSession: true`, `autoRefreshToken: true`. The library checks every 30 s and refreshes near expiry; a stored expired session is refreshed on load. The access-token lifetime is the project's JWT expiry (not visible here). There is no idle or absolute timeout in the app. The session lasts until Log Out or a non-retryable refresh error.
- **Log Out.** `signOut()` defaults to `scope: "global"` in this library version, so the refresh token is revoked server-side (unlike the dashboard, R-B-21), then the page reloads. Botpress identity and local residue are not cleared (R-C-01, R-C-22).
- **Refresh failure: closed or stale.** Network-class failures keep the session and retry. A rejected refresh token makes the library remove the session and emit SIGNED_OUT. The listener then resets the header to guest, but the per-account globals, the open chat and the Botpress identity remain: it fails **stale**, not closed (R-C-17, R-C-01). Messages typed in that state still enter the persistence path (the stale `clientId` passes the guest check at `3993`) and are rejected under RLS without a session; the failure is console-only.
- **`?t=` strip.** Synchronous, first in DOMContentLoaded (`3813`), before `_aloHandleInviteParam()` and before every await in the file. Not before all scripts: inject.js and supabase-js run earlier (R-C-26, S4).
- **Single use and expiry enforced server-side.** Yes, in the repo source. `exchange-client-token/index.ts` consumes the token with one conditional UPDATE (`eq token_hash`, `used_at is null`, `expires_at > now`, returning `client_auth_id`), so not-found, used, expired and lost-race all return the same 401. The token is 32 CSPRNG bytes with only its SHA-256 stored (`_shared/tokens.ts`), and expiry is 60 s from mint (per R-B's reading of `open-as-client`). The CORS allowlist is `alowen.ai`, `www.alowen.ai`, `dashboard.alowen.ai`. Whether the deployed function matches the repo is R-A's to confirm (section 7).
- **Failure copy.** One bare `catch` (`3770-3777`) covers a rejected fetch, non-2xx, malformed JSON, a missing `token_hash`, and a `verifyOtp` error, and shows only `ALO_TOKEN_EXCHANGE_FAILURE_MESSAGE`. Nothing is logged or interpolated. **No issue** with the copy (harness `token_strip_order`: exactly that toast). The surrounding flow has R-C-19.
- **CSP.** `dev.html:10-21`:
  `default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.botpress.cloud https://cdn.jsdelivr.net https://files.bpcontent.cloud; style-src 'self' 'unsafe-inline' https://cdn.botpress.cloud https://fonts.googleapis.com; img-src 'self' data: blob: https://files.bpcontent.cloud https://*.supabase.co; connect-src 'self' https://lelsdezstbnzyxvsvbyx.supabase.co https://*.botpress.cloud wss://*.botpress.cloud https://files.bpcontent.cloud; frame-src 'self' https://cdn.botpress.cloud; font-src 'self' data: https://fonts.gstatic.com https://fonts.googleapis.com; media-src 'self' data:; object-src 'none'; base-uri 'self'`.
  **The production client (`index.html`) has no CSP at all**, and GitHub Pages adds none. The A7-D9 mitigation's precondition is absent on the build clients use today, and where present it does not stop inline injection (R-C-18).
- **Other.** URL-borne sessions (R-C-06), sign-out via a crafted link (R-C-27), and the reset flow (R-C-20).

### R-C.2 Consent gate -- adversarial

Path enumeration is in section 4. Each attempt the brief lists:

- **Direct calls from the console.** Everything is reachable: `_aloInitBotpress()`, `showConnectedUI()`, assigning `therapistLink`, `sendAuthBridge()`, `window.botpress.sendEvent(...)`. The gate is a page control; neither RLS nor the bot reads `consent_acknowledged_at`. A client can therefore skip their own screens, and can PATCH their own row's `consent_acknowledged_at` to any timestamp (`client_update_own_link`, RLS v1.2), which limits its value as evidence. No third party gains anything from this that R-C-10 does not already give. **No additional finding** beyond recording that consent is not enforced server-side (Gate B on the parked branch).
- **Racing SIGNED_IN against the explicit call.** Both entries pass through the same gate. For an unconsented row the `alreadyHolding` guard (`2036-2039`) keeps the screens stable (S4A-min verified). For a consented row, side effects are duplicated (R-C-28). One more ordering, reasoned from the code and not exercised: if consent completes while a second entry's link read is still in flight, that entry sees the pre-consent row and re-opens the screens at step 1 although consent is recorded, so the client consents again. It fails closed (S4, not listed separately).
- **Stale `therapistLink` from a previous account in the same tab.** Reachable through SIGNED_OUT without reload: the consent write uses the stale id and cannot succeed until a reload; the stale link offers journal sharing to an unlinked account (R-C-17).
- **A row with `client_id` set but `status` not active.** The link query filters `status=eq.active` (`1973`), so such a row is invisible to the page: the account is treated as unlinked (`1975-2027`), gets the chat, and sends no identity. No therapist feature unlocks. **No issue on this build.** The parked branch's "pending until consent" design would land in this branch too, which is correct as long as nothing therapist-visible keys on that row.
- **A second tab.** Consent completed in tab B does not unlock tab A until reload (fails closed). A connected tab A stays connected if consent is later cleared server-side (stale until reload). Both tabs share one Botpress user, so the private flag set in one applies to the other's next conversation (R-C.4 note). **No gate bypass.**
- **A second link (found in review).** Bypass (R-C-02, S1).
- **Post-write re-read satisfied by a row the user does not own.** Not guaranteed as written: `uid = clientId || getUser()` (`1379-1383`) can be stale. With row-scoped SELECT the re-read is empty and the gate stays closed (harness). With a broader SELECT a foreign consented row would satisfy it, but `loadConnectedState()` (`1411`) re-reads with the authenticated id and re-gates. It is bounded either way (R-C-17).
- **`alo_consent_acknowledged_fallback`.** 0 occurrences in `dev.html` and `index.html`. Every `localStorage`/`sessionStorage` key the page writes: `alo_theme`, `alo_tip_<key>_seen`, `alo_pending_invite`, `alo_conv_<botpress id>`, `alo_unsent_messages`, `alo_dropped_messages`, `alo_privacy_bar_dismissed`, `alo_memory_onboard_ask`, `alo_memory_onboard_done`, `alo_memory_onboard_dismiss_count`, `alo_memory_prompt_dismissed`, `alo_install_dismissed`, `alo_ios_install_card_shown`; session: `alo_connect_prompt_dismissed`, `alo_guest_benefits_dismissed`, `alo_active_tab`; SDK-managed: `alo_client_session`, `bp-webchat-<webchat client id>`, `bp-unread-message-count`. **None stores consent.** No issue.

### R-C.3 Identity handoff to the bot (A-21, client side)

| Call | Line | What the client asserts | Where each value comes from |
|---|---|---|---|
| `botpress.init` | 3838-3857 | `botId`, webchat `clientId` (public), selector, configuration | Constants. No user identity. `conversationHistory: false` is not a v3.3 configuration key and is ignored |
| `updateUser` | 2090-2097 | `data.sessionNonce`, `data.clientId`, `data.homeworkActive`, `data.timeZone` | nonce: `crypto.randomUUID()` (2077), written to `session_metadata` with the client's JWT first; clientId: `user.id` from `supabase.auth.getUser()` (server-validated JWT, 2044); homework: therapist-authored title/type/goal (2087-2089), **not read by the bot**; timezone: browser |
| `sendEvent` | 2254-2257 | `{bp_event: 'alo_auth_bridge_v1', clientId}` | the `clientId` global (may be stale, R-C-17) |
| `updateUser` | 2267-2270 | `{userKey: clientId, data: {clientId}}` | as above; after init the webchat's `updateUser` keeps only `name`, `pictureUrl`, `data`, so `userKey` is dropped. Before init the inject.js stub merges the whole object, and the v3.3 iframe code would take a pre-set `user.userKey` as the Botpress user key, so if this call lands before the webchat script has read its initial user (slow CDN load), the chat would try to connect with the Supabase id as its key and fail. Read from the bundle, not exercised |
| `updateUser` | 2975-2977, 2988-2990 | `data.privateSession: 'true'` / `'false'` | the in-memory flag; unconfirmed (R-C-07) |
| `restartConversation` | 3091 | -- | -- |
| `sendMessage` | 3634 | journal entry text | "Bring this to Alo" |

- **Memory preference** is never sent; the bot reads `client_settings` itself. **Therapist link** is never sent; the bot reads `therapist_clients` itself.
- **What a hostile page script or the console can assert:** any `data` key, including any `clientId`, `privateSession: 'false'`, a `timeZone`, and `journalInject`, which the bot copies into the LLM context (Init_State 677-684; this client never sets it). Any `sendEvent` payload. Nothing client-side prevents or signs any of this: the SDK is a global, and the only binding (the nonce) is not verified (R-C-10). Because the webchat iframe is same-origin, a page script can also read the Botpress user key from `localStorage` and use the Chat API as that user from anywhere, listing that client's Botpress conversations.
- **Supabase tokens to Botpress:** none. No Botpress call carries the access or refresh token; they appear only in `api()`'s headers and in SDK storage. Caveat: `webchat.js` is third-party code served from an unpinned `v3.3` path and runs in this origin, where it could read `alo_client_session`; the bundle read here does not.

### R-C.4 Private session and history OFF

- **Lifecycle.** `startPrivateSession()` sets the in-memory flag, updates the UI, then fires `updateUser` without awaiting it (R-C-07). `endPrivateSession()` does the reverse. `startNewConversation()` ends private mode before `restartConversation()` (`3081-3091`), so `'false'` is sent while the private conversation is still current. The exported bot reads the flag only at turn 1 of the next conversation, so nothing results on this revision; that is an ordering hazard if a future bot reads it at conversation end. The flag is lost on reload while the Botpress user keeps `'true'`: from then on the UI says memory is on and the bot skips memory in every future conversation (safe direction, part of R-C-04's reload path). "Start new private conversation" restarts first, then sets the flag.
- **`client_messages`** (messages to the therapist) are user-initiated and unaffected by private mode. **No issue.**
- **`conversations`:** a row is written for every private conversation and listed (R-C-04).
- **`conversation_messages`:** nothing during the private session; after a reload, the rest of the conversation (R-C-04).
- **Journal:** the client sends nothing that asks for a journal save; the only client input is the conversation itself plus the flag. On the exported bot `JOURNAL_SAVE` ignores the flag (A-20 open), so any Alo-generated save during a private session is written, and delivery of the flag is unconfirmed (R-C-07).
- **Memory summaries:** generated only from stored transcripts of non-private rows. A conversation made private midway keeps its earlier turns summarizable (R-C-15). Memory off does not stop history (R-C-14).
- **Botpress conversation:** retained on the platform and restored in the window after a reload or on the next visit (R-C-01, R-C-16). Not deleted on this build (2.5b is Gate B). **The copy does not say so on the private-session surfaces:** the banner (`277`), toast (`2967`), tip (`2968`) and confirm (`3070`) are silent; only About (`228`) and the Privacy modal (`4142`) mention platform deletion, and only in the context of deleting conversations. Misleading by omission (S3 class, not listed separately; the D35 section 6 one-pager should cover it).
- **Local:** `alo_dropped_messages` can hold private-session message objects (R-C-22).

### R-C.5 Deletion and "forget"

| Action | Request | Response means | Verified? | Reaches | Claim |
|---|---|---|---|---|---|
| Clear all memories | DELETE `conversation_summaries?client_id=eq.<uid>` (2948) | 204 whether 0 or N rows | No | Supabase only; bot regenerates (R-C-05) | "permanently deletes all conversation summaries Alo has stored. Future conversations will start fresh" -- FALSE |
| Delete conversation | DELETE summaries by conversation, DELETE conversation (2697-2698) | 204 each; messages depend on an unverified cascade | No | Supabase only | "removes the conversation and Alo's memory of it from your Alo account" -- UNVERIFIABLE (policy, cascade); platform copy correct |
| Clear unpinned | PATCH summaries `source_expired` (loaded ids), DELETE all unpinned conversations (2762-2767) | 204 each | No | Supabase only | count can be wrong (R-C-24); "Alo will still remember themes from recent sessions" -- TRUE (the bot loads `source_expired` summaries, Init_State 512-517) |
| Delete journal entry | DELETE `journal_entries?id=eq.<id>` (3544) | 204 | No (the list refresh would show a survivor) | Supabase only | "This can't be undone." |
| Ask Alo to forget | the chat message goes through Botpress; the bot DELETEs summaries with the service key (Check_And_Route 40-43, 210-213) and feeds the result into its reply | the bot knows whether its call threw | bot-side only | Supabase summaries only; transcripts untouched; regenerated for the latest 3 conversations (R-C-05) | "ask Alo to forget a specific topic" -- FALSE for recent conversations |

**Silent non-deletion:** R-C-05 (S1), and conditionally every row of R-C-08.
**Only Supabase:** every deletion above. None reaches Botpress.
**Claims implying platform-side deletion:** none. The delete confirm says "from your Alo account", and About/Privacy say platform deletion "is coming and isn't in place yet". Correct as far as it goes; see R-C.4 for the private-session silence.

### R-C.6 Journal privacy

- **Writes and reads.** Create with `shared_with_therapist: false` (3255-3263). Share and revoke PATCH by entry id (3605, 3585). List read by `client_id` (3294). The badge shows "Shared with <therapist>" (3371-3373).
- **Share to a therapist the client is not linked to.** The client cannot choose a therapist; the flag is a boolean. Who can read a shared entry is RLS's decision (R-B-15: any therapist whose policy reaches the client's rows, including a later one). The page offers the toggle only when `therapistLink && chatSettings.allow_journal_sharing !== false` (3427), which is client-side only, and the stale-link case offers it to an unlinked account (R-C-17). `allow_journal_sharing = false` hides the toggle but does not revoke earlier shares.
- **Unsharing.** Works only if the UPDATE matches; it is not verified, and the harness showed "Share revoked" with the server row still shared (R-C-08).
- **Journal content in Botpress payloads.** Yes, twice. (1) "Bring this to Alo" sends the full entry as a chat message (3634), a client action that silently ends private mode (R-C-25). (2) The bot loads the five most recent entries, up to 400 characters each, into the LLM context at the first turn when memory is on and the session is not private (Init_State 608-665). That is a server-side read, not a client payload, and is disclosed ("Alo may reference your journal entries"). The homework payload carries no journal data. The local safety-keyword check (3650-3684) makes no network call. **No issue** there.

### R-C.7 Output escaping and injection

| Source | Sink | Escaped? | Result |
|---|---|---|---|
| Bot replies | Botpress webchat bubbles (same-origin iframe) | react-markdown without raw HTML: raw HTML becomes literal text; URLs pass react-markdown's default transform (`tel:` also allowed); tables/lists/links as React elements | **No issue** found in the bundle read (not exercised live). Any HTML injection there would be same-origin |
| Bot text stored in history | transcript viewer (2500), share text (2596) | `esc()` / text | Safe |
| Alo-generated journal entries | cards (3381), detail (3437-3438), edit (3511) | `esc()` | Safe |
| Therapist display name | homework "From" (1077), message modal (1737-1739), share confirm (3598 via 797) | **no** | R-C-09 (S2) |
| Therapist display name | badge (877), journal badge (3372), tip (1095, `textContent`) | yes | Safe |
| Homework title/goal/type | homework card (1078, 1084, 1083) | **no** | R-C-09 (S2) |
| Therapist's label for the client / client's own name | badge (880) | yes | Safe |
| Same name, read back via `textContent` | name edit `value="..."` (974) | **no** (attribute) | R-C-03 (S1) |
| Invite text `?invite=` | input `.value` property (3796) | n/a (property) | Safe |
| Invite code | PostgREST URL (1451) | not URL-encoded | R-C-29 (S4) |
| User email | forgot-password `value` (1617) | `escAttr` | Safe |
| User email | wrong-password `onclick` string (1566) | `escAttr` in a JS string context | R-C-30 (S4, self) |
| Conversation titles | list (2358, 2365, 2369), transcript title (2538), rename `value` (2643) | `escAttr` | Safe |
| Journal text | all sites | `esc()` | Safe |
| Database ids | `data-*`/`id` attributes and selectors (1074-1087, 2360-2372, 3375, 3447, 3533) | raw | Safe while those columns are `uuid` (assumed; the schema is not in any repo) |
| Static strings | `createModal` titles and labels (713, 704-705) | raw | Safe (no dynamic input except R-C-09's) |

### R-C.8 Guest surface

- **What a guest can cause server-side.** Through the bot: `crisis_events` rows with `client_id` null, carrying up to 200 characters of what was typed (R-C-12; A-15). Nothing else on the exported revision: `JOURNAL_SAVE`, memory load, summary generation and "forget" all require a resolved client id. The exception is a stale id in the browser's Botpress user (R-C-01) or a console-asserted one (R-C-10), which turns "guest" writes into writes on a real client's journal and alert record. Through the page: no Supabase write while `clientId` is null (the message handler returns at 3993-3996). The login modal's `signUp` fallback (1541-1552) can create an auth user if GoTrue signups are enabled (not verifiable here); the reduced trigger v3 hard-codes `role = 'individual'` and ignores metadata, so the `role` the page sends cannot escalate (`alo-supabase` migration `20260908150000`).
- **Rate limits.** None in the page, the bot node, or any Supabase object in the repos. The webchat client id is public (3840), so the Chat API can be scripted without the page. Botpress-side limits are unknown.
- **Recommendation (smallest change that stops guest writes reaching therapist-visible tables without removing guest chat).** Leave the in-chat 988 response exactly as it is and change who can see the row. In Safety_Check, write `crisis_events` only when identity came from the verified path (the nonce found in `session_metadata` for that client id, R-C-10); for an unidentified user, log the event to the Botpress trace (or an operations-only table with no therapist SELECT policy) and do not store the typed text. In the database, make the therapist SELECT predicate on `crisis_events` require `client_id in (<therapist's active or pending links>)`, which excludes null rows (R-B-07's rule), so the dashboard stops receiving guest events even if the bot condition regresses. That is one bot condition and one policy predicate; no client change.

### R-C.9 A7-C status and parity

Section 5.

### R-C.10 Claims-freeze spot check (item 4.25)

Every client-visible sentence on the merged build that claims something about privacy, memory, storage, or what the therapist sees. The S4A-min D1 list was the starting point; rows marked "missed" were marked true or left unchanged there.

| Where | Sentence (quoted) | Verdict | Note |
|---|---|---|---|
| og:description `54` | "A private space to process your thoughts and emotions. Your therapist recommended Alowen as a companion between sessions." | TRUE (private) / UNVERIFIABLE (recommended) | Link preview; "recommended" is not a build fact |
| Menu memory detail `177` | "Alo keeps short summaries of recent conversations for continuity. Your therapist cannot see this. You can start a private session anytime from the eye icon." | TRUE (linked) / FALSE (unlinked until first new conversation) | R-C-21; therapist visibility per RLS v1.2 SELECT policy |
| About `214` | "Your conversations are private — always. Your therapist never sees what you say to Alo." | TRUE (as designed) | Breakable by R-C-03/R-C-09/R-C-06 |
| About `215` | "...they can see general patterns across your sessions and whether you've completed any reflections they've assigned. That's it. They aren't notified in real time..." | **FALSE** (missed) | "That's it" omits crisis alerts, homework viewed times, shared entries, messages. R-C-13. "Not notified in real time": TRUE (no crisis email yet, plan 5.4) |
| About `216` | "Guest conversations aren't saved to an account." | TRUE | Stored on the platform and restored locally (R-C-16) |
| About `216` | "...start a private session (nothing from it goes into your history or memory), or ask Alo to forget a specific topic." | **FALSE** / **FALSE** | R-C-04, R-C-15; R-C-05 (regenerated) |
| About `217`, `236` | "Journal entries are private by default — your therapist can't see them unless you choose to share a specific entry." / "Your therapist can only see entries you explicitly share — and you can revoke sharing at any time." | TRUE (UI) / UNVERIFIABLE (revoke) | Revoke unverified (R-C-08); multi-therapist scope R-B-15 |
| About `237` | "Alo may reference your journal entries naturally in conversation ... but never comments on the act of journaling itself." | TRUE (bot loads entries with that instruction, Init_State 631-643) | Bot revision of Sep 8 |
| About crisis `223` | "If you share something that sounds like a crisis, Alo will pause and share these resources with you directly." | TRUE | Therapist alert not mentioned here (R-C-13) |
| About memory `228` | "When you're signed in, Alo keeps your conversation history so you can review it, and you can delete any conversation from your Alo account at any time. Deletion from the chat platform Alo runs on is coming and isn't in place yet." | TRUE (kept) / UNVERIFIABLE (delete) | R-C-08 |
| About memory `229` | "When memory is on, Alo also keeps brief summaries of past conversations ... Memory is on by default and you can turn it off any time." | TRUE (linked) | Unlinked: R-C-21 |
| About memory `230` | "You're always in control: turn memory off, go private for a session, or ask Alo to forget something." | **FALSE** (forget, private) | R-C-05, R-C-04 |
| About memory `231` | "Memory and history are for signed-in accounts. Guests start fresh every visit." | TRUE / **FALSE** | R-C-16 |
| Memory popover `255` | "Alo uses short summaries from recent conversations for continuity. Your therapist cannot see this." | TRUE | -- |
| Private banner `277` | "Private session — Alo won't remember this conversation" | **FALSE** (missed) | R-C-15, R-C-04, R-C-07 |
| Memory card `304` | "Alo keeps brief summaries of past conversations so you don't have to re-explain. Your therapist can't see any of this. You can turn this off any time in Settings." | TRUE (linked) | Unlinked: R-C-21; "Settings" is the Memory menu section |
| Privacy bar `348` | "Your conversations with Alo are private. Your therapist cannot see what you discuss here." | TRUE | As `214` |
| Journal empty `378` / `3209` | "A private place to hold your thoughts, so Alo picks up where you left off." | FALSE for unlinked (missed) | R-C-21 (this variant is shown only when unlinked) |
| Journal empty `3207` | "A private place to catch what matters between sessions." | TRUE | -- |
| Connect prompt `853` | "...link your account to see homework and send them messages between sessions." | TRUE | -- |
| Homework tip `1095` | "<therapist> assigned this. Mark it done when you're ready — they'll see that, not what you wrote." | Misleading by omission | `viewed_at` (R-C-13) |
| Onboarding 2 `1243` | "Your conversations with Alo stay between you and Alo. Your therapist can't read them." | TRUE | -- |
| Onboarding 2 `1243` | "Nothing is shared unless you share it." | **FALSE** (missed) | R-C-13; R-B-11 |
| Onboarding 3 `1248`, consent `1341`, Privacy `4160` | "...it will let your therapist know something happened. Not what you said." / "...never what you said." | TRUE (display) / **FALSE (storage)** until A-15 lands | Bot writes a 200-character excerpt (Safety_Check 249) |
| Consent `1341` | "Your conversations are yours — nothing is shared unless you choose to." | **FALSE** (missed) | R-C-13 |
| Read-only screen 4 `1354` | "Before your first conversation, you confirmed: ..." | TRUE for gated clients | Not true for R-C-02's second link |
| Connect modal `1419-1420` | "They can send you exercises, and you can message them anytime." / "Your conversations with Alo are between you and Alo — your therapist never sees them." | TRUE / TRUE | -- |
| Login modal `1497` | "Create an account to save your conversations and let Alo remember what you've discussed." | UNVERIFIABLE (self-signup) / FALSE for unlinked | S4A-min flagged; R-C-21 |
| Login modal `1498` | "Your conversations stay private. Signing in does not share anything." | TRUE / **FALSE** (missed) | R-C-13 |
| Message modal `1739` | "<therapist> will see this message in their dashboard." | TRUE | -- |
| Transcript share `2510` | "N messages · Nothing is sent until you choose where." | TRUE | Local copy/share only |
| Delete confirm `2679` | "This removes the conversation and Alo's memory of it from your Alo account. This can't be undone." | UNVERIFIABLE | R-C-08 (unverified), R-C-05 (summary delete) |
| Clear confirm `2739-2745` | "This will delete N unpinned conversation(s) from your Alo account. ... Alo will still remember themes from recent sessions." | N can be FALSE / TRUE | R-C-24 |
| Memory toast/tip `2918` | "Alo remembers a little between conversations so you don't have to start over. You can clear it anytime." | **FALSE** (clear) | R-C-05 |
| Clear memories `2933-2934` | "This permanently deletes all conversation summaries Alo has stored. Future conversations will start fresh with no context from past sessions." | **FALSE** | R-C-05 |
| Private toast/tip `2967-2968` | "Private session — this conversation won't be remembered" / "Nothing from this conversation goes into your history or memory." | **FALSE** | R-C-04, R-C-15, R-C-07 |
| Memory-off toast `3001`, `3021` | "Memory is already off — nothing is being remembered" | **FALSE** (missed) | R-C-14 |
| New-conversation confirm `3070-3071` | "This private conversation is not kept in your history." / "Your current conversation is saved in your history." | **FALSE** / TRUE | R-C-04 |
| Journal tip `3160` | "Entries stay private unless you choose to share one." | TRUE (UI) | -- |
| Share confirm `3598` | "<therapist> will be able to see this entry. You can revoke anytime." | TRUE / UNVERIFIABLE (revoke) | R-C-08; R-B-15 |
| Journal safety `3649` (comment) / banner | no privacy claim in the UI; code comment "No data sent" | TRUE | No network call |
| Persistence toast `4066` | "This message couldn't be saved to your history." | TRUE | Content kept locally (R-C-22) |
| Token failure `3736` | "That link didn't work — ask your therapist for a new one." | TRUE | -- |
| Consent failure `1369` | "Something didn't go through. Nothing was changed. Try again in a moment." | Usually TRUE | R-C-31 |
| Terms `4115` | "Your therapist does not see your conversations with Alo" | TRUE | -- |
| Privacy "What we store" `4132-4136` | Account info; connection; homework completion; messages to therapist; journal entries | Incomplete (missed) | Also stored: transcripts (next section says so), summaries, session activity, crisis records with excerpts, profile name |
| Privacy `4141` | "If you have an account, conversations are saved so Alo can provide continuity" | TRUE | -- |
| Privacy `4142` | "You can delete any conversation from your Alo account at any time from the sidebar. Deletion from the chat platform Alo runs on is coming and is not yet in place" | UNVERIFIABLE / TRUE | R-C-08 |
| Privacy `4143` | "You can turn off memory in settings — Alo will treat each chat as new" | TRUE | Bot skips memory and journal context when off; history still saved (R-C-14) |
| Privacy `4144` | "Guest conversations (no account) are not saved to an account" | TRUE | -- |
| Privacy `4145`, `4159` | "Your therapist cannot access your Alo conversations" / "never sees" | TRUE (as designed) | As `214` |
| Privacy `4146` | "Conversations are not used for training, analytics, or advertising" | UNVERIFIABLE | The Sep 8 export still contains the two improvement hooks; the truth table records them uninstalled Sep 13 |
| Privacy `4151-4153` | journal private by default / you choose / revoke anytime | TRUE / TRUE / UNVERIFIABLE | R-C-08 |
| Privacy `4158` | "Your therapist sees homework status, messages you send them, and any journal entries you explicitly share" | **FALSE** (missed) | Omits activity records (R-C-13) |
| Privacy `4161` | "We don't sell or share your data with third parties" | UNVERIFIABLE | Legal question (S4A-min) |
| Privacy `4166`, `4167` | "All stored data is encrypted at rest (AES-256) and in transit (TLS)" / "Chat data is encrypted at rest and in transit by our chat provider" | UNVERIFIABLE | Platform properties; device-side `localStorage` (session, Botpress key, message queues) is not encrypted by the app |
| Privacy `4168` | "Database access is controlled by row-level security — your therapist can only see their own clients" | UNVERIFIABLE | Live policies unverified; R-B-07 |
| Guest card `288`, prompt bar `339` | (never shown) | n/a | Verified no-ops (1011-1013, 3108-3112) |

---

## 4. Connected-state path enumeration (R-C.2)

"Connected state" means `therapistLink` set, `showConnectedUI()`, homework, and identity sent with a link. It is reached in exactly one place: `loadConnectedState()` past the gate, lines `2043-2110`. There is no other assignment to `therapistLink` except the Log Out reset (`1223`). Every path below ends in that function; the gate at `2033-2041` runs before any unlock, **but evaluates `links[0]` only** (R-C-02).

| # | Entry | Trigger (line) | Reaches `loadConnectedState()` at | Gate passes? |
|---|---|---|---|---|
| 1 | Page load with a stored session | DOMContentLoaded `getSession()` (4219-4222) | 4222 | Yes, first row only |
| 2 | SIGNED_IN listener | 4187-4188; fired by `signInWithPassword` (1536), `signUp` returning a session (1541-1581), `verifyOtp` after `?t=` (3759), tokens in the URL detected at `createClient` (456; R-C-06), a sign-in in another tab (library broadcast) | 4188 | Yes, first row only |
| 3 | Login modal, no invite | 1594-1600 | 1599 | Yes, first row only |
| 4 | Login modal with invite | 1596-1597 then `handleConnectSubmit` | 1483 | Yes, first row only |
| 5 | Connect modal | menu 150 (hidden once connected, 906), connect prompt 860, `?invite=` 3794 (**not hidden once connected**) -> 1437 -> `handleConnectSubmit` | 1483 | Yes, first row only (R-C-02) |
| 6 | Stored invite code, no active link | 2000-2006 -> `handleConnectSubmit` | 1483, or 2016 if unclaimed | Yes (R-C-11: may claim someone else's code) |
| 7 | Consent completion | button 1348 -> `_aloOnboardingComplete` 1371 | 1411 | Yes (re-read at 1391-1394 checks every row) |
| 8 | Password recovery | 4183-4185 -> `showSetNewPasswordModal` | 1701 | Unreachable in practice (R-C-20) |
| 9 | Reloads (theme toggle 573, error retry buttons 2128, 3862, 4082, iOS PWA relaunch) | page load | as 1 | as 1 |

Not connected-state (nothing therapist-related unlocks): `showLoggedInNoConnection()` (817: chat, memory settings, journal, tab bar) for an account with no active link; `resetToGuestUI()` (1049) and the failed-`?t=` path (4214) for guests. `TOKEN_REFRESHED` (4193-4195) does nothing.

Adversarial attempts and results: R-C.2 answer in section 3.

---

## 5. Parity (R-C.9)

`dev.html` 4,308 lines vs `index.html` 3,498; `dev.css` 3,811 vs `styles.css` 3,573. `dev.html` references `dev.css?v=15`; `index.html` references `styles.css?v=11`. Production (`index.html`) last changed 2026-05-09 (`acad1ed`). Every difference is dev ahead of production; nothing in production is newer; no drift.

### 5.1 A7-C status

| Item | dev.html marker and behaviour | index.html |
|---|---|---|
| A7-C1 write-before-confirm | `2078-2110`: `session_metadata` POST awaited, then `updateUser` and the auth bridge. The catch path still sends the bridge (by design since `1be5fa7`). Present, but ineffective against A-21 because the bot never reads the nonce (R-C-10) | Absent (0 `A7/C` markers) |
| A7-C2 guarded persistence | `4035-4067`: one retry after 2 s, then the local queue and toast. The queue is never replayed (R-C-22) | Absent |
| A7-C3 serialized write queue | `472-475`, `2199-2237`: present; the conversation id is read at execution (R-C-23) | Absent |
| A7-C4 in-flight create dedup | `4040-4047` `window._aloEnsureConvPromise`: present (the retry path at 4055-4057 is not deduplicated) | Absent |
| A7-C5 Botpress init failure state | `3835-3864`: present | Absent |
| A7-C19 dropped-format logging | `4011-4022`: present; stores raw messages locally (R-C-22) | Absent |
| (A7-bonus) `privateSession` as a string | `2971-2977`, `2988-2990` | **Absent: production still sends booleans** (`index.html:2467`, `2480`), which the dev comment says "silently broke every subsequent turn once this was set" |

As D36 expects, all six A7-C fixes are absent from `index.html`, as are the A-11 consent gate (production has no onboarding or consent screens at all; `grep consent index.html` = 0), the A-10 memory display default (`index.html:423` `memoryGlobalEnabled = false`), the A-23 copy (`index.html:179` "Alo doesn't store your conversations word for word"), the CSP, the `?t=` exchange and `?invite=` prefill. Because the demo URL is production (D35 section 7), until the promotion sitting every one of those is live as the old version.

### 5.2 `diff dev.html index.html` (116 hunks, 1,156 lines), grouped

| dev.html lines | What | Class |
|---|---|---|
| 10-21 | CSP meta | missing promotion (R-C-18) |
| 29-33 | manifest, apple-touch-icon, favicons | intentional dev-only per comment; **hazard** if copied (R-C-32) |
| 63 | `dev.css?v=15` vs `styles.css?v=11` | expected; rewrite the reference at promotion |
| 67-82, 4228-4305 | Android install banner, iOS card, install logic | missing promotion (Phase 2 item 13a) |
| 84, 3028-3040 | logo click behaviour | missing promotion |
| 138-145, 633-639 | "How Alo works", "Your privacy" menu items | missing promotion (P2B-11) |
| 158-166, 2994-3025; index 311-314 removed | private toggle and new-private items; old floating button removed | missing promotion |
| 177, 216, 228-231, 2679, 2740, 3069-3074, 3639, 4129-4172 | demo copy pass, A-23 | missing promotion (Brief 1a-min C/D) |
| 280-309, 337-339, 1007-1013, 1048-1049, 3043-3058, 3110-3111, 4224-4225 | guest card and prompt bar as no-ops; memory card as disclosure | missing promotion (1a-min B/D) |
| 434-441, 1231-1414, 3600+ (css) | four-screen onboarding and consent | missing promotion (P2B item 8, 1a-min A) |
| 471-478, 487-496, 1948-2130, 3806-3864, 4089-4090, 4198-4217 | A7-C3 state, A-10 default, deferred Botpress init, consent predicate and gate, A7-C1, load-error state, `?t=` takeover | missing promotion (1a-min A, A7-C1/C3/C5, D29-03) |
| 591-630, 1095, 2918, 2968, 3160 | contextual tips | missing promotion (P2B item 10) |
| 643-688, 740-744 | shared focus trap | missing promotion (Phase 3 COSMETIC-1/-2) |
| 815-818, 1447-1537 | no-link Botpress init; `handleConnectSubmit` return values; login modal A5 | missing promotion (1a-min A2/A4/A5) |
| index 1394-1424 removed | old `showPrivacyModal()` (its list included "How often you use Alo (not what you discuss)") | missing promotion of a deletion; the disclosure did not carry over (R-C-13) |
| 1105-1149, 2178-2181, 2221-2235, 2260-2274, 3094-3096, 3349-3356 | console-only rationale comments; homework and journal load-error UI | missing promotion (Phase 3 SILENT) |
| 2193-2237, 4011-4067 | A7-C2/C3/C4/C19 | missing promotion |
| 2297-2348, 2403-2478 | thread paging (BROKEN-1, Phase 2 item 4) | missing promotion |
| 2821-2827 | A-10 settings default | missing promotion |
| 2970-2989 | A7-bonus string flag | missing promotion |
| 3692-3799 | D29-03 token exchange; `?invite=` prefill | missing promotion |

### 5.3 `diff dev.css styles.css` (4 hunks, all additions in dev)

| dev.css lines | What | Class |
|---|---|---|
| 2537-2545, 2548-2565 | `.load-error`, `.load-retry-btn` | missing promotion (Phase 3 SILENT-6) |
| 3600-3699, 3701-3811 | installable-app placeholders; onboarding and consent overlay | missing promotion (13a, P2B item 8) |

At promotion, `styles.css` needs `?v=12` or higher in `index.html`, and the manifest link must not be copied until `start_url` changes (R-C-32).

### 5.4 Hygiene

- Zero-width and smart-quote scan, `python3 scripts/scan-invisible.py dev.html dev.css index.html styles.css`: CLEAN on all four, exit 0. The script covers ZWSP, ZWNJ, ZWJ, BOM, WJ, NBSP and the four smart quotes. It was also run on this report before commit: CLEAN.
- `node --check` on both inline scripts of each HTML file: pass.
- **`manifest.json`:** `"start_url": "./dev.html"`, `"scope": "./"`; linked from `dev.html:30` only. This is the R-B-38 finding, present here (R-C-32).
- **Secrets:** the anon JWT (`role: anon`) once in each HTML file (`dev.html:448`, `index.html:397`), permitted by CLAUDE.md; no service-role key, no `sk-ant`.
- `!important`: 18 in each stylesheet.
- **Doc drift:** the home `CLAUDE.md` gives `index.html` ~2,811 and `styles.css` ~2,850 lines (actual 3,498 and 3,573) and a `chat: [what changed]` commit format that the repo `CLAUDE.md` replaces with "No required format". Not security; noted.
- **Tracked files served publicly** from the production origin: `backup.html`, `padding: 8px 12px;` (R-C-32), `PHASE3_REPORT.md`, `docs/reports/*`, `.claude/commands/*.md` (whether dot-directories are served was not checked).

---

## 6. Harness runs

Headless Google Chrome 153, local `python3 -m http.server`, fresh profile per run. Harness copies of `dev.html` lived in the session scratchpad: `inject.js` replaced by a recording stub that also mirrors the webchat v3.3 storage key and server-side user data; supabase-js replaced by a stub ("stub") or served locally from the real 2.39.0 file ("real"); `window.fetch` answered by a local router with row-scoped read/write emulation. The page's CSP meta was kept. Multi-phase scenarios reload a same-origin iframe so `localStorage` persists. No request left the machine; no real credentials were used.

| Scenario | Mode | Shows | Result |
|---|---|---|---|
| `gate_multilink_consented_first` | stub | two active links, consented row first | no gate; connected; identity sent (R-C-02) |
| `gate_multilink_unconsented_first` | stub | same, unconsented row first | gate shown; no init (R-C-02) |
| `invite_while_connected` | stub | `?invite=` while connected | modal opens; second link active with consent null; no gate; "Connected successfully!" (R-C-02) |
| `stale_after_signout_B_unconsented` | stub | SIGNED_OUT then B with an unconsented link | stale `clientId`/link; old id re-sent to Botpress; consent PATCH on A's row; B stuck (R-C-17, R-C-01) |
| `stale_after_signout_B_nolink` | stub | SIGNED_OUT then B with no link | Botpress data still A; share toggle offered naming A's therapist (R-C-17, R-C-01) |
| `xss_therapist_strings` | stub | therapist name, homework fields, client label | handlers ran at load, in the name editor (attribute), message modal, share confirm (R-C-03, R-C-09) |
| `delete_zero_rows` | stub | writes filtered to zero rows | five success toasts, `rowsChanged: 0`, server row still shared (R-C-05, R-C-08, R-C-24) |
| `private_new_conv_and_reload` | stub | new private conversation, then reload | `is_private` row listed; after reload, message written into it (R-C-04) |
| `private_toggle_midconv` | stub | private after two turns | earlier turns kept, row not private, copy shown (R-C-15) |
| `memory_off_private_refused` | stub | memory off | private refused with "nothing is being remembered"; message saved (R-C-14) |
| `private_flag_delivery_fails` | stub | `updateUser` rejects | private UI shown; bot data without flag; unhandled rejection only (R-C-07) |
| `pending_invite_residue` | stub | leftover `alo_pending_invite`, B signs in | code claimed for B; profile renamed; gate (R-C-11) |
| `double_entry_consented` | stub | SIGNED_IN plus explicit call | +2 `session_metadata` rows (R-C-28) |
| `token_strip_order` | stub | `?t=` failure | head scripts saw `t=`; strip; one POST; constant toast; guest init (R-C-26, R-C.1) |
| `logout_botpress_residue` (x2) | stub | Log Out and reload | guest header; Botpress conversation restored; user data still the client's (R-C-01) |
| `c3_queue_reset_race` | stub | reset while a write is queued | queued message written with `conversation_id: null` (R-C-23) |
| `real_pageload_double_entry` | real | stored session, plain load | one link read, one `session_metadata` row |
| `real_implicit_hash_injection` | real | tokens in fragment | stored session replaced; connected as the other account (R-C-06) |
| `real_implicit_query_injection` | real | tokens in query | same; tokens remain in the URL (R-C-06) |
| `real_error_description_logout` | real | `error_description` in fragment | session removed; guest page (R-C-27) |
| `real_recovery_modal` | real | recovery tokens | signed in; no "Set New Password" (R-C-20) |
| `real_token_fail_existing_session` | real | failed `?t=` with a stored session | toast; no init; no link read; spinner shown (R-C-19) |

---

## 7. What could not be verified without live credentials or Studio

1. **Live RLS policy text** for `conversation_summaries` (is there a client DELETE?), `conversations` and `journal_entries` (UPDATE/DELETE), `therapist_clients` (SELECT scope for the consent re-read; whether a client may hold two active links), `session_metadata` (who may INSERT a nonce for which `client_id`), `profiles` (therapist name readable by the client). Phase 1 ran from Migration v1.4, which is not local. Close with: `select tablename, policyname, cmd, roles, qual, with_check from pg_policies where schemaname = 'public' and tablename in ('conversation_summaries','conversations','conversation_messages','journal_entries','therapist_clients','session_metadata','profiles','crisis_events');`
2. **Foreign keys and uniqueness:** whether `conversation_messages.conversation_id` cascades on delete, what `conversation_summaries.conversation_id` does, and whether anything prevents two active links for one client. `select conrelid::regclass, conname, confdeltype, pg_get_constraintdef(oid) from pg_constraint where conrelid in ('public.conversation_messages'::regclass, 'public.conversation_summaries'::regclass, 'public.therapist_clients'::regclass);` and `select indexdef from pg_indexes where tablename = 'therapist_clients';`
3. **The live bot.** The export's revision was saved 2026-09-08; Session 2 changes (A-15 excerpt removal, A-20 private gate, identity) are not reflected. Re-export and re-check Init_State identity (66-104), Validate_And_Send line 27, Safety_Check 239-274, Check_And_Route forget (40-43, 210-213) and the two improvement hooks.
4. **Botpress platform behaviour:** the Chat API's server semantics for `updateUser` data (the client-side merge was read from `webchat.js`), how long a user and conversation persist, and any rate limit on user or conversation creation for a public webchat client id. Webchat persistence and rendering were read from the v3.3 CDN bundle (an unpinned path) and emulated, not run against Botpress.
5. **GoTrue project settings:** whether self-signup is enabled (the login modal's `signUp` fallback), the JWT expiry (the lifetime of a URL-borne session link in R-C-06), and the redirect allowlist (reset and confirmation land on `window.location.origin`).
6. **The deployed `exchange-client-token`** matching the repo's single-use and expiry code (R-A's scope).
7. **The dashboard's use of `session_metadata` and `viewed_at`,** taken from the R-B report, not re-read.
8. **Device behaviour:** iOS Safari storage eviction for non-installed sites (how long R-C-01/R-C-22 residue lasts), and real phone rendering of any affected surface.
9. **Whether `alowen.ai` serves dot-directories** (`.claude/commands/*.md`) from the public repo.

---

*R-C v1.0 -- 2026-09-16. Findings only. Fixes are A/S7's after triage. No app file was changed. Branch `auto/r-c-review`, one file.*
