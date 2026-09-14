# Contract — implemented in alo-supabase; run by Kano; client coded against it in Brief 1a

Version: v1.0 · Source: Brief 1a, section 3 (2026-09-14) · Consumer: `dev.html` (alo-client-chat-full_v1, branch `auto/s4a-consent-gate`)

The database changes, RPCs and edge function below are built in the private `alo-supabase` repo and run by Kano. The client app is coded exactly to this contract and never ahead of it. Nothing in this file is executed from the client repo.

## 3.1 Columns (informational — the client never writes these directly)

```sql
alter table public.therapist_clients
  add column if not exists consent_version text,
  add column if not exists consent_collect_at timestamptz,
  add column if not exists consent_share_safety_at timestamptz,
  add column if not exists attest_adult_at timestamptz,
  add column if not exists attest_location text,
  add column if not exists attest_location_at timestamptz,
  add column if not exists paused_at timestamptz;

alter table public.client_settings
  add column if not exists history_enabled boolean not null default false;
```

`paused_at` is set by the dashboard (therapist pause); null means not paused. `status` values the client may see on its own rows: `pending`, `active`, `archived`.

## 3.2 RPCs (called with `supabase.rpc(...)`, user JWT)

```text
peek_invite_code(p_code text) -> jsonb
  { "valid": true,  "therapist_name": "Dr. Example", "client_display_name": "Sam" }
  { "valid": false }
  raises: not_authenticated

redeem_invite_code(p_code text, p_consent jsonb) -> jsonb
  p_consent = {
    "version": "consent-2026-09-v1.3",
    "collect": true,
    "share_safety": true,
    "memory": false,
    "attest_adult": true,
    "attest_location": "WA",
    "acknowledged_at": "<ISO timestamp from the client clock, informational>"
  }
  returns { "link_id": "<uuid>", "status": "active", "therapist_name": "...", "client_display_name": "..." }
  raises (message text is the code): not_authenticated · consent_incomplete · invalid_code · already_linked
  Atomic: claim + consent record + client_settings upsert (memory_enabled = memory, history_enabled = memory) in one transaction.

renew_consent(p_consent jsonb) -> jsonb
  same p_consent shape; updates the caller's own ACTIVE link's consent columns; returns { "status": "active", "consent_version": "..." }
  raises: not_authenticated · consent_incomplete · no_active_link
```

Error handling rule: read the error message string; if it equals one of the codes above, show the matching copy from Brief 1a section 5; anything else → the generic "Something didn't go through. Nothing was changed. Try again in a moment." Never show raw error text.

## 3.3 Edge function `delete-client-data`

```text
POST {SUPABASE_URL}/functions/v1/delete-client-data
headers: apikey: <anon key>, Authorization: Bearer <session access_token>, Content-Type: application/json
body:   { "scope": "data" | "account", "confirm": "DELETE" }

200 { "ok": true, "scope": "data",
      "deleted": [ { "table": "journal_entries", "rows": 12 }, ... ],
      "botpress": { "conversations_found": 3, "conversations_deleted": 3, "status": "complete" | "partial" | "failed" },
      "account_deleted": false,
      "vendor_note": "<one or two sentences, server-authored, about what the AI vendor retains under its policy>",
      "completed_at": "<ISO>" }
4xx/5xx { "ok": false, "error": "<code>" }
```

The client renders the receipt from the response only. On any non-200, or `ok: false`, show: "Deletion didn't go through. Nothing was deleted. You can try again, or email kano@alowen.ai." (`account` scope on success: sign the user out and show the receipt on the waiting room.)

## 3.4 Constants (near the top of the client script)

```js
const ALO_CONSENT_VERSION = 'consent-2026-09-v1.3';
const ALO_PILOT_LOCATION = 'WA';
const ALO_DISCLOSURE_RETURN_DAYS = 7;
const ALO_DISCLOSURE_INTERVAL_MS = 3 * 60 * 60 * 1000;
const ALO_DISCLOSURE_GAP_MS = 30 * 60 * 1000;
```

## How the client uses this contract (for the reviewer)

| Client function (`dev.html`) | Contract surface |
| --- | --- |
| `aloFetchLatestLink` | `select` on `therapist_clients` (own rows, any status): `id, therapist_id, display_name, status, paused_at, consent_version, consent_collect_at, consent_share_safety_at, attest_adult_at, attest_location, connected_at, allow_*` |
| `aloComputeAccess` | `status`, `paused_at`, `consent_version`, `attest_adult_at` |
| `aloStartConnectFlow` | `peek_invite_code(p_code)` |
| `_aloConsentSubmit` (gate) | `redeem_invite_code(p_code, p_consent)` |
| `_aloConsentSubmit` (renew) | `renew_consent(p_consent)` |
| `loadMemorySettings` / `aloSaveSettings` | `client_settings.memory_enabled`, `client_settings.history_enabled` |
| `aloCallDeleteFunction` | `POST /functions/v1/delete-client-data` |
| `aloReceiptHTML` | the 200 response body, verbatim |

The client makes zero direct writes to `therapist_clients` (grep proof in `S4A_CONSENT_GATE_REPORT_v1_0.md`).
