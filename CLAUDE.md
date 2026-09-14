# CLAUDE.md — Alo Client Chat Interface
## What This Repo Is
Client-facing chat interface for Alo (alowen.ai).
Deployed at alowen.ai via GitHub Pages.
Vanilla HTML + CSS + JS. No build step. No framework. No bundler.
## Project Philosophy — Read This First
- Bridge not container: Alo builds emotional independence, not dependency.
- No engagement hooks: no streaks, no notifications, no "we miss you." Ever.
- User agency: users control timing, depth, and direction at all times.
- Zero-Knowledge: clinical signals go to therapist dashboard, never transcripts.
- Craft integrity: nothing ships until it's done right. No shortcuts.
- Data posture (Brief 1a, 2026-09-14) — every screen builds to this and must not contradict it:
  "Alo keeps only what you can see, only for you, deletable in one tap. Nothing is sold.
  Nothing shared without your separate consent. Your therapist never sees a conversation."
## File Structure
- `dev.html` + `dev.css` — development copy, tested at alowen.ai/dev.html. **Edit these.**
- `index.html` + `styles.css` — production, live on push to `main`. **Never touch unless explicitly told to.**
- `scripts/scan-invisible.py` — zero-width / smart-quote scan (ruling D3, D20)
- `docs/contracts/consent-gate-contract-v1_0.md` — server contract the client is coded against
  (columns, `peek_invite_code`, `redeem_invite_code`, `renew_consent`, `delete-client-data`);
  implemented in alo-supabase, run by Kano
- `docs/reports/` — verification artifacts (screenshots)
- `manifest.json`, `icons/` — installable-app assets (dev.html only)
- `CLAUDE.md` — this file
## Stack
- Frontend: Vanilla HTML/CSS/JS
- Hosting: GitHub Pages → alowen.ai (CNAME via Porkbun)
- Conversation Engine: Botpress Cloud (webchat v3.3 SDK, iframe embed)
- LLM: Claude Sonnet 4.5 API (via Botpress)
- Database: Supabase (auth, memory, homework, crisis logging)
- Supabase URL: https://lelsdezstbnzyxvsvbyx.supabase.co
- Botpress Bot ID: fc0fad71-daea-4d22-adf5-3a659042d46a
- Auth/session goes through the Supabase JS SDK (`supabase.auth.*`, `supabase.rpc`); data reads and
  writes go through raw `fetch` via the `api()` helper.
## Account Types
Invite-only. There is no guest chat. The chat opens only when the access gate returns `chat`.
- Signed out: the waiting room (sign in / create account, invite-code field).
- Account (email/password), no active therapist link: the waiting room. Journal read-only
  (view, export, delete), Export my data, Delete my data. An invite code from a therapist connects.
- Client: account + ACTIVE therapist link + CURRENT consent (`consent_version` = `ALO_CONSENT_VERSION`)
  + adult attestation + not paused → chat, memory + history switches, homework, therapist connection.
  Paused / ended / consent-outdated links show the waiting room (`aloComputeAccess` in dev.html).
- Therapist: email/password, dashboard access only.
## Code Standards — Non-Negotiable
- Mobile-first: primary users are on iPhone Safari and Chrome mobile
- WCAG AA minimum: 4.5:1 contrast ratio for text, 3:1 for large text
- Touch targets minimum 44x44px
- CSS custom properties only — never hardcode colors
- Never use !important unless absolutely unavoidable
- Test at 375px (iPhone SE) and 390px (iPhone 14) before every commit
## Critical Warnings
- INVISIBLE CHARACTER BUG: AI-generated code can contain U+200B zero-width spaces
  that silently break JavaScript. Verify page loads after every large code block.
  Scan command (ruling D3, 2026-09-09, versioned per D20 into `scripts/scan-invisible.py`
  instead of a duplicated heredoc — see the "Code safety" section below for why):
```bash
  python3 scripts/scan-invisible.py dev.html dev.css
  ```
- Botpress webchat SDK loaded via CDN — do not version-pin without testing
- Auth flow is sensitive — sign-in/sign-up changes require full end-to-end test
- **`?t=` on load is a one-time test-client session token** (D29-03, 2026-09-09, spec section 6/7/10 in alo-supabase's `Alo_Therapist_Signup_Edge_Function_Spec_v1_0.md`). Stripped from the URL synchronously, before any other async work, then exchanged server-side for a session. Every failure mode shows one constant, cause-neutral message (ruling D31) — do not add a per-cause error message here, ever, even one that feels harmless. Full writeup: alo-dashboard's `OPEN_AS_CLIENT_REPORT.md`.
- **Consent fails closed** (Brief 1a, 2026-09-14). The link becomes active only when `redeem_invite_code`
  writes the consent record in the same transaction as the claim. The client app makes zero direct
  writes to `therapist_clients`; there is no localStorage consent fallback. Do not add either back.
- **The Botpress webchat is initialised only in `aloOpenChat()`, only after the gate returns `chat`.**
  Never call `window.botpress.init` anywhere else.
- **History is the client's switch.** `client_settings.history_enabled` is OFF by default; OFF means
  no `conversations` row and no stored message. Memory needs history on (R-1). The therapist's
  `allow_history` is a recommendation sentence, never a control.
- **Deletion is server-owned.** "Delete my data" / "Delete my account" call `delete-client-data` and
  render the receipt from the response only. Never claim a deletion the server did not report.
- Never send conversation content anywhere except through Botpress
## Working Rules

### Git workflow
- Sessions work on `auto/*` branches; Kano merges. **Never push to `main`.**
- Verify every push actually landed: after `git push`, run `git status` and `git log --oneline -3` to confirm the commit is on the remote branch, not just locally.
- Merging to `main` (Kano) triggers GitHub Pages deploy (allow 1-2 min). Verify alowen.ai on actual iPhone after every deploy if possible.

### File discipline
- This repo has a dev/production file split:
  - `dev.html` + `dev.css` → tested at `alowen.ai/dev.html` (client repo) or `dashboard.alowen.ai/dev.html` (dashboard repo)
  - `index.html` + `styles.css` → production, live immediately on push
- **Never touch production files unless explicitly told to.** Every prompt should name the files to modify.
- When copying dev to production, check whether `index.html` references a different CSS filename than `dev.html`. If `dev.html` references `dev.css?v=N` and `index.html` references `styles.css?v=N`, rewrite the stylesheet reference during the copy — do not blindly `cp dev.html index.html` without fixing this.
- Always increment the cache buster version (`?v=N`) when CSS changes.

### Commit messages
- No required format. Plain descriptive messages are fine.
- Examples of good messages:
  - `Phase 1A: Share journal entry toggle + improved shared visibility`
  - `Fix: timeline badge now refreshes immediately after share/revoke`
  - `Dashboard: shared journal entries view for therapists`
- Messages should describe what changed, not how.

### Code safety
- Scan for zero-width characters (U+200B, U+200C, U+200D, U+FEFF, U+2060) before every commit. One invisible character in inline JavaScript silently breaks the page. This is a known hazard with Claude-generated code.
- Scan command (ruling D3, 2026-09-09, versioned per D20 into `scripts/scan-invisible.py` instead of a duplicated heredoc — not a `grep -P`/`python3 -c` one-liner, whose character class was mangled by shell quoting on 2026-09-08 and produced 2312 false positives; the same mangling can produce a false negative, and this check exists to catch a bug that silently breaks the page. Covers NBSP and smart quotes too, which the old five-codepoint form missed). Exit 0 and `CLEAN` on every line is a pass:
```bash
  python3 scripts/scan-invisible.py dev.html dev.css
  ```

### Schema changes
- Supabase schema changes (ALTER TABLE, CREATE POLICY, etc.) run in Supabase SQL Editor by the developer, not by Claude Code.
- If a change file includes schema changes, flag them as a prerequisite step and do not attempt to run them.
- The consent-gate migration and RPCs live in alo-supabase; the client only consumes them
  (`docs/contracts/consent-gate-contract-v1_0.md`).

### Security reminders
- API keys and secrets never go in commits. The Supabase anon key in `dev.html`/`index.html` is the only exception — it's the public anon key and is designed to be exposed client-side.
- Flag any other credential-looking strings before committing.
- Flag any public vs. private access issues in plain language before making changes.
## What Claude Code Must Never Do
- Do not modify Botpress conversation flows — those live in Botpress Studio
- Do not modify the system prompt — that lives in Botpress Studio
- Do not touch Supabase schema — use Supabase Studio
- Do not add engagement hooks, notifications, or streak mechanics
- Do not add third-party analytics or tracking scripts without approval
- Do not add any feature that sends conversation content outside Botpress
- Do not add a guest chat, a countdown, a "we'll be here", a "come back", or any urgency device to the waiting room
- Do not write `therapist_clients` from the client app, and do not add a consent fallback that lets the chat open without a server-side consent record
