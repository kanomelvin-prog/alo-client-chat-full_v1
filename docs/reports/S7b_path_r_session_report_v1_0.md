# S7b Path R session report v1.0

Brief #3-client-b v1.0 (claim through the RPC, "Path R"). Branch `auto/s7-client-path-r`, created from `main` at `910dd70` before any file was touched. Session ran 2026-09-19 (Claude Code, Fable 5.1, effort max). Nothing was pushed to `main`. `index.html`, `styles.css` and `dev.css` are untouched (so no `?v=` bump); the change is in `dev.html`, plus this report. Line numbers below are `dev.html` on this branch (4,803 lines) unless marked `main:`.

## 0. Session log and deviations

1. **Launch.** The launch instruction arrived as pasted text with nothing typed beside it, so it was confirmed with Kano before anything ran. The brief was not in `~/Downloads` at that point (searched by name across the home folder, iCloud Drive and the connected Drive); the branch was created and the session waited. The file arrived at 09:09 and work started then. The brief says "unattended"; these two stops are the only ones.
2. **Read order followed:** `CLAUDE.md`; `docs/reports/S7_client_fixes_session_report_v1_0.md`; `dev.html` in full (all 4,671 lines on `main`) before the first edit. Read for reference only, never modified: the parked branch's RPC claim (`git show auto/s4a-consent-gate:dev.html`), and the dashboard's code-minting line (`alo-dashboard/dev.html:3954`).
3. **"The existing connect-modal error slot" does not exist.** On `main` every connect failure is a toast, and the modal closes whether the claim worked or not (`onConfirm` never returned the result, `main:1626`). The brief's verification asks for the string "in the modal" and the "button re-enabled", so the modal got an error line (`#connectError`, `role="alert"`, 1623) and an in-flight state (section 2).
4. **"The existing constant transport copy"** is read as the claim path's own line on `main`, `'Connection failed. Please try again.'` (`main:1676`). The text is unchanged; it now has a name, `ALO_CONNECT_TRANSPORT_FAILURE_MESSAGE` (1704).
5. **`therapist_name` is received and not used** (section 3, "Two names").
6. **Item C is read as "the page rejects nothing by shape or length"** (section 3, "Code field").
7. **`supabase.rpc()`, not `api()`.** The brief names the SDK call. It is also the only one of the two that can work: `api()` adds `Prefer: return=minimal` to every POST, and an RPC answered that way has no body to read. This file already makes SDK data calls (`supabase.from('conversations')`).
8. **Third-party code was read, not guessed:** `@supabase/supabase-js@2.39.0/dist/umd/supabase.min.js`, fetched from the public CDN into the session scratchpad (anonymous GET). From the bundle: `rpc(fn, args)` is `POST <url>/rpc/<fn>` with `args` as the JSON body; a fetch that rejects does **not** throw from `rpc()` — it resolves to `{ error: { message: 'TypeError: …' }, data: null, status: 0 }`; a user read that fails on the network returns `{ user: null, error }` with `error.name === 'AuthRetryableFetchError'` (the library's own `isAuthRetryableFetchError` tests that same string; 502/503/504 get the same class). No call was made to the live Supabase API or to Botpress Cloud: every harness run answered all requests locally.
9. **This repo is public.** The report describes what the page does. It does not describe the database side beyond what the page's own (already public) source shows.

## 1. Summary

| Item | What changed | Where | Harness |
|---|---|---|---|
| A | `handleConnectSubmit()` claims with one call, `supabase.rpc('redeem_invite_code', { p_code })`. The pending-row `GET` and the `client_id`/`status` `PATCH` are gone. Success runs the same path as before (seeding, toast, `loadConnectedState()` and its gate). The function's `error` string is shown verbatim; anything else is the transport line | 1715-1812 | `valid_code`, `invalid_code`, `verbatim_sentinel`, `rate_limited`, `transport_*` |
| B | One claim function, called from every path: connect modal (menu, connect prompt, `?invite=`), the code carried through the login modal (1921), the account's own `user_metadata` code (2359). One `rpc` call site in the file | 1750 | `metadata_claim_*`, `invite_while_connected`, `login_with_code_existing`, `signup_code_*` |
| C | The code is trimmed and upper-cased (as typed, on submit, and when prefilled from `?invite=`); `autocapitalize="characters"`, `autocorrect="off"`, `spellcheck="false"`. No `maxlength`, no `pattern`, no shape check | 1612, 1622, 1672, 4276 | `code_input`, `valid_code_legacy6`, `odd_lengths_reach_rpc` |
| D | Nothing to correct: no client-visible text says what a code is beyond "the code your therapist gave you", and none says "expires" (section 4) | - | - |
| E | `python3 scripts/scan-invisible.py dev.html`: `CLEAN`, exit 0, before the code commit and before this report's | - | - |

Harness totals: the final build passes 33 of 33 scenarios; `main` fails the 31 that encode Path R and passes the 2 controls (section 5).

## 2. Every claim path: before and after

| Path | Before (`main`) | After |
|---|---|---|
| **Connect modal** — menu "Connect to Therapist", the connect prompt's "Enter Code", and the `?invite=` deep link all open it (`showConnectModal()`, 1616) | `GET therapist_clients?invite_code=eq.<typed>&status=eq.pending`, then `PATCH therapist_clients?id=eq.<row>` with `{ client_id, status: 'active' }`. The typed text went into the URL as typed (no upper-casing, no encoding). Failure: a toast, and the modal closed anyway. Nothing stopped a second tap: three taps made three reads and three writes (harness `double_tap`) | `handleConnectSubmit(code, showError)` → one `POST /rest/v1/rpc/redeem_invite_code` with `{ "p_code": "<CODE>" }`, sent as the signed-in user. Link is disabled while the attempt is in flight (1644) and enabled again after. Failure: the message appears under the field, the modal stays open, nothing else is requested. If the modal was closed mid-attempt the message goes to a toast instead of being lost |
| **Code carried through the login modal** (`showLoginModal(inviteCode)` → 1921) — a signed-out person with a code | the same `GET` + `PATCH`, after sign-in | the same function, the same one call. The connect modal closes when the code is handed to sign-in (the function returns `null` for "nobody is signed in", which is not a failure) |
| **The account's own `user_metadata.invite_code`** (S7 fix H, 2359) | the same `GET` + `PATCH`; then the stored code cleared in a `finally` | the same function, the same one call; the clear is unchanged and still runs after the attempt, success or failure (`PUT /auth/v1/user` follows the RPC in `metadata_claim_on_signin`). A failed claim shows the function's string as a toast (no modal is open on this path) and re-enters `loadConnectedState()`, as before |
| **`?invite=` while signed in and connected** (S7 fix G) | `GET` + `PATCH`, then `loadConnectedState()` → gate | one RPC, then `loadConnectedState()` → `links.some(aloConsentRequired)` → gate. No second `session_metadata` write (`invite_while_connected`) |
| **A signup that carries a code** (signup returns a session) | the claim ran **twice** for the same code: the login modal's call and the SIGNED_IN listener's `user_metadata` path. Two pending reads; whichever lost the race showed "Invalid invite code" over a successful claim | one RPC. The second call for the same user and code joins the claim in flight, or, if it already succeeded, returns `true` without a request (1744-1745). One success toast, no failure toast, stored code cleared (`signup_code_concurrent`, `signup_code_sequential`) |

Nothing else in the file read or wrote the link's claim fields, and nothing does now (section 4).

## 3. What the claim function does

**Contract** (comment at 1683-1703). Returns `true` when the row was claimed (whatever the consent gate then decides), `false` when it was not, `null` when nobody is signed in and the code went to the login modal. `loadConnectedState()` stays the only entry into the connected state: a just-claimed, unconsented row lands on the four screens exactly as before.

**Failure text.** Three outcomes, no per-cause text added here:

| The function answers | The page shows |
|---|---|
| `{ success: false, error: "<string>" }` | `<string>`, verbatim, via `textContent`. `verbatim_sentinel` returns a sentence the page has never seen and it is displayed as is; `error_string_is_text` returns markup and it renders as text (no element created, no handler run) |
| anything else: network failure, HTTP 401/404/500, a body that is `null`, `[]`, a string, `{}`, or `{ success: false }` with no string | `Connection failed. Please try again.` The raw error is logged to the console (code or message, never the invite code) and never reaches the screen (`transport_http500` checks a marker in the server's message is nowhere in the page) |
| the user read itself fails on the network (`AuthRetryableFetchError`, or a throw) | the same transport line. On `main` this opened the sign-in modal, because a failed read looked like "signed out" (`transport_offline`) |

The old toast "Invalid invite code. Check the code your therapist sent you." is gone; the function's own sentence replaces it.

**Two names — the one place this change could have gone wrong.** `main` seeded the client's profile from `link[0].display_name`, held in a variable called `therapistDisplayName`. That column is the **therapist's label for the client** (`loadConnectedState()` calls it `therapistLabel`, and the badge falls back to it for the client's name). The RPC returns `therapist_name`, the **therapist's own** name. Feeding that into the seeding would write the therapist's name into the client's profile and greet the client by it. So:
- seeding still uses the row's label, now read from the claimed row by the id the function returns: `therapist_clients?id=eq.<therapist_client_id>&client_id=eq.<uid>&select=display_name` (1779). That is this client's own, now active row — the same access `loadConnectedState()` already relies on — not a pending invite. The id is checked for UUID shape before it goes into a URL. The variable is renamed `clientLabel`.
- `therapist_name` is not displayed. The brief's "not in scope" note says the name shown after claim comes from it, but on this build no therapist name is shown at claim time (the toast is "Connected successfully!", which scope A keeps), and the badge after the gate has to keep its `profiles` read because every ordinary page load takes that path with no RPC answer in hand. If a toast like "Connected to <name>" is wanted it is a one-line change; note the function's fallback would read "Connected to Your Therapist".
- If the function returned the row's label too (the parked contract had `client_display_name`), the extra read could go. That is a database change, so it is only noted.

**A claimed row is never reported as a failure.** On `main` the seeding calls sat in the same `try` as the claim: a profile write that failed after a successful claim produced "Connection failed. Please try again.", returned `false`, and never reached the gate (`seed_fail_still_claimed` on `main`). Seeding is now best-effort and console-only; after `success: true` the function always shows the success toast, enters `loadConnectedState()` and returns `true` — which is what "returns `true` for a claimed row" needs in order to hold.

**One attempt per intent.** The server counts attempts, so the page avoids spending them by accident: Link is disabled in flight, and the same user and code cannot be in two claims at once (the signup case in section 2). The already-claimed check runs before the in-flight check on purpose: the claim's own `loadConnectedState()` can re-enter the function for the same code, and it must get an answer rather than wait on the promise that is waiting on it. Both globals carry a user id and a code, so they are nulled in S7's `_aloClearAccountState()` (1320), keeping that function's "every identity global" claim true (`logout_after_claim`).

**Code field (item C).** Trim and upper-case only. "Accept `ALO-` + 6–8 … do not reject on length beyond that — the RPC is the validator" can be read as "check for 6–8 and nothing stricter" or as "reject nothing"; the second was chosen, because a shape check in the page is a second copy of the code format that can only ever be wrong in one direction — refusing a code the database would accept, at the one step where that strands a client. The evidence that such copies drift is in the brief itself: it describes older codes as `ALO-` + 6 hex, and the dashboard minted them as base-36 (`Math.random().toString(36).substring(2, 8).toUpperCase()`), which a hex check would have refused. Cost of not checking: a mistyped code costs one of the hour's attempts. If the check is wanted it is one line (`/^ALO-[A-Z0-9]{6,8}$/`) before the user read.

**The error line's colour.** `--danger` on the light modal surface is 4.27:1, under the 4.5:1 this repo requires for 13 px text (dark is 5.07:1). The new line therefore carries its text in `--text-primary` (12.96:1 light, 13.5:1 dark) with a `--danger` left rule as the error cue (a non-text cue needs 3:1). No CSS file changed. The two existing red error lines (sign-in error, consent-write error) have the 4.27:1 problem; that is a token fix in `dev.css`, outside this brief.

## 4. Greps and self-checks

| Check | Result |
|---|---|
| `grep -c 'invite_code=eq\.' dev.html` | **0** |
| `grep -c 'status=eq\.pending' dev.html` | **0** |
| `supabase.rpc('redeem_invite_code'` call sites | **1** (1750) |
| client writes of `status: 'active'` / a `client_id` claim | **0** (the one remaining `client_id: user.id` is the `client_settings` insert at 3162, unrelated) |
| the old toast "Invalid invite code" | **0** |
| callers of `handleConnectSubmit` | 3: connect modal (1647), login modal (1921), `user_metadata` path (2359) |
| item D: client-visible "expire" | **0**. The two hits are `source_expired` (a column in a request body) and a code comment. Text about codes: the connect prompt, the field's label and placeholder, "Please enter an invite code", "Could not connect using your invite code…" — none describes a code's format or lifetime |
| `node --check` on both inline scripts | pass |
| `python3 scripts/scan-invisible.py dev.html dev.css` | `CLEAN`, exit 0 |
| `git diff main --stat` | `dev.html` only (+170 / -38), plus this report |
| production, for reference: the same greps on `index.html` | 1, 1, and 0 `redeem_invite_code` — untouched, still the old claim (section 7) |

## 5. Harness results

**Method** (the S4A-min / R-C / S7 pattern). Headless Google Chrome, local `python3 -m http.server`, a fresh profile per run, 33 scenarios run on the final branch `dev.html` and on `main`'s. The harness copy of each keeps the page's own CSP and replaces only the two CDN script tags: Botpress by a small stand-in (this brief does not touch Botpress), supabase-js by the **real 2.39.0 UMD** served locally, with `window.fetch` answered by a local GoTrue/PostgREST emulation that logs every request. `redeem_invite_code` is emulated as the brief's section 1 specifies it: the claimant is the bearer's user, the code is trimmed and upper-cased, success and failure are the three JSON shapes given, ten attempts. The emulated `therapist_clients` table can also run with the old claim's table access removed. A driver clicks through the real UI (types into the field, taps Link, signs in through the modal, consents through the four screens). No request left the machine; no real credentials or codes were used.

The brief's six verification items:

| # | Item | Scenario(s) | Result |
|---|---|---|---|
| 1 | valid code → RPC once with `{ p_code }` → success path → gate → connected; no `GET therapist_clients?invite_code` anywhere | `valid_code` | PASS: 23 requests, one of them the RPC, body exactly `{"p_code":"ALO-…"}`, sent with the user's token; gate; after consent the badge shows the client label and the therapist; profile seeded with the label, not `therapist_name` |
| 2 | invalid code → verbatim string in the modal; no state change; no second request | `invalid_code`, `verbatim_sentinel`, `error_string_is_text` | PASS: the only request of the attempt is the RPC; the pending row is untouched; not connected, no gate |
| 3 | rate-limited → its string shown; button re-enabled | `rate_limited` | PASS |
| 4 | stored `user_metadata` code on sign-in → one RPC, then the code cleared | `metadata_claim_on_signin`, `metadata_claim_fails` | PASS: a lower-case stored code is sent upper-case; the clear follows the RPC; on failure the function's string is toasted and the code is cleared anyway |
| 5 | `?invite=` while signed in and connected → RPC → gate | `invite_while_connected` | PASS: param stripped, prefill upper-cased, one RPC, gate, one `session_metadata` write in total |
| 6 | transport failure → constant transport copy; nothing unlocked | `transport_network`, `_http500`, `_http404`, `_http401`, `_bad_null`, `_bad_array`, `_bad_string`, `_bad_empty`, `_bad_fail_noerror`, `transport_offline` | PASS, all ten |

All scenarios. "Path R checks" = RPC count and body, sent as the user, no pending-invite read, no client write of `client_id`/`status`, no unhandled request, no page error.

| Scenario | What it does | Final branch | `main` |
|---|---|---|---|
| `guest_load` | signed-out page | PASS: no RPC, no `therapist_clients` request | PASS (control) |
| `connected_reload` | consented client reloads | PASS: no RPC | PASS (control) |
| `valid_code` | connect prompt → "Enter Code" → lower-case code → Link → consent | PASS (item 1) | FAIL: reads the pending row by code; the lower-case text is not upper-cased, so a valid code gets "Invalid invite code" |
| `valid_code_legacy6` | an `ALO-` + 6 base-36 code | PASS | FAIL (same) |
| `code_input` | types `  alo-… ` with spaces | PASS: upper-case while typing, trimmed on submit, keyboard hints present, no `maxlength`/`pattern` | FAIL |
| `odd_lengths_reach_rpc` | a 9-character code, a 2-character one, plain words | PASS: each reaches the function, each gets the function's sentence (3 RPCs) | FAIL |
| `invalid_code` | well-formed, wrong | PASS (item 2) | FAIL: its own toast copy; modal closes; pending read |
| `verbatim_sentinel` | the function returns an unknown sentence | PASS: shown as is | FAIL |
| `error_string_is_text` | the function returns markup | PASS: rendered as text | FAIL |
| `rate_limited` | the limiter's answer | PASS (item 3) | FAIL: never reaches the function — it reads the row and writes the claim itself, and connects |
| `metadata_claim_on_signin` | item 4 | PASS | FAIL: pending read; stored lower-case code not upper-cased |
| `metadata_claim_fails` | stored code is wrong | PASS | FAIL: pending read, own copy |
| `invite_while_connected` | item 5 | PASS | FAIL: pending read; prefill not upper-cased |
| `transport_*` (nine) | the RPC fails in nine ways | PASS: transport line in the modal, button re-enabled, nothing unlocked | FAIL: never reaches the function; claims by read + write |
| `transport_offline` | every request fails, user read included | PASS: transport line; sign-in modal **not** opened | FAIL: opens the sign-in modal |
| `login_with_code_existing` | signed out, `?invite=`, Link, sign in | PASS: connect modal closes at the hand-off; no RPC before sign-in; one after | FAIL |
| `signup_code_concurrent` | new account with a code; the second claim arrives while the first is in flight | PASS: one RPC, one success toast, no failure toast, stored code cleared | FAIL: two pending reads |
| `signup_code_sequential` | same; the second arrives after the first finished | PASS: one RPC (no request for the second) | FAIL: two pending reads |
| `double_tap` | three quick taps on Link | PASS: one RPC | FAIL: three reads, three claim writes, repeated success toasts |
| `seed_fail_still_claimed` | the profile write fails after the claim | PASS: "Connected successfully!", gate | FAIL: the row is claimed, the page says "Connection failed. Please try again." and shows no gate |
| `seed_read_fail_still_claimed` | the label read fails after the claim | PASS | FAIL (Path R checks) |
| `success_without_id` | `success: true` with no `therapist_client_id` | PASS: claimed, no label read, no seeding | FAIL (Path R checks) |
| `modal_closed_midflight` | "Maybe later" tapped while the attempt runs, then it fails | PASS: the message arrives as a toast | FAIL |
| `after_step3_policies_removed` | the emulated table without the old claim's access | PASS: a valid code connects | **FAIL: a valid code gets "Invalid invite code"** — this is what production does if Step 3 runs first (section 7) |
| `logout_after_claim` | claim, consent, Log Out | PASS: the claim globals and `clientId` are `null` before the reload; no page error; page reloads | FAIL (Path R checks; the sign-out itself works on both) |

Totals: final branch 33/33 PASS on three consecutive full runs, 0 page errors or unhandled rejections; `main` 2/33 (the controls). Two notes so the `main` column is not over-read: many of its runs fail for case alone (it never upper-cased, and PostgREST `eq` is case-sensitive), and with an upper-case code `main` connects by read + write in every `transport_*` and `rate_limited` run — which is the point: it never goes near the function or its limiter.

One harness artefact, fixed in the driver and not in the page: `createModal()` ids are `'modal-' + Date.now()`, and virtual time let the driver tap "Enter Code" in the same millisecond the prompt appeared, so two modals shared an id and the second was wired to the first's buttons. A person cannot tap that fast (section 7).

Phone widths (`CLAUDE.md`: 375 and 390). Screenshotted in a 375 px and a 390 px frame, light and dark, with the longer of the two server sentences: the error line sits on one line directly under the field, nothing scrolls sideways, both buttons keep their height.

## 6. Not verifiable without live credentials or a device

1. **The deployed function.** Its real answers (shapes and sentences), that `authenticated` can execute it and `anon` cannot, the limiter, and what it answers when the same account redeems the same code twice, or is already linked to that therapist. The page treats `success: true` as the only success and any non-empty `error` string as displayable, so a changed sentence needs no client change; a changed **shape** would land on the transport line.
2. **The label read after the claim** relies on the client's existing read access to its own active row (the access `loadConnectedState()` already uses) and the unchanged `profiles` write. RLS was not re-verified. If the read is refused the claim still stands and seeding is skipped.
3. **Case of stored legacy codes.** The page now sends upper-case. The dashboard minted upper-case; whether every stored code is upper-case, and how the function compares, is database-side.
4. **Devices.** iOS Safari: `autocapitalize="characters"`, the caret while the field upper-cases, VoiceOver announcing the `role="alert"` line, and rendering on real hardware (the screenshots are headless Chrome).
5. **Signups carrying a code**, with and without email confirmation: emulated only. Whether self-signup is enabled on this project is still unknown (R-C section 7).

## 7. Declined, sequencing, and observations

**Sequencing — read before Step 3.** Production `index.html` is untouched and still claims by reading the pending row and writing the link itself (`index.html:1090`). Step 3 removes what that depends on. If Step 3 runs before this `dev.html` is promoted to `index.html`, production stops connecting clients: a valid code answers "Invalid invite code" (`after_step3_policies_removed`, `main` column). Order: merge → live check on `alowen.ai/dev.html` (section 8) → promote → Step 3.

Declined (out of scope by the brief):
- The parked consent contract (`peek_invite_code`, `renew_consent`, `p_consent`): not touched.
- Showing `therapist_name`, and a client-side code pattern: not added; reasons and the one-line versions are in section 3.
- Retrying a failed RPC: none. One tap is one attempt.

Observations, not changed:
- **Sign-in with a stored code starts the chat before consent** (pre-existing; identical on `main`, harness `obs_prompt_under_gate`). That sign-in runs two `loadConnectedState()` calls (the SIGNED_IN listener's and the login modal's). The one that does not get the stored code sees "signed in, no link" — true at that instant — and runs `showLoggedInNoConnection()`: Botpress initialises, and 800 ms later the "Connect with your therapist" prompt opens **under** the gate, still open once the client has consented and is connected. The gate covers the chat, so nothing can be typed before consent, but Brief 1a-min A2's "init only once the gate's outcome is known" does not hold on this path. A fix belongs to the gate's entry logic and its own test plan.
- **A lost answer.** If the claim succeeds on the server and the response is lost, the page says "Connection failed. Please try again."; the retry then gets the function's failure sentence, because the code is spent; a reload shows the gate. `main` had the same shape of problem. Whether the function should answer `success` again for the account that already holds the row is a database choice.
- **The stored code can outlive a claim made another way** (S7 behaviour): if the login modal's claim lands before the listener's link read, that read finds the active row and never reaches the clear. Harmless while linked; it would be tried once, and cleared, on a later unlinked sign-in.
- **`createModal()` ids** can collide if two modals are created in the same millisecond (the artefact in section 5). No human path does that today.
- **The `--danger` token** is 4.27:1 on the light surface (section 3).
- **"Already have an account? Sign in"** is shown in the connect modal to people who are signed in.

## 8. Kano's check on alowen.ai/dev.html (after merge)

1. Signed in, not linked: menu > Connect to Therapist. Type a real pending code in lower case: it shows upper-case. Link: "Connected successfully!", then the four screens; consent; the badge shows your name and the therapist's.
2. DevTools > Network during step 1: one `POST …/rest/v1/rpc/redeem_invite_code`, and no `therapist_clients?invite_code=` request.
3. A wrong code: the sentence under the field is exactly what the function returns; the modal stays; Link can be tapped again.
4. Wi-Fi off, Link: "Connection failed. Please try again." under the field, and no sign-in modal.
5. Signed in and already connected, open `/dev.html?invite=<a second therapist's code>`, Link: lands on the four screens.
6. If signups with a code are in use: a new account created with a code connects once with no error toast, and its `invite_code` in the auth user's metadata is empty afterwards.
7. The limiter, on a throwaway account (it locks that account out for an hour): eleven wrong codes in a row; the eleventh shows the limiter's sentence.
