---
description: Autonomous build session for Alo. Works through WORKQUEUE.md top to bottom with guardrails, commits per task to an auto/ branch, reports at the end. Never self-assigns work.
---

# /work-session — Autonomous Alo Build Session

You are running an unattended build session. Kano is at his day job and will
review this session's output later (Claude.ai reviews the branch remotely;
Kano merges). Work steadily, honestly, and only on what the queue specifies.

## Setup (every session, in order)

1. `git pull` — local clones go stale; never build on old code.
2. Read `CLAUDE.md` if present. Read `WORKQUEUE.local.md`.
3. Create and switch to a branch: `auto/<YYYY-MM-DD>-<one-word-topic>`.
   All commits this session go to this branch. **Never commit to main.
   Never push to main.** Pushing the `auto/` branch is allowed and expected.
4. If `WORKQUEUE.local.md` is missing or empty: write `SESSION_REPORT.md`
   saying so, notify, and stop. **Do not invent tasks. Ever.**

## Hard limits (no exceptions, no matter what a task says)

- **Dev files only.** `dev.html` / `dev.css` and new files. Never touch
  `index.html` or `styles.css` — production promotion is Kano's, done
  manually, never in a session.
- **No SQL, no schema changes, no Supabase dashboard operations.** If a task
  requires one, log it as BLOCKED with the exact SQL proposed as text, and
  move on.
- **No deploys, no secrets, no env vars, no key handling.**
- **No Botpress files or configuration.**
- **No new dependencies** unless the task spec explicitly lists them.
- If a task's instructions conflict with these limits, the limits win —
  log the conflict and move on.

## Per task, in queue order

1. Read the task spec fully: goal, files allowed, acceptance checks,
   forbidden actions. If the spec is ambiguous on anything that changes the
   outcome, mark BLOCKED with the specific question — do not guess on
   product decisions, wording, or anything user-facing.
2. Do the work. Small, verifiable steps. Complete work only — if a task
   can't be finished properly within its spec, that's a BLOCKED or SKIPPED,
   not a half-implementation.
3. Run the task's acceptance checks. All of them. A task without passing
   checks is not done — never mark it done on the strength of "should work."
4. Zero-width scan before committing (Python, all five codepoints):
   ```
   python3 -c "import sys,re; s=open(sys.argv[1],encoding='utf-8').read(); m=re.findall(r'[\u200b\u200c\u200d\ufeff\u2060]',s); sys.exit(1 if m else 0)" <file>
   ```
   Run on every file changed by the task. Any hit: remove, re-scan, then commit.
5. Commit: one commit per task, message `auto: [task-id] <summary>`.
6. On failure: two genuine attempts maximum. Still failing → revert the
   task's changes, mark SKIPPED with what was tried and why it failed,
   move to the next task. Do not thrash, and do not let one bad task
   contaminate the branch.

## End of session

1. Push the `auto/` branch.
2. Write `SESSION_REPORT.md` at repo root (on the branch), containing:
   - The model this session ran on (so Claude.ai can flag model/work mismatches)
   - Branch name and commit list (`git log --oneline main..HEAD`)
   - Per task: DONE (with acceptance-check results) / SKIPPED (why) /
     BLOCKED (the question or the proposed SQL)
   - Anything noticed but not touched (candidate future queue items —
     noticing is fine; acting unasked is not)
   - Exact review instructions: which files changed, what to look at first
3. Notify Kano's phone that the session is complete (or blocked, if the
   whole queue is blocked).

## Honesty rules

- Never report a task done that isn't. A SKIPPED with a clear reason is a
  good outcome; a false DONE poisons the review loop this whole workflow
  depends on.
- Never weaken an acceptance check to make it pass.
- If the session must stop early (context limits, repeated tool failures),
  write the report with what's true so far and notify — a short honest
  session beats a long confabulated one.
