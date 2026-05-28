# EventOps Backend

## Setup

```powershell
python -m pip install -r requirements.txt
copy .env.example .env
python manage.py migrate --run-syncdb
python manage.py reset_demo_data
python manage.py seed_eventops_demo
python manage.py runserver
```

Demo users use password `Admin12345`. Usernames are emails:

`owner@example.com`, `admin@example.com`, `sales@example.com`, `operations@example.com`, `accountant@example.com`, `technician@example.com`, `driver@example.com`, `cashier@example.com`, `viewer@example.com`.

To reset and reseed in one step:

```powershell
python manage.py seed_eventops_demo --reset
```

## API

- JWT login: `POST /api/auth/login/`
- Current user: `GET /api/auth/me/`
- Swagger UI: `GET /api/docs/`
- Schema: `GET /api/schema/`

Examples:

```http
POST /api/auth/login/
Content-Type: application/json

{"username": "owner@example.com", "password": "Admin12345"}
```

```http
GET /api/orders/1/profitability/
Authorization: Bearer <access-token>
```

```http
POST /api/orders/1/confirm/
Authorization: Bearer <access-token>
Content-Type: application/json

{"manager_override": false}
```

## Important Endpoints

- `/api/clients/`
- `/api/orders/`
- `/api/orders/{id}/confirm/`
- `/api/orders/{id}/close/`
- `/api/orders/{id}/profitability/`
- `/api/quotations/`
- `/api/quotations/{id}/convert-to-order/`
- `/api/items/`
- `/api/items/availability/`
- `/api/lookups/clients/`
- `/api/lookups/items/`
- `/api/lookups/item-categories/`
- `/api/lookups/vendors/`
- `/api/lookups/drivers/`
- `/api/lookups/staff/`
- `/api/lookups/orders/`
- `/api/lookups/invoices/`
- `/api/lookups/payment-methods/`
- `/api/lookups/expense-categories/`
- `/api/lookups/cashboxes/`
- `/api/vendors/`
- `/api/drivers/`
- `/api/staff/`
- `/api/payroll/`
- `/api/finance/payments/` and alias `/api/payments/`
- `/api/finance/expenses/` and alias `/api/expenses/`
- `/api/finance/cashboxes/` and alias `/api/cashboxes/`
- `/api/finance/invoices/` and alias `/api/invoices/`
- `/api/reports/dashboard/`
- `/api/reports/revenue/`
- `/api/reports/profit/`
- `/api/reports/client-balances/`
- `/api/reports/vendor-balances/`
- `/api/reports/export/?report=profit&file_format=csv`
- `/api/reports/export/?report=profit&file_format=xlsx`

## Tests

```powershell
python manage.py test
```

Covered business logic includes inventory reservation/double-booking prevention, manager override, job profitability, and cashbox balance.

## PostgreSQL

SQLite is default. To switch later:

```env
DB_ENGINE=postgres
DB_NAME=eventops
DB_USER=eventops
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## Deploy Backend To Railway

1. Create a Railway project and link this GitHub repository.
2. In Railway service settings, set **Root Directory** to `backend`.
3. Add a PostgreSQL service in Railway and attach it to the backend service.
4. Set environment variables for backend service:

```env
DJANGO_SECRET_KEY=<strong-random-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<your-railway-domain>
CORS_ALLOWED_ORIGINS=<frontend-url>
CSRF_TRUSTED_ORIGINS=https://<your-railway-domain>,<frontend-url>
DATABASE_URL=<provided-by-railway-postgres>
DB_SSL_REQUIRE=True
```

Railway will use `Procfile` to run migrations and start Gunicorn automatically.
