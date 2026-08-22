# Fix Log

This note records the issues found during the app startup review and the fixes applied.

## Confirmed issues

- [app/main.py](../app/main.py): `app.include_router(api_router)` ran before `app = FastAPI(...)`. That caused a startup `NameError` because the app object did not exist yet.
- [app/schemas/auth.py](../app/schemas/auth.py): `from typing import Optional, List, str` imported `str` from `typing`, which is invalid and prevented the schema module from loading.
- [app/services/blood_request_service.py](../app/services/blood_request_service.py): `BloodRequestCreate` and `BloodRequestUpdate` were imported from `app.schemas.request`, but those classes live in [app/schemas/bloodRequest.py](../app/schemas/bloodRequest.py).
- [app/database.py](../app/database.py): `get_db()` yielded `SessionLocal` instead of a real session from `SessionLocal()`, so dependency injection could not provide an actual database session.

## Environment issues found during validation

- `email-validator` was missing, which Pydantic needs for `EmailStr` in [app/schemas/auth.py](../app/schemas/auth.py).
- The argon2 backend for `pwdlib` was missing, which broke password hashing in [app/core/security.py](../app/core/security.py).

## Fixes applied

- Moved FastAPI app creation before router registration in [app/main.py](../app/main.py).
- Removed the invalid `str` import from [app/schemas/auth.py](../app/schemas/auth.py).
- Corrected the blood request schema import in [app/services/blood_request_service.py](../app/services/blood_request_service.py).
- Changed `get_db()` to create and yield a real SQLAlchemy session in [app/database.py](../app/database.py).
- Installed the missing runtime dependencies in the workspace virtual environment.

## Validation

- `from app.main import app` now succeeds in the workspace venv.
- The app title prints successfully as `Hemo`.

## Future Reference

- Workspace root: [c:/Users/Danish-PC/Desktop/Hemo](../)
- Python environment used for validation: `.venv` at [c:/Users/Danish-PC/Desktop/Hemo/.venv](../.venv)
- Verified run command: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` using the workspace venv interpreter.
- Verified healthy endpoints: `GET /health`, `GET /`, `GET /openapi.json`.
- Verified authenticated flows: `POST /auth/register`, `POST /auth/login`, `POST /requester/profile`, `GET /requester/profile/me`, `POST /blood-request`, `GET /blood-request/me`.
- Valid enum values for blood requests come from [app/models/enums.py](../app/models/enums.py): blood group values like `O+`, urgency values like `high`, and relationship values like `family`.
- Naming review: the backend is functionally consistent, but some filenames still use mixed casing such as [app/schemas/bloodRequest.py](../app/schemas/bloodRequest.py). Keep imports aligned with the current filenames unless you do a full rename pass.
- Next backend slice to validate: donor profile creation, volunteer acceptance, and donation-proof upload.
- Do not store bearer tokens or passwords here; only keep durable setup and validation facts.
- Automated backend flow tests live in [tests/test_backend_flow.py](../tests/test_backend_flow.py) and pass with `python -m unittest tests.test_backend_flow` from the workspace venv.
