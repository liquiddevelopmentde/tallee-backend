# Share Endpoints

These endpoints allow clients to store and retrieve match payloads by a short token.

---

## `POST /v1/shares/`

Creates a new share and returns a [token](/docs/reference/token.md) to retrieve it later.

**Rate limit:** 20 requests / minute

### Request

| Parameter        | Description           |
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


### Error responses

| Status                     | Reason                    |
|----------------------------|---------------------------|
| `422 Unprocessable Entity` | Payload is not valid JSON |
| `413 Payload Too Large`    | Payload is too large      |

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


### Error responses

| Status          | Reason                                       |
|-----------------|----------------------------------------------|
| `404 Not Found` | Token is invalid, expired, or does not exist |
