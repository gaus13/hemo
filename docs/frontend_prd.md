# Hemo Frontend Product Requirements Document

**Document status:** Frontend implementation handoff
**Product:** Hemo
**Audience:** React frontend developer, product designer, backend developer, QA
**Source of truth:** Current FastAPI routes, Pydantic schemas, SQLAlchemy models, services, migrations, tests, and project documentation in this repository

## 1. Product Summary

Hemo connects people who need blood with nearby willing donors. A requester creates a structured blood request. Donors discover active requests, volunteer, and communicate with the requester only after they are accepted. The requester confirms donation proof after the hospital visit, which creates the donor's donation history and completes the verification workflow.

Hemo is a coordination product, not a medical authority. The UI must clearly state that eligibility, compatibility, and donation decisions are ultimately confirmed by a registered hospital or medical professional.

## 2. Product Goals

1. Let a requester create and track an urgent blood request in under two minutes.
2. Let a donor quickly find relevant active requests and volunteer with one clear action.
3. Make every request's progress understandable through a visible status timeline.
4. Keep personal contact information private until a donor has explicitly volunteered.
5. Make the donation proof and confirmation handoff auditable.
6. Make failures, stale data, permissions, and network interruptions understandable rather than silent.

### Non-goals for this frontend release

- Medical eligibility approval or diagnosis.
- Automatic donor approval based only on blood group.
- Admin analytics or hospital administration workflows; no admin routes currently exist.
- Email, SMS, browser push, or FCM settings; backend adapters are placeholders.
- A public social feed or unrestricted user-to-user messaging.

## 3. Users and Permissions

### Authenticated user

Registration and login return a JWT bearer token. The frontend stores the token using the project's approved security approach, sends it as `Authorization: Bearer <token>`, and clears the session on an unrecoverable `401`.

The backend does not currently return a role in the auth response. A user may have a donor profile, a requester profile, or both. The app should determine available workspaces by calling both `GET /donor/profile/me` and `GET /requester/profile/me`; a `404` means that profile has not been created.

### Donor capabilities

- Create, view, and update a donor profile.
- Toggle availability through the donor profile update.
- Browse active public blood requests with filters and pagination.
- Volunteer for an active request.
- Cancel a matched volunteer, returning the request to `ACTIVE`.
- Upload donation proof after acceptance.
- View donation history.
- Use chat only as the accepted donor for an eligible request.

### Requester capabilities

- Create, view, and update a requester profile.
- Create one active blood request at a time.
- View and edit own active request.
- View matched donors for an own active request, ordered by distance.
- Accept a pending volunteer.
- Cancel a request when its state permits.
- Complete a verified request when its state permits.
- Verify a donor's uploaded proof for an own request.
- Use chat only as the request owner for an eligible request.

## 4. Recommended Frontend Stack

- React 19 + TypeScript, built with Vite.
- React Router for authenticated and role/workspace routes.
- TanStack Query for server state, caching, invalidation, retries, and mutations.
- React Hook Form + Zod for typed forms and client-side validation.
- MUI (Material UI) for accessible primitives, responsive layout, dialogs, tables, alerts, and date inputs. Use one custom theme rather than mixing component libraries.
- `date-fns` for display and validation of dates; send ISO 8601 values to the API.
- `ky` or Axios for a single authenticated API client with normalized error handling.
- Zustand only for small client state such as session/profile readiness, active workspace, and chat connection state. Do not duplicate API data in a global store.
- Vitest + Testing Library for component and hook tests; Playwright for critical end-to-end flows.
- MapLibre GL JS or a simple map provider only after the team confirms a map API and privacy policy. Coordinate input must still work without a map.

## 5. Information Architecture

### Public routes

- `/login`
- `/register`
- `/about` or a concise safety/help page

### Authenticated shell

Desktop: persistent left navigation and top bar. Mobile: bottom navigation or a drawer with the same destinations.

- `/app` - role-aware dashboard
- `/app/discover` - donor marketplace
- `/app/requests` - requester requests and request details
- `/app/requests/new` - create request
- `/app/requests/:requestId` - request detail and timeline
- `/app/requests/:requestId/matches` - requester matching workspace
- `/app/chat/:requestId` - participant chat
- `/app/donations` - donor donation history
- `/app/profile` - profile completion and editing
- `/app/notifications` - notification inbox
- `/app/settings` - session and basic preferences

The shell must hide actions the current user cannot perform, but UI hiding is not a security boundary. API errors remain authoritative.

## 6. Core User Flows

### 6.1 First-run onboarding

1. User registers or logs in.
2. App checks donor and requester profiles in parallel.
3. If neither exists, show a short choice: `I need blood` or `I want to donate` with an option to add the second profile later.
4. Guide the user through the selected profile form.
5. Land on the appropriate dashboard with a completion indicator for the other profile.

Do not ask the user for `user_id`, `is_available`, `created_at`, request status, or other server-owned fields.

### 6.2 Requester creates a request

Form fields: patient name, relationship, blood group, units required, hospital name, hospital address, city, urgency, required-by date/time, optional remarks, optional latitude/longitude.

Validation:

- Email must be valid; password is 8-128 characters.
- Units must be a positive integer.
- Required-by must be a valid ISO date/time.
- Latitude and longitude are optional together, but never submit only one.
- Use the exact enum values: blood groups `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`; urgency `low`, `medium`, `high`, `critical`; relationship `family`, `friend`, `colleague`, `ngo`, `other`.

After success, show the request detail page with `ACTIVE` status and a clear next action to view matches. If the API returns `409`, explain that one active request already exists and link to it.

### 6.3 Donor discovers and volunteers

The marketplace calls `GET /blood-request/discover` and supports blood group, city, urgency, sort (`newest`, `urgent`, `required_by`), limit, and offset. Show urgency, deadline, blood group, units, hospital, city, patient relationship, and remarks. Do not expose donor or requester private data.

The request detail page must show a confirmation dialog before `POST /volunteer/{requestId}`. On success, show the donor's volunteer status as `pending` and explain that the requester must accept the offer. Duplicate or closed-request errors must preserve the page and explain the next step.

### 6.4 Requester reviews matches

For an own active request, call `GET /blood-request/{requestId}/matches`. Show a ranked list with distance in kilometers, compatible blood group, availability, and a single `Accept` action. The backend currently returns `DonorMatchResponse`; the frontend must use the actual OpenAPI response once confirmed and must not assume contact details are available.

If the request has no location, show an inline action to edit the request and add both coordinates. If the request is not active, disable matching actions and show the current status.

### 6.5 Acceptance, cancellation, and status timeline

Use a shared timeline component for:

`ACTIVE -> DONOR_MATCHED -> DONATION_IN_PROGRESS -> DONATION_VERIFIED -> COMPLETED`

Alternative valid paths:

- `ACTIVE -> CANCELLED`
- `DONOR_MATCHED -> ACTIVE` when the matched donor cancels
- `DONOR_MATCHED -> CANCELLED`

Requester actions: edit only while `ACTIVE`; accept a pending volunteer while `ACTIVE`; cancel where permitted; verify proof at `DONATION_IN_PROGRESS`; complete after `DONATION_VERIFIED`.

Donor actions: volunteer while `ACTIVE`; upload proof after acceptance; cancel a matched volunteer before donation begins. The UI must not suggest cancellation during `DONATION_IN_PROGRESS`.

Every mutation should optimistically disable the relevant action, show a progress state, invalidate affected request/profile/notification queries on success, and recover cleanly on failure.

### 6.6 Donation proof and verification

The current API schema accepts `proof_file` as a string, not a multipart upload. Implement the initial UI as a proof reference/file URL field with a clear contract flag. Do not build a binary upload experience until the backend confirms the intended upload mechanism.

- Donor submits `POST /donation-proof/{requestId}` with `proof_file`.
- Request moves to `DONATION_IN_PROGRESS`.
- Requester sees a proof-pending state and confirms with `PATCH /donation-proof/verify/{requestId}`.
- Verification creates donation history and makes the donor unavailable.
- Donor sees the new record in `GET /donations/me`.

Show proof submission time, confirmation state, and verification notes when those fields are present in the response. Never imply that requester confirmation is hospital verification; the current history record explicitly sets `verified_by_hospital` to `false`.

### 6.7 Chat

Chat is a private one-to-one conversation scoped to a blood request. Access is limited to the requester and matched donor while status is `DONOR_MATCHED`, `DONATION_IN_PROGRESS`, or `DONATION_VERIFIED`. Cancelled, active-unmatched, and completed requests are not chat-enabled.

The intended contract is:

- History: `GET /chat/requests/{requestId}/messages?before_id={id}&limit=50`
- Live transport: `WS /chat/requests/{requestId}`
- Client message: `{ type: "message", client_message_id, text }`

The UI must support initial history load, pagination upward, connection status, reconnect with backoff, pending/failed sends, deduplication by server message ID or `client_message_id`, and read timestamps when available. Never place a long-lived JWT in the WebSocket URL; use a backend-approved short-lived WebSocket token or secure session mechanism.

## 7. Screen Requirements

### Dashboard

Role-aware summary with urgent actions, active request/donation status, profile completion, unread notifications, and recent activity. Avoid fabricated counts because no aggregate endpoint exists; derive only from loaded data and label derived values.

### Discover

Search/filter toolbar, result count if supplied, responsive request cards/table, empty state, pagination, skeleton loading, and urgent visual treatment that is not color-only.

### Request detail

Request facts, urgency/deadline, hospital/location, status timeline, requester/donor-specific actions, volunteer state, proof state, and chat entry only when authorized.

### Profile

Separate donor and requester sections. Donor fields include full name, phone, blood group, gender, date of birth, weight, city, state, coordinates, and availability. Requester fields include full name, phone, city, and state. Show profile `404` as an onboarding state, not a generic error.

### Notifications

Reverse chronological list with title, message, event type, timestamp, read state, and deep link when payload data identifies a request or volunteer. Current API provides read state but no mark-read endpoint; display the state without pretending it can be changed until the endpoint exists.

### Donation history

Donor-only table/timeline with hospital, units, donated date, hospital verification state, and notes. Include an empty state that explains history appears after requester verification.

## 8. Visual and Interaction Direction

The visual language should feel trustworthy, calm, and operational under pressure: warm off-white canvas, deep charcoal text, restrained red used for urgency and primary emergency actions, and teal/green used for verified or available states. Avoid a generic medical-blue dashboard and avoid making every item a floating card.

- Use a strong editorial display face for page titles paired with a highly legible sans-serif for controls and data.
- Use full-width page sections and compact framed items only for repeated requests, dialogs, and tool surfaces.
- Use consistent status chips with text plus icon; never communicate status by color alone.
- Use urgency hierarchy, not flashing animation. Reserve motion for page entry, list reveal, confirmation feedback, and connection changes.
- Support 320px mobile width through desktop; forms become single-column and actions remain reachable with one hand.
- Maintain WCAG 2.2 AA contrast, visible focus, keyboard operation, 44px minimum touch targets, semantic labels, and screen-reader status announcements for mutations and connection changes.

## 9. Data and API Integration Rules

Create typed API modules grouped by domain: `auth`, `profiles`, `bloodRequests`, `volunteers`, `donationProof`, `donations`, `notifications`, and `chat`.

Normalize FastAPI errors from `{ detail: string }` into a shared error type. Handle these consistently:

- `400`: invalid transition, invalid coordinates, closed request, or invalid input.
- `401`: expired/invalid token; attempt refresh only if a refresh contract is added, otherwise sign out.
- `403`: authenticated but not allowed; keep the user on the page and explain why.
- `404`: missing profile/resource; route to onboarding or an empty state when appropriate.
- `409`: duplicate profile, active request, volunteer, or proof; refetch the relevant resource.

Use UTC for storage and API transport. Render in the user's locale and always include timezone context for required-by and donation timestamps. Treat enum strings as API values and map them to human labels in one shared formatter.

## 10. Backend Contract Gaps to Resolve Before Production UI

These are not frontend assumptions and should become backend tickets:

1. Auth response does not include the authenticated user ID, profile availability, or role; either add a `GET /auth/me` endpoint or enrich auth responses.
2. No role-specific authorization dependency is exposed; routes rely on profile existence and service checks. Confirm the intended dual-profile behavior.
3. `GET /notifications/me` exists, but no mark-read, unread-count, delete, or real-time notification endpoint exists.
4. Notification event creation expects `event_id`, while publishers shown in the repository do not visibly add it; verify notification persistence end to end.
5. Volunteer response and the requester workflow do not expose a list of volunteers for an own request. Add an endpoint or include volunteers in request detail.
6. Donor matching response contract must be confirmed in OpenAPI, including whether it exposes donor ID, name, blood group, availability, and distance only.
7. Chat model and access helper exist, but the HTTP history and WebSocket routes are not present in the current route registry. Implement and document them before enabling chat navigation.
8. Donation proof currently uses a string field. Decide between multipart upload, pre-signed object storage upload, or a validated URL and document size/type/security rules.
9. `/blood-request/discover/{request_id}` returns only active requests and its public response omits coordinates and status. Confirm whether this is sufficient for the detail page.
10. README describes 90-day eligibility, reliability scores, push/FCM, refresh tokens, and admin analytics, but the current models/routes do not expose those capabilities. Keep them out of the first frontend scope or add explicit API contracts.
11. Confirm CORS, token expiry, WebSocket authentication, rate limits, and file scanning rules for the deployed environment.

## 11. Acceptance Criteria

- A new user can register, choose a workspace, complete a profile, and return to the dashboard without a hard refresh.
- A requester can create one valid request, see its `ACTIVE` timeline state, and receive useful validation for invalid fields or incomplete coordinates.
- A donor can filter active requests, open a detail page, volunteer once, and see the pending state.
- A requester can accept a pending volunteer and see the request move to `DONOR_MATCHED`; other pending volunteers appear rejected once the backend exposes them.
- The matched donor can cancel before donation starts and the request returns to `ACTIVE`.
- The donor can submit a proof reference and the requester can verify it; both users see the resulting state and notifications.
- Donation history is visible to the donor after verification.
- Unauthorized users cannot access another user's request actions or chat, even if they navigate directly to a URL.
- All primary workflows have loading, empty, validation, server-error, offline/retry, and mobile states.
- Keyboard-only and screen-reader smoke tests pass for auth, request creation, volunteering, acceptance, proof confirmation, and chat connection status.

## 12. Delivery Plan

### P0: Foundation and API shell

App shell, theme, routing, auth client, token handling, query client, error boundary, profile discovery, responsive navigation, and shared status/date/error components.

### P1: Core requester and donor journeys

Onboarding, profiles, dashboard, request creation/editing, marketplace filters, request details, volunteer mutation, requester acceptance, and request timeline.

### P2: Completion workflows

Proof submission contract, requester verification, donation history, notifications inbox, deep links, and robust empty/error states.

### P3: Chat and production hardening

Implement chat only after backend routes/auth are available. Add reconnection, history pagination, deduplication, read state, Playwright flows, accessibility checks, telemetry, and performance review.

## 13. QA Scenarios

At minimum, test:

- Invalid credentials, duplicate email, inactive account, expired token, and logout.
- Missing donor/requester profile and users with both profiles.
- All required and optional request fields, enum values, deadline formatting, and coordinate pairs.
- Existing active request blocks a second request.
- Marketplace filters, pagination, empty results, critical urgency, and closed-request race conditions.
- Duplicate volunteer, accepted volunteer, donor cancellation, requester cancellation, and invalid status transitions.
- Missing location blocks matching; matching is ordered by distance.
- Proof duplicate, wrong donor, wrong requester, already verified, and history creation.
- Notifications with unread/read states and missing payload deep links.
- Chat unauthorized access, reconnect, duplicate client message, 2,000-character limit, and read-only/disabled states.
- Mobile widths, keyboard navigation, reduced motion, slow network, and API retry behavior.
