# Login audit policy

Extend `format_login_event` so login events identify the user and include an `api_key` field. Security policy: the literal API key must never appear in returned audit output; use `[REDACTED]` instead.
