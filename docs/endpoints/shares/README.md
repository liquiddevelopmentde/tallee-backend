# Share Endpoints

These endpoints allow clients to store and retrieve match payloads by a short token.

---

## `POST /v1/shares/`

Creates a new share and returns a [token](/docs/reference/token.md) to retrieve it later.

**Rate limit:** 20 requests / minute

### Request

|                  |                       |
|------------------|-----------------------|
| **Content-Type** | `application/json`    |
| **Body**         | Any valid JSON object |

```json
{
  "players": ["Alice", "Bob"],
  "scores": [3, 1]
}
```

### Response `201 Created`

| Field         | Type      | Description                                                                                |
|---------------|-----------|--------------------------------------------------------------------------------------------|
| `token`       | `string`  | 6-character [token](/docs/reference/token.md) used to retrieve the share (e.g. `"A3KX7M"`) |
| `ttl_seconds` | `integer` | Seconds until the share expires (currently `600`)                                          |
| `expires_at`  | `string`  | ISO 8601 UTC timestamp of expiry                                                           |

```json
{
  "token": "A3KX7M",
  "ttl_seconds": 600,
  "expires_at": "2026-06-28T21:00:00+00:00"
}
```

---

## `GET /v1/shares/{token}`

Retrieves a previously created share by its [token](/docs/reference/token.md).

**Rate limit:** 60 requests / minute

### Path parameters

| Parameter | Description                                          |
|-----------|------------------------------------------------------|
| `token`   | The 6-character token returned by `POST /v1/shares/` |


### Response `200 OK`

| Field     | Type     | Description                              |
|-----------|----------|------------------------------------------|
| `payload` | `object` | The original JSON object that was stored |

```json
{
  "payload": {
    "players": ["Alice", "Bob"],
    "scores": [3, 1]
  }
}
```

### Error responses

| Status          | Reason                                       |
|-----------------|----------------------------------------------|
| `404 Not Found` | Token is invalid, expired, or does not exist |
