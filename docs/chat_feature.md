Updated todo list "adding chat feature"

Yes, for a serious production-ready project, WebSockets are the right choice for real-time chat. But WebSockets should handle **delivery**, not be the source of truth. Messages must still be stored in PostgreSQL.

**Recommended architecture**

```text
Client
  ↓ WebSocket
FastAPI WebSocket endpoint
  ↓
Authorization service
  ↓
PostgreSQL message storage
  ↓
Redis Pub/Sub
  ↓
Other connected server instances
```

**Core rules**

- Only the requester and the accepted donor can connect.
- Authorization must be checked when the WebSocket connects.
- Authorization must also be checked when sending each message.
- A volunteer who has not been accepted must receive `403`.
- Chat should be available only while the request is matched or donation is active.
- Cancelled or completed conversations should become read-only, or follow a defined retention policy.

**Database model**

Create a `chat_messages` table containing:

```text
id
request_id
sender_user_id
message_text
created_at
read_at
client_message_id
```

Important database constraints:

- `message_text` cannot be empty.
- Limit message length, for example 2,000 characters.
- Add indexes on `(request_id, created_at)`.
- Add a unique constraint on `(sender_user_id, client_message_id)` to prevent duplicate messages after reconnects.
- Store timestamps in UTC.

The database is important because users can disconnect, refresh the page, or reconnect from another device. When they reconnect, the frontend should request message history from PostgreSQL.

**API design**

Use normal HTTP for history:

```text
GET /chat/requests/{request_id}/messages?before_id=123&limit=50
```

Use WebSocket for live communication:

```text
WS /chat/requests/{request_id}
```

Client sends:

```json
{
  "type": "message",
  "client_message_id": "unique-client-generated-id",
  "text": "I can donate tomorrow morning."
}
```

Server broadcasts:

```json
{
  "type": "message",
  "message": {
    "id": 501,
    "request_id": 42,
    "sender_user_id": 8,
    "text": "I can donate tomorrow morning.",
    "created_at": "2026-08-22T10:30:00Z"
  }
}
```

The server should save the message first, then publish the saved message. This ensures the client receives the real database ID and timestamp.

**Authentication**

For browser clients, avoid putting long-lived access tokens directly in the WebSocket URL because URLs can appear in logs.

Better options:

- Use an HttpOnly secure session cookie.
- Or issue a short-lived WebSocket token through an authenticated HTTP endpoint.
- Validate the token before accepting the WebSocket connection.

For your existing FastAPI application, the clean design would be a WebSocket authentication dependency that reuses your existing JWT verification logic from `auth.py`.

**Redis’s role**

A simple in-memory connection manager works only with one server process. It breaks when you run multiple workers or deploy multiple containers.

Redis Pub/Sub solves that:

- Each WebSocket server subscribes to a request-specific or chat-specific Redis channel.
- When a message is saved, the server publishes an event.
- Every server with a connected participant receives the event.
- Each server sends it to its local WebSocket connection.

Redis should not be the permanent message store. Pub/Sub messages disappear if nobody is listening, so PostgreSQL remains authoritative.

**Reliability features**

Production chat should include:

- Ping/pong heartbeat to detect dead connections.
- Automatic client reconnect with exponential backoff.
- Message history loading after reconnect.
- Duplicate prevention using `client_message_id`.
- Server-generated message IDs.
- Rate limiting per user and request.
- Maximum connection/message sizes.
- Graceful close codes for unauthorized or expired sessions.
- Structured logging without logging message contents unnecessarily.
- Database transactions around message creation.
- Tests for two users, unauthorized users, reconnects, duplicates, and expired tokens.

**Best implementation order**

1. Create the chat message model and migration.
2. Build the shared authorization function:
   - requester matches `request.requester_id`, or
   - donor matches `request.matched_donor_id`.
3. Add paginated HTTP message history.
4. Add a WebSocket endpoint for one matched request.
5. Persist incoming messages before broadcasting.
6. Add Redis Pub/Sub for multi-worker support.
7. Add heartbeat, reconnect handling, rate limits, and observability.
8. Add integration tests using two authenticated clients.

The most important design decision is this:

> WebSocket is the real-time transport; PostgreSQL is the source of truth; Redis distributes events between application instances.

That gives you a project that demonstrates real authentication, authorization, persistence, real-time communication, horizontal scalability, and failure handling rather than just a basic chat demo.