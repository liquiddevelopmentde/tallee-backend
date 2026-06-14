# tallee Match-Sharing API

An **ephemeral, account-less relay** for sharing tallee match data between app
instances. The app uploads a compressed match JSON and gets back a short
6-character token; receivers fetch the match by token (QR scan, typed code, or
deep link) until it expires. "Fire & forget" — data lives at most **10 minutes**
and is then deleted automatically.

The server is deliberately dumb: it stores the payload **opaquely** and never
inspects player names or scores. Preview and player-mapping happen entirely on
the client.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Runs immediately with no external dependencies. API docs at
http://localhost:8000/docs.

## API

| Method | Path                  | Description                                                          |
|--------|-----------------------|----------------------------------------------------------------------|
| POST   | `/v1/shares`          | Upload match JSON → `{ token, expires_at, ttl_seconds }` (201)        |
| GET    | `/v1/shares/{token}`  | Fetch match JSON by token → `{ payload, created_at, expires_at }`     |
| DELETE | `/v1/shares/{token}`  | Revoke a share early (204)                                           |
| GET    | `/health`             | Health check                                                         |

Tokens are case-insensitive. Unknown/malformed → `404`; expired → `410`;
oversized payload → `413`; rate limit hit → `429`.

### Example

The payload is one match plus the entities it references (game, group,
players) — the same top-level shape as the app's full export, filtered to a
single match and without `statistics`. The server stores it opaquely; the IDs
are sender-local join keys that the receiver remaps on import.

```bash
# Sender uploads
curl -X POST localhost:8000/v1/shares \
  -H 'content-type: application/json' \
  -d '{
    "players": [
      {"id":"p1","createdAt":"2026-06-01T10:00:00Z","name":"Thomas","description":"","deleted":false},
      {"id":"p2","createdAt":"2026-06-01T10:00:00Z","name":"Mark","description":"","deleted":false}
    ],
    "games": [
      {"id":"g1","createdAt":"2026-06-01T10:00:00Z","name":"Catan","ruleset":"","description":"","color":"#E07A5F","icon":"dice"}
    ],
    "groups": [
      {"id":"gr1","createdAt":"2026-06-01T10:00:00Z","name":"Spieleabend","description":"","memberIds":["p1","p2"]}
    ],
    "matches": [
      {"id":"m1","name":"Catan am 13.06.","createdAt":"2026-06-13T19:30:00Z","endedAt":"2026-06-13T21:00:00Z",
       "gameId":"g1","groupId":"gr1","playerIds":["p1","p2"],
       "scores":{"p1":{"roundNumber":0,"score":10,"change":10},"p2":{"roundNumber":0,"score":8,"change":8}},
       "notes":"","isTeamMatch":false,"teams":null}
    ]
  }'
# → {"token":"XF89J2","expires_at":"...","ttl_seconds":600}

# Receiver fetches
curl localhost:8000/v1/shares/XF89J2
```

## Configuration

Copy `.env.example` to `.env`. Key variables:

- `TTL_SECONDS` — share lifetime (capped at 600).
- `MAX_PAYLOAD_BYTES` — upload size limit (default 256 KB).
- `CORS_ORIGINS` — comma-separated origins or `*`.
- `RATE_LIMIT_CREATE` / `RATE_LIMIT_READ` — per-IP slowapi limits.

## Storage

Shares are kept **in memory** in a single process; a background task purges
expired entries. Data is lost on restart — fine for a 10-minute relay, and it
means the app must run with a single worker.

## Deployment (Docker)

On a server with Docker installed:

```bash
docker-compose up --build -d
```

Builds the image and runs a single app container, restarting automatically
unless stopped. Put a reverse proxy (Caddy / Nginx / Traefik) in front for TLS.

> The container runs a **single uvicorn worker** on purpose — the in-memory
> store lives in one process. That's plenty for this tiny relay. Data is lost on
> restart/redeploy, which is fine for a 10-minute ephemeral relay.

## Tests

```bash
pytest
```
