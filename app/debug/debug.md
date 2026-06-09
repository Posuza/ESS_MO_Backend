# PBAC Backend — Full Debug Report

> Generated: 2026-06-07
> Project: `backEnd/`

---

## 1. Project Structure

```
backEnd/app/
├── __init__.py                    # Module marker
├── main.py                       # FastAPI app entrypoint
├── debug.md                      # THIS FILE
│
├── api/
│   ├── __init__.py
│   ├── dependencies.py           # @active_employee_required, @roles_required, @permissions_required
│   └── endpoints/
│       ├── __init__.py           # Routes aggregated into api_router
│       ├── auth.py               # POST /auth/register, /auth/login, /auth/logout, /auth/forgot-password, /auth/change-password
│       └── mo_daily_transactions.py  # CRUD /mo-daily-transactions
│
├── core/
│   ├── __init__.py
│   ├── audit_logger.py           # _AuditWrapper, contextvars, fire-and-forget threading
│   ├── config.py                 # Settings from .env (DB, SMTP, JWT, MFA)
│   ├── orm.py                    # Re-exports Base from db.engine
│   ├── db/
│   │   ├── __init__.py
│   │   ├── engine.py             # SQLAlchemy engine, SessionLocal, Base, DATABASE_URL builder
│   │   ├── session.py            # get_db (FastAPI dep), get_session (context manager), port check
│   │   └── db_error_handler.py   # DatabaseErrorMiddleware — catches SQL errors globally
│   ├── registries/
│   │   ├── __init__.py           # Re-exports all message constants
│   │   ├── auth_message.py       # Auth errors + audit action templates
│   │   ├── backend_message.py    # 5xx server error messages
│   │   ├── client_message.py     # 4xx client error messages
│   │   └── database_message.py   # DB connection/query/data messages
│   └── security/
│       ├── __init__.py
│       ├── auth.py               # get_password_hash, verify_password (bcrypt via passlib)
│       ├── request_actor.py      # extract_actor_employee_code from headers
│       └── reset_password.py     # (placeholder for token-based reset)
│
├── models/                       # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── addresses.py, audit_logs.py, departments.py, districts.py, divisions.py
│   ├── employee_permissions.py, employees.py, fields.py
│   ├── mo_daily_transaction_detail_1.py, mo_daily_transaction_detail_2.py
│   ├── mo_daily_transactions.py, name_prefixs.py, position_change_logs.py
│   ├── positions.py, postal_codes.py, provinces.py, roles.py
│   ├── route_change_logs.py, routes.py, shifts.py, sub_districts.py
│
├── schemas/                      # Pydantic request/response models
│   ├── __init__.py
│   ├── addresses.py, audit_logs.py, auth.py, departments.py, districts.py
│   ├── divisions.py, employee_permissions.py, employees.py, fields.py
│   ├── mo_daily_transactions.py, name_prefixs.py, position_change_logs.py
│   ├── positions.py, postal_codes.py, provinces.py, routes.py, sub_districts.py
│
└── services/                     # Business logic
    ├── __init__.py
    ├── addresses.py, audit_logs.py, auth.py, departments.py, districts.py
    ├── divisions.py, email.py, employee_permissions.py, employees.py
    ├── fields.py, mo_daily_transactions.py, name_prefixs.py
    ├── position_change_logs.py, positions.py, postal_codes.py
    ├── provinces.py, routes.py, sub_districts.py
```

---

## 2. Database Connection

### 2.1 Engine (`core/db/engine.py`)

| Setting | Source | Default |
|---------|--------|---------|
| `DB_ENGINE` | `.env` | `mysql` (or `sqlite`) |
| `DB_HOST` | `.env` | `localhost` |
| `DB_PORT` | `.env` | `3306` |
| `DB_USER` | `.env` | `root` |
| `DB_PASSWORD` | `.env` | (empty) |
| `DB_NAME` | `.env` | `pbac_db` |
| `SQLITE_PATH` | `.env` | `pbac.db` |

**URL Builder Logic:**
```python
if DB_ENGINE == "sqlite":
    url = f"sqlite:///{SQLITE_PATH}"
else:
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
```

**Engine kwargs:**
- SQLite: `{"future": True}`
- MySQL: `{"future": True, "pool_pre_ping": True, "connect_args": {"connect_timeout": 3}}`

### 2.2 Session (`core/db/session.py`)

Two ways to get a DB session:

| Method | Type | Use case |
|--------|------|----------|
| `get_db()` | FastAPI `Depends` generator | Endpoints |
| `get_session()` | `@contextmanager` | Services that manage their own session |

**Pre-flight check:** `_is_db_port_open(timeout=0.3)` does a TCP socket check before connecting.

**Error handling:**
- `HTTPException(503)` with `DATABASE_ERROR_CONNECTION_FAILED` if port unreachable
- `HTTPException(503)` with `DATABASE_ERROR_HOST_BLOCKED` if error contains "1129" or "blocked"

### 2.3 Error Handler Middleware (`core/db/db_error_handler.py`)

`DatabaseErrorMiddleware` catches at the middleware level:

| Exception | Status | Detail |
|-----------|--------|--------|
| `OperationalError` / `InterfaceError` / `DBAPIError` / `DatabaseError` | 503 | `DATABASE_ERROR_CONNECTION_FAILED` or `DATABASE_ERROR_HOST_BLOCKED` |
| `IntegrityError` (duplicate) | 409 | `"Duplicate entry detected"` |
| `IntegrityError` (other) | 500 | `DATABASE_ERROR_DATA_CORRUPTION` |
| `DataError` | 500 | `DATABASE_ERROR_QUERY_ERROR` |
| `SQLTimeoutError` | 503 | `DATABASE_ERROR_CONNECTION_FAILED` |
| `HTTPException` | passthrough | re-raised |
| `Exception` (unexpected) | 500 | `DATABASE_ERROR_QUERY_ERROR` |

---

## 3. Audit Logger (`core/audit_logger.py`)

### 3.1 Architecture

```
Request → AuditContextMiddleware → set_audit_context(request, user_name="anonymous")
                                           ↓
                                  contextvars: _current_request
                                              _current_user_name
                                              _current_employee_code
                                           ↓
                                  Endpoint calls audit_logger.log(action=...)
                                           ↓
                                  _AuditWrapper.log() resolves context
                                           ↓
                                  Background thread → AuditLogService.create()
                                           ↓
                                  INSERT INTO audit_logs
```

### 3.2 Context Variables

| Variable | Set by | Default |
|----------|--------|---------|
| `_current_request` | `AuditContextMiddleware` | `None` |
| `_current_user_name` | `AuditContextMiddleware` → `"anonymous"` | `None` |
| `_current_employee_code` | `@active_employee_required` decorator | `None` |

### 3.3 IP Address Resolution

Format: `{client_ip}/{geo_info}/{device}`

| Component | Source | Example |
|-----------|--------|---------|
| Client IP | `X-Forwarded-For` or `request.client.host` | `171.6.207.133` |
| Geo | `X-Latitude` / `X-Longitude` or `X-Geo-Status` | `Latitude : 13.726 Longitude : 100.595` |
| Device | `User-Agent` header | `iPhone`, `Android`, `Desktop` |

### 3.4 Fire-and-Forget Behavior

```python
def _worker(p):
    try:
        _service.create(p)
    except Exception as exc:
        _logger.error("audit.log failed in background thread: %s", exc)

t = threading.Thread(target=_worker, args=(payload,), daemon=True)
t.start()
```

✅ **Threading is daemon** — won't block shutdown
✅ **Exception is caught** — audit failure never crashes the app
❌ **No retry** — if the DB insert fails, the log is silently lost
❌ **No request queue** — each log spawns a new thread (could be many)

---

## 4. Registry Messages

### 4.1 Auth Audit Actions (`registries/auth_message.py`)

These are the audit action template strings used with `audit_logger.log(action=...)`:

| Constant | Template | Where used |
|----------|----------|------------|
| `LOGIN_ATTEMPT` | `"{resource} Attempt to Login"` | `EmployeeAuthService.authenticate_employee` |
| `LOGIN_FAILED` | `"{resource} Login attempt failed"` | (available, not used yet) |
| `LOGIN_SUCCESS` | `"{resource} Login successful"` | `EmployeeAuthService.authenticate_employee` |
| `LOGOUT_ATTEMPT` | `"{resource} Attempt to Logout"` | (available, not used yet) |
| `LOGOUT_FAILED` | `"{resource} Logout failed"` | (available, not used yet) |
| `LOGOUT_SUCCESS` | `"{resource} Logout successful"` | `EmployeeAuthService.logout` |
| `FORGOT_PASSWORD_ATTEMPT` | `"{resource} attempted forgot-password request"` | `PasswordService.forgot_password` |
| `FORGOT_PASSWORD_FAILED` | `"{resource} Forgot-password request failed - {reason}"` | `PasswordService.forgot_password` |
| `FORGOT_PASSWORD_EMAIL_SENT` | `"{resource} Password reset email sent successfully to {email}"` | `PasswordService.forgot_password` |
| `CHANGE_PASSWORD_ATTEMPT` | `"{resource} attempted to change password"` | `PasswordService.change_password` |
| `CHANGE_PASSWORD_SUCCESS` | `"{resource} changed password successfully"` | `PasswordService.change_password` |
| `RESET_PASSWORD_SUCCESS` | `"Password reset successful"` | (available, not used yet) |
| `REGISTER` | `"{resource} registered successfully (code={employee_code})"` | `EmployeeAuthService.register_employee` |

### 4.2 Auth Error Messages (`registries/auth_message.py`)

| Constant | Message | Where used |
|----------|---------|------------|
| `AUTH_ERROR_UNAUTHORIZED` | `จำเป็นต้องยืนยันตัวตน...` | (available) |
| `AUTH_ERROR_FORBIDDEN` | `Access denied...` | `roles_required`, `permissions_required` |
| `AUTH_ERROR_TOKEN_EXPIRED` | `Session expired...` | (available) |
| `AUTH_ERROR_INVALID_CREDENTIALS` | `รหัสผ่านไม่ถูกต้อง` | `EmployeeAuthService.authenticate_employee` |
| `AUTH_ERROR_INVALID_OLD_PASSWORD` | `รหัสผ่านล่าสุดไม่ถูกต้อง` | `PasswordService.change_password` |
| `AUTH_ERROR_ACCOUNT_INACTIVE` | `Account is inactive...` | `EmployeeAuthService.authenticate_employee`, `_get_active_employee` |
| `AUTH_ERROR_ACCOUNT_INACTIVE_FORGOT_PASSWORD` | `Employee account is inactive...` | `PasswordService.forgot_password`, `PasswordService.change_password` |
| `AUTH_ERROR_ACCOUNT_LOCKED` | `Account is locked...` | (available) |
| `AUTH_ERROR_EMPLOYEE_NOT_FOUND` | `ไม่พบรหัสพนักงานในระบบ...` | All services, dependencies |
| `AUTH_ERROR_NO_EMAIL_REGISTERED` | `ไม่พบอีเมลที่ลงทะเบียนไว้...` | `PasswordService.forgot_password` |
| `ACCESS_DENIED_ROLE` | `Access denied: insufficient role` | `roles_required` |
| `ACCESS_DENIED_PERMISSION` | `Access denied: insufficient permissions` | `permissions_required` |
| `EMPLOYEE_NOT_FOUND` | `Employee not found` | `_get_active_employee` |
| `ACCOUNT_INACTIVE` | `Account is inactive` | `_get_active_employee` |

### 4.3 Client Error Messages (`registries/client_message.py`)

| Constant | Message | Where used |
|----------|---------|------------|
| `CLIENT_ERROR_BAD_REQUEST` | `The request was malformed...` | `PasswordService.change_password` |
| `CLIENT_ERROR_CONFLICT` | `Resource conflict detected...` | `EmployeeAuthService.register_employee` |
| `CLIENT_ERROR_NOT_FOUND` | (standard 404) | (available) |

### 4.4 Database Error Messages (`registries/database_message.py`)

| Constant | Message | Where used |
|----------|---------|------------|
| `DATABASE_ERROR_CONNECTION_FAILED` | `Database connection timeout...` | `session.py`, `db_error_handler.py` |
| `DATABASE_ERROR_HOST_BLOCKED` | `Database host is temporarily blocked...` | `session.py`, `db_error_handler.py` |
| `DATABASE_ERROR_QUERY_ERROR` | `Database query execution failed...` | `db_error_handler.py` |
| `DATABASE_ERROR_DATA_CORRUPTION` | `Data integrity check failed...` | `db_error_handler.py` |

### 4.5 Backend Error Messages (`registries/backend_message.py`)

| Constant | Message |
|----------|---------|
| `BACKEND_ERROR_INTERNAL` | `An unexpected internal server error occurred...` |
| `BACKEND_ERROR_NOT_IMPLEMENTED` | `This feature is not yet implemented...` |
| `BACKEND_ERROR_SERVICE_UNAVAILABLE` | `Server is temporarily offline...` |
| `BACKEND_ERROR_BAD_GATEWAY` | `Received an invalid response from the upstream server...` |

---

## 5. Dependencies (`api/dependencies.py`)

### 5.1 `active_employee_required` Decorator

**Flow:**
```
Request → extract_actor_employee_code(request)
              ↓
         Checks X-Employee-Code, X-User-Code, X-Actor-Code headers (regex: ^\d{6}$)
              ↓ fallback
         Bearer token (also treated as employee code in dev)
              ↓
         _get_active_employee(db, employee_code)
              ↓
         if not found → HTTPException(404) + audit_logger.log(EMPLOYEE_NOT_FOUND)
         if not active → HTTPException(403) + audit_logger.log(ACCOUNT_INACTIVE)
              ↓
         set_audit_context(request, user_name=full_name, employee_code=code)
              ↓
         kwargs["current_employee"] = employee ORM object
```

**Shortcomings:**
- ❌ Token is just raw employee code — no JWT, no signature, no expiry
- ❌ Any 6-digit string in headers authenticates as that employee
- ❌ No password verification at the decorator level (delegated to login endpoint)

### 5.2 `roles_required` Decorator

```python
@roles_required("admin")        # single role
@roles_required("admin", "manager")  # multiple
@roles_required(["admin", "manager"]) # list
```

- Reads `role_id` from `Employee`, joins `Role` to get `role_name`
- Audit on failure: `ACCESS_DENIED_ROLE` → `HTTPException(403)` with `AUTH_ERROR_FORBIDDEN`
- ⚠️ Must be stacked **below** `@active_employee_required`

### 5.3 `permissions_required` Decorator

```python
@permissions_required("reports.read")
@permissions_required("reports.read", "reports.write")
```

- Reads from `employee_permissions` table (active rows only)
- Audit on failure: `ACCESS_DENIED_PERMISSION` → `HTTPException(403)` with `AUTH_ERROR_FORBIDDEN`
- ⚠️ Must be stacked **below** `@active_employee_required`

---

## 6. Endpoints

### 6.1 Auth Endpoints (`api/endpoints/auth.py`)

| Method | Path | Schema (Request) | Schema (Response) | Auth | Service |
|--------|------|------------------|-------------------|------|---------|
| `POST` | `/auth/register` | `EmployeeRegister` | `EmployeeResponse` | None | `EmployeeAuthService.register_employee` |
| `POST` | `/auth/login` | `EmployeeLogin` | `LoginResponse` | None | `EmployeeAuthService.authenticate_employee` + `build_login_response` |
| `POST` | `/auth/logout` | — | `LogoutResponse` | `@active_employee_required` | `EmployeeAuthService.logout` |
| `POST` | `/auth/forgot-password` | `ForgotPasswordRequest` | `MessageResponse` | None | `PasswordService.forgot_password` |
| `POST` | `/auth/change-password` | `ChangePasswordRequest` | `MessageResponse` | `@active_employee_required` | `PasswordService.change_password` |

### 6.2 Mo Daily Transactions (`api/endpoints/mo_daily_transactions.py`)

| Method | Path | Schema (Request) | Schema (Response) | Auth | Service |
|--------|------|------------------|-------------------|------|---------|
| `GET` | `/mo-daily-transactions/` | query params | `List[MoDailyTransactionResponse]` | `@active_employee_required` | `MoDailyTransactionService.list_reports` |
| `POST` | `/mo-daily-transactions/` | `MoDailyTransactionCreate` | `MoDailyTransactionResponse` | `@active_employee_required` | `MoDailyTransactionService.create_report` |
| `GET` | `/mo-daily-transactions/{id}` | path param | `MoDailyTransactionResponse` | `@active_employee_required` | `MoDailyTransactionService.get_report` |
| `PATCH` | `/mo-daily-transactions/{id}` | `MoDailyTransactionUpdate` | `MoDailyTransactionResponse` | `@active_employee_required` | `MoDailyTransactionService.update_report` |
| `DELETE` | `/mo-daily-transactions/{id}` | path param | `200 OK` | `@active_employee_required` | `MoDailyTransactionService.delete_report` |

### 6.3 Global Routes (in `main.py`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root: `{"status": "healthy", ...}` |
| `GET` | `/api/v1/health` | Health check: `{"status": "ok"}` |

### 6.4 Router Prefix

All routes are mounted under `/api/v1`:
```python
app.include_router(api_router, prefix="/api/v1")
```

So the full path for login is: `POST /api/v1/auth/login`

---

## 7. Security (`core/security/`)

### 7.1 Password Hashing (`auth.py`)

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str    # bcrypt hash
def verify_password(plain: str, hashed: str) -> bool  # verify
```

✅ `bcrypt` via `passlib` — available and importable
❌ **Not used anywhere** in the service layer — passwords stored in plaintext
❌ `Employee.password` column is `String(6)` — too short for a bcrypt hash (need ~60 chars)

### 7.2 Request Actor (`request_actor.py`)

```python
def extract_actor_employee_code(request: Request) -> str:
    # Checks headers: X-Employee-Code, X-User-Code, X-Actor-Code
    # Fallback: Bearer token (treated as raw employee code)
    # Regex: ^\d{6}$
```

**Security issues:**
- ❌ **No JWT validation** — any 6-digit string in header = authenticated
- ❌ **No token expiry** — tokens never expire
- ❌ **No signature** — tokens can't be verified server-side

---

## 8. Email Service (`services/email.py`)

### 8.1 Configuration (from `.env`)

| Setting | Default | Required? |
|---------|---------|-----------|
| `SMTP_HOST` | `smtp.gmail.com` | Yes |
| `SMTP_PORT` | `587` | Yes |
| `SMTP_USER` | (empty) | Yes, for auth |
| `SMTP_PASS` | (empty) | Yes, for auth |
| `EMAIL_FROM` | (falls back to SMTP_USER) | Optional |

### 8.2 Functions

| Function | Trigger | Content |
|----------|---------|---------|
| `send_plain_password_email` | `forgot-password` | Plaintext password in email body |
| `send_change_password_notification_email` | `change-password` | New plaintext password in email body |

**⚠️ Security:** Both send passwords in plaintext over email — insecure by design (legacy mode).

### 8.3 SMTP Flow

```
smtplib.SMTP(host, port) → server.ehlo() → server.starttls()
→ server.login(user, pass) → server.sendmail(from, to, msg)
```

- ✅ STARTTLS enabled
- ⚠️ No timeout set on SMTP connection (could hang)
- ⚠️ Background task (fire-and-forget) — email failures are silent

---

## 9. Services

### 9.1 `EmployeeAuthService` (`services/auth.py`)

| Method | Audit | Error on |
|--------|-------|----------|
| `register_employee` | `REGISTER` on success | Duplicate employee_code or email → `409` |
| `authenticate_employee` | `LOGIN_ATTEMPT` always, `LOGIN_SUCCESS` on success | Not found → `404`, Wrong password → `401`, Inactive → `403` |
| `logout` | `LOGOUT_SUCCESS` | — |
| `build_login_response` | — | — |
| `get_employee_display_name` | — | — |

### 9.2 `PasswordService` (`services/auth.py`)

| Method | Audit | Error on |
|--------|-------|----------|
| `forgot_password` | `FORGOT_PASSWORD_ATTEMPT`, `FAILED` (with reason), `EMAIL_SENT` | Not found → `404`, Inactive → `403`, No email → `400` |
| `change_password` | `CHANGE_PASSWORD_ATTEMPT`, `CHANGE_PASSWORD_SUCCESS` | Not found → `404`, Inactive → `403`, Wrong old password → `401`, Same password → `400` |

### 9.3 `AuditLogService` (`services/audit_logs.py`)

| Method | Description |
|--------|-------------|
| `create(payload)` | Insert log entry (uses `get_session()` internally) |
| `list_logs(employee_code, limit, offset)` | Paginated list, newest first |
| `get(log_id)` | Single entry by PK |

---

## 10. Middleware Stack (in `main.py`)

Order of middleware execution:

```
Request
  ↓
1. CORSMiddleware          — allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
  ↓
2. AuditContextMiddleware  — set_audit_context(request, "anonymous")
  ↓
3. DatabaseErrorMiddleware — catch SQL errors → proper HTTP responses
  ↓
4. Route Handler           — process request
  ↓
5. AuditContextMiddleware  — clear_audit_context() on response
Response
```

---

## 11. Known Issues & Gaps

### 🔴 Critical
1. **No real auth** — employee code in header = full access. No JWT, no session, no password at decorator level.
2. **Passwords stored in plaintext** — `String(6)` column can't hold bcrypt hashes. Need schema migration.
3. **Audit logger is fire-and-forget in a thread** — if DB is down, audit logs are silently lost.

### 🟡 Medium
5. **`roles_required` / `permissions_required` not used** on any current endpoints.
6. **`mo_daily_transactions`** endpoints have no role/permission checks — any authenticated employee can CRUD.
7. **`ChangePasswordRequest` schema still has `employee_code`** field even though the endpoint gets it from `current_employee`.
8. **Audit context lost in background tasks** — `AuditContextMiddleware` clears context after response, so email audit logs show `anonymous`.

### 🟢 Low
9. **`LoginRequest`** (with `login` field) removed from schemas — make sure no other code imports it.
10. **`LOGIN_FAILED`, `LOGOUT_ATTEMPT`, `LOGOUT_FAILED`** constants defined but never used.
11. **`RESET_PASSWORD_SUCCESS`** constant defined but never used.
12. **`reset_password.py`** in security/ is likely a placeholder.

---

## 12. Quick Start Check

| Check | Command | Expected |
|-------|---------|----------|
| App imports | `python -c "from app.main import app"` | No ImportError |
| Schemas load | `python -c "from app.schemas.auth import EmployeeRegister"` | OK |
| Services load | `python -c "from app.services.auth import employee_auth_service"` | OK |
| Models load | `python -c "from app.models import employees"` | OK |
| DB engine | `python -c \"from app.core.db.engine import engine; print(engine.url)\"` | Shows DB URL |
| Config load | `python -c \"from app.core.config import settings; print(settings.DB_ENGINE)\"` | `mysql` or `sqlite` |
| DB connection test | `python -c \"from app.core.db.session import get_session; from app.core.db.engine import Base; print('Session factory OK')\"` | Session factory OK |
| DB tables sync (lifespan) | `python -c \"from app.main import app\"` | Warning logged if MySQL unreachable, app still starts |
