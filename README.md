<div align="center">

<br/>

```
██╗  ██╗███████╗███╗   ███╗ ██████╗
██║  ██║██╔════╝████╗ ████║██╔═══██╗
███████║█████╗  ██╔████╔██║██║   ██║
██╔══██║██╔══╝  ██║╚██╔╝██║██║   ██║
██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝
╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝
```

### **Blood. When it matters most.**

*A production-grade platform connecting verified blood donors to patients in urgent need — built for real impact.*

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-red?style=flat-square)](LICENSE)

<br/>

[**Live API →**](https://hemo.railway.app/docs) · [**Architecture**](#architecture) · [**Quick Start**](#quick-start) · [**API Reference**](#api-reference)

<br/>

</div>

---

## The Problem

Every year, millions of people need blood transfusions. Hospitals face shortages daily. Willing donors exist nearby — but there's no fast, structured way to reach them.

WhatsApp forwards. Desperate Facebook posts. Families calling strangers at midnight.

**Hemo fixes this.**

---

## What Hemo Does

```
Patient needs blood  →  Create request  →  Matching engine finds eligible donors
                                                          ↓
Hospital donation  ←  Donor visits hospital  ←  Donor sees request & opts in
```

- A **requester** posts a blood request with hospital name, blood group, and urgency
- The **matching engine** finds eligible donors by blood group, city, and 90-day eligibility rules
- Matched **donors** receive a notification and choose to volunteer
- Contact is shared **only after opt-in** — never automatically
- After donation, the donor's eligibility is **locked for 90 days**

> **Hemo is a connector, not a medical authority.** All donations occur at registered hospitals. The app never approves donors medically.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│              Web App  ·  Mobile App  ·  Swagger UI             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
┌────────────────────────────▼────────────────────────────────────┐
│                      FastAPI Backend                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Auth Routes │  │ Donor Routes │  │   Request Routes     │  │
│  │  /auth/*     │  │ /donors/*    │  │   /requests/*        │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         └─────────────────▼──────────────────────┘             │
│                    Service Layer                                │
│         ┌──────────────────┐  ┌────────────────────┐           │
│         │ EligibilityService│  │  MatchingService   │           │
│         │  (pure logic)    │  │  (score & rank)    │           │
│         └──────────────────┘  └────────────────────┘           │
└───────────┬──────────────────────────┬──────────────────────────┘
            │                          │
┌───────────▼──────────┐  ┌───────────▼──────────────────────────┐
│     PostgreSQL 15    │  │              Redis 7                  │
│                      │  │                                       │
│  • users             │  │  • Donor search cache  (TTL 60s)     │
│  • donor_profiles    │  │  • Rate limiting       (sliding)     │
│  • blood_requests    │  │  • Celery task broker                │
│  • donor_volunteers  │  └───────────────────────────────────────┘
│  • donations         │
└──────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────────────┐
│                     Celery Workers                               │
│   Donor match notifications  ·  Opt-in alerts  ·  Thank-you emails │
└──────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Async FastAPI + asyncpg** | Non-blocking I/O handles burst traffic (emergencies create spikes) without adding servers |
| **Service layer isolation** | `eligibility.py` and `matching.py` are pure Python — no FastAPI imports, testable in isolation |
| **Opt-in contact sharing** | Donor phone numbers are never exposed in search results. Shared only after explicit volunteer action |
| **90-day eligibility lock** | Enforced at the DB level via `next_eligible_date`, not just application logic |
| **Redis cache-aside** | Donor matching is the hottest query path — cached with 60s TTL, invalidated on profile update |
| **JWT access + refresh tokens** | 15-minute access tokens limit blast radius of theft. Refresh rotation on every use |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **API Framework** | FastAPI 0.111 (async) |
| **Language** | Python 3.11+ |
| **Database** | PostgreSQL 15 + SQLAlchemy 2.0 (async) |
| **Migrations** | Alembic |
| **Validation** | Pydantic v2 |
| **Auth** | JWT (python-jose) + bcrypt (passlib) |
| **Cache & Rate Limiting** | Redis 7 |
| **Background Tasks** | Celery + Redis broker |
| **Email** | SendGrid |
| **Error Tracking** | Sentry |
| **Containerisation** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |
| **Hosting** | Railway |

---

## Project Structure

```
hemo/
├── app/
│   ├── main.py                  # FastAPI app, middleware, router registration
│   ├── config.py                # Settings via Pydantic BaseSettings, reads .env
│   ├── database.py              # Async SQLAlchemy engine + session factory
│   │
│   ├── models/
│   │   ├── user.py              # User (id, email, password_hash, role, is_active)
│   │   ├── donor.py             # DonorProfile (blood_group, city, age, eligibility)
│   │   ├── request.py           # BloodRequest + DonorVolunteer
│   │   └── donation.py          # Donation history
│   │
│   ├── schemas/
│   │   ├── auth.py              # RegisterRequest, LoginResponse, TokenResponse
│   │   ├── donor.py             # DonorProfileCreate, DonorSummary (no contacts)
│   │   └── request.py           # RequestCreate, MatchResult
│   │
│   ├── routes/
│   │   ├── auth.py              # POST /auth/register, /login, /refresh
│   │   ├── donors.py            # GET/PUT /donors/profile/me
│   │   ├── requests.py          # POST /requests, GET /requests/{id}/matches
│   │   └── admin.py             # GET /admin/stats
│   │
│   ├── services/
│   │   ├── eligibility.py       # Pure eligibility logic — zero FastAPI imports
│   │   ├── matching.py          # Donor scoring and ranking
│   │   └── notification.py      # Celery tasks for email/SMS
│   │
│   └── core/
│       ├── auth.py              # JWT create/verify
│       ├── security.py          # bcrypt hash/verify
│       └── deps.py              # Depends() guards: require_donor, require_requester
│
├── tests/
│   ├── test_eligibility.py      # Unit tests — pure logic, no DB
│   ├── test_matching.py
│   └── test_auth.py             # Integration tests with httpx
│
├── alembic/                     # Database migrations
├── .github/workflows/ci.yml     # Run pytest on every push
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Git

### 1. Clone and configure

```bash
git clone https://github.com/gaus13/hemo.git
cd hemo
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql+asyncpg://hemo:secret@postgres:5432/hemo
REDIS_URL=redis://redis:6379
SECRET_KEY=your-256-bit-secret-key-here
SENDGRID_API_KEY=your-sendgrid-key
SENTRY_DSN=your-sentry-dsn
```

### 2. Start everything

```bash
docker compose up --build
```

This starts:
- **FastAPI** on `http://localhost:8000`
- **PostgreSQL** on port `5432`
- **Redis** on port `6379`
- **Celery worker** for background notifications

### 3. Run migrations

```bash
docker compose exec app alembic upgrade head
```

### 4. Open Swagger

```
http://localhost:8000/docs
```

All 18 endpoints are documented and testable from the browser.

---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register donor or requester | Public |
| `POST` | `/api/v1/auth/login` | Login, receive JWT tokens | Public |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | Public |
| `POST` | `/api/v1/auth/logout` | Revoke refresh token | Bearer |

### Donors

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/donors/profile` | Create donor profile | DONOR |
| `GET` | `/api/v1/donors/profile/me` | Get own profile + eligibility | DONOR |
| `PUT` | `/api/v1/donors/profile/me` | Update city, availability, etc | DONOR |
| `GET` | `/api/v1/donors/{id}/summary` | Public donor summary (no contact) | Bearer |

### Blood Requests

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/requests` | Create blood request (hospital required) | REQUESTER |
| `GET` | `/api/v1/requests` | List open requests, filter by city/group | Bearer |
| `GET` | `/api/v1/requests/{id}` | Full request details | Bearer |
| `GET` | `/api/v1/requests/{id}/matches` | Ranked eligible donors (no contacts) | REQUESTER |
| `POST` | `/api/v1/requests/{id}/volunteer` | Donor opts in — contact revealed | DONOR |
| `PATCH` | `/api/v1/requests/{id}/status` | Mark fulfilled or cancelled | REQUESTER |

### Donations

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/donations/complete` | Record donation, lock 90-day eligibility | DONOR |
| `GET` | `/api/v1/donations/history` | Full donation history + badges | DONOR |

### Utility

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/health` | Health check + DB status | Public |
| `GET` | `/api/v1/admin/stats` | Platform analytics | ADMIN |
| `GET` | `/api/v1/about/safety` | Safety disclaimer | Public |

---

## Core Business Logic

### Eligibility Engine

`app/services/eligibility.py` — zero FastAPI imports. Pure Python. Independently testable.

```python
def check_eligibility(
    age: int,
    last_donation: date | None,
    available: bool,
    declared: bool
) -> EligibilityResult:
```

| Rule | Condition | Failure reason |
|---|---|---|
| Age check | 18 ≤ age ≤ 60 | `age_out_of_range` |
| Donation gap | today − last_donation ≥ 90 days | `too_soon` |
| Availability | `available == True` | `unavailable` |
| Declaration | `self_declaration == True` | `no_declaration` |

### Matching Engine

`app/services/matching.py` — finds and scores eligible donors for a blood request.

```
1. Filter:  blood_group = request.blood_group AND city = request.city
2. Filter:  eligibility_service.check() passes
3. Score:   score = 100 − days_since_eligible + availability_bonus
4. Sort:    ORDER BY score DESC
5. Return:  donor summaries only (name, blood_group, city) — never phone number
```

Results are cached in Redis with a 60-second TTL and invalidated on any donor profile update.

---

## Safety

Hemo is built with a privacy-first, safety-first model:

- **No auto-contact sharing** — donor phone numbers are never in search results
- **Explicit opt-in** — donors read the full request and actively choose to help
- **Hospital-only donations** — `hospital_name` is a required field, validated server-side
- **No medical approval** — Hemo checks self-declared eligibility only; hospitals handle medical screening
- **Rate limiting** — 10 requests/minute per IP, 100/hour per authenticated user
- **Disclaimer endpoints** — `/about/safety` and `/about/disclaimer` are public and linked from every response

---

## Testing

```bash
# Run the full test suite
pytest tests/ -v

# Unit tests only (no DB required)
pytest tests/test_eligibility.py tests/test_matching.py -v

# Integration tests
pytest tests/test_auth.py -v --asyncio-mode=auto
```

Test coverage targets:

| Module | Coverage | Focus |
|---|---|---|
| `eligibility.py` | 100% | Age boundary, 90-day exact, all rules |
| `matching.py` | 95%+ | Blood group filter, ineligible exclusion, scoring |
| Auth flow | 90%+ | Register → login → protected route → 401/403 |

GitHub Actions runs the full suite on every push and blocks merge if tests fail.

---

## Deployment

### Railway (recommended — free tier)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway up
```

Add environment variables in the Railway dashboard. PostgreSQL and Redis are available as one-click addons.

### Environment variables required

```env
DATABASE_URL      # postgresql+asyncpg://...
REDIS_URL         # redis://...
SECRET_KEY        # 256-bit random string
SENDGRID_API_KEY  # for email notifications
SENTRY_DSN        # for error tracking
ENVIRONMENT       # production
```

---

## Roadmap

- [x] Core matching engine with eligibility scoring
- [x] JWT auth with refresh token rotation
- [x] Opt-in contact sharing
- [x] Async notifications via Celery + SendGrid
- [x] Redis caching + rate limiting
- [x] Docker Compose local dev setup
- [x] GitHub Actions CI
- [ ] WebSocket real-time alerts for matched donors
- [ ] Donation history badges (First Drop, Hero, Lifesaver)
- [ ] Hospital verification layer
- [ ] PostGIS geo-radius matching (replace city-based)
- [ ] Hindi / Bengali / Tamil language support
- [ ] Mobile app (React Native)

---

## Why Hemo?

*Hemo* comes from the Greek *haima* — blood. Short, medical, real.

This project was built to solve an actual problem that kills people in India every day. It is not a tutorial project or a CRUD demo. It is a complete backend system with a matching engine, a privacy model, async task processing, a caching layer, role-based auth, and a test suite — deployed and live.

If you want to contribute, open an issue. If you want to fork it and deploy it in your city, go ahead. The code is MIT licensed.

---

## Contributing

```bash
# Fork the repo
# Create a feature branch
git checkout -b feature/geo-radius-matching

# Make changes, write tests
pytest tests/ -v

# Push and open a PR
git push origin feature/geo-radius-matching
```

All PRs must pass the full test suite. Business logic changes require tests.

---

## Author

**Gulam Gaus** ([@gaus13](https://github.com/gaus13))

Backend & DevOps Engineer

---

<div align="center">

**Hemo** · MIT License · Built in India

*Every unit of blood you find is a life you keep.*

</div>
