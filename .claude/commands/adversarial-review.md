Assume the code changed in this session contains flaws. Do not be neutral — actively search for attack surfaces and failure modes in these seven areas:

1. **Authentication** — can anything be accessed without proper auth?
2. **Data loss** — any path where user data (memory, journal) could be silently dropped?
3. **Race conditions** — async flows where two things happening simultaneously breaks state?
4. **Rollbacks** — if a Supabase write fails mid-operation, is the state recoverable?
5. **Degraded dependencies** — what happens if Botpress, Supabase, or the Claude API is slow or down?
6. **Version skew** — any assumptions about API versions or schema that could break on update?
7. **Observability gaps** — if something fails in production, would you know? Is it logged?

Report findings only — do not implement fixes. Rate each finding: LOW / MEDIUM / HIGH / CRITICAL.

Save report to notes/adversarial-reviews/[date]-[brief-description].md
