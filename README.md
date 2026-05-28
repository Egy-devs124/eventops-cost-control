# EventOps Cost Control System

ERP-style web application for replacing Excel-based event installation cost control, payments, stock reservations, payroll, reports, and cashbox tracking.

## Stack

- Backend: Django, Django REST Framework, JWT auth, drf-spectacular Swagger, SQLite by default, PostgreSQL-ready settings.
- Frontend: React + Vite, React Router, Axios, responsive admin UI, Arabic/English switch, RTL, dark/light theme.
- Demo login after seeding: `owner@example.com / Admin12345`.

## Quick Start

```powershell
cd backend
python -m pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py reset_demo_data
python manage.py seed_eventops_demo
python manage.py runserver
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/api/docs/`
- Django admin: `http://localhost:8000/admin/`

## Main Modules

Clients, orders/jobs, quotations, inventory, vendors, drivers, staff, payroll, finance, cashboxes, invoices, reports, attachments, notifications, audit logs, roles, and user profiles.

The backend keeps business rules in services, including stock reservation, availability checks, cashbox balance, invoice payment status, payroll calculation, and job profitability.

## Development Notes

Local apps are migration-light for fast setup. Use `python manage.py migrate --run-syncdb` in development. For production, generate normal migrations and set `DB_ENGINE=postgres` with the PostgreSQL variables from `backend/.env.example`.

## Railway Backend Deployment

Backend deployment is prepared for Railway with:

- `backend/Procfile` (Gunicorn startup + migrations)
- `DATABASE_URL` support for Railway PostgreSQL
- production security settings enabled when `DJANGO_DEBUG=False`

See `backend/README.md` for full deployment steps and required environment variables.
