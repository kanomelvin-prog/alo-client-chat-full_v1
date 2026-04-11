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
## File Structure
- `chat_index.html` — client chat interface
- `chat_styles.css` — chat stylesheet
- `dashboard_index.html` — dashboard HTML reference copy
- `dashboard_styles.css` — dashboard CSS reference copy
- `CLAUDE.md` — this file
## Stack
- Frontend: Vanilla HTML/CSS/JS
- Hosting: GitHub Pages → alowen.ai (CNAME via Porkbun)
- Conversation Engine: Botpress Cloud (webchat v3.3 SDK, iframe embed)
- LLM: Claude Sonnet 4.5 API (via Botpress)
- Database: Supabase (auth, memory, homework, crisis logging)
- Supabase URL: https://lelsdezstbnzyxvsvbyx.supabase.co
- Botpress Bot ID: fc0fad71-daea-4d22-adf5-3a659042d46a
## Account Types
- Guest: no auth, conversation only, no memory
- Individual: email/password, memory + conversation history
- Client (invite): invite code → Supabase, memory + homework + therapist connection
- Therapist: email/password, dashboard access only
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
  Check with: grep -rP '[\x{200B}]' . --include="*.html" --include="*.js"
- Botpress webchat SDK loaded via CDN — do not version-pin without testing
- Auth flow is sensitive — sign-in/sign-up changes require full end-to-end test
- Never send conversation content anywhere except through Botpress
## Working Rules

### Git workflow
- Work directly on `main`. No feature branches at this stage.
- Solo developer, single-environment project. Branches add overhead without benefit.
- Verify every push actually landed: after `git push`, run `git status` and `git log --oneline -3` to confirm the commit is on `origin/main`, not just locally.
- Push to main triggers GitHub Pages deploy (allow 1-2 min). Verify alowen.ai on actual iPhone after every deploy if possible.

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
- Scan command: `grep -P "[\x{200B}\x{200C}\x{200D}\x{FEFF}\x{2060}]" dev.html dev.css` — should return nothing.

### Schema changes
- Supabase schema changes (ALTER TABLE, CREATE POLICY, etc.) run in Supabase SQL Editor by the developer, not by Claude Code.
- If a change file includes schema changes, flag them as a prerequisite step and do not attempt to run them.

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
