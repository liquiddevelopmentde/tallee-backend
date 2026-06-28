# Health Endpoint

Returns the current status of the service. Intended for liveness probes and uptime monitoring.

**Rate limit:** 120 requests / minute

## `GET /health`

### Response `200 OK`

| Field    | Type     | Description                               |
|----------|----------|-------------------------------------------|
| `status` | `string` | Always `"ok"` when the service is running |

```json
{
  "status": "ok"
}
```
