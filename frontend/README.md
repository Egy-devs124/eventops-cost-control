# EventOps Frontend

## Setup

```powershell
npm install
copy .env.example .env
npm run dev
```

Open `http://localhost:5173`.

Demo login: `owner@example.com / Admin12345`.

The frontend expects the backend at:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Features

- JWT login/logout and current-user profile.
- Role-aware sidebar navigation.
- Responsive admin layout for desktop, tablet, and mobile.
- Arabic/English switch with RTL support.
- Dark/light theme switch stored in local storage.
- Dashboard cards and charts connected to `/api/reports/dashboard/`.
- CRUD screens connected to the backend for clients, orders, quotations, inventory, vendors, drivers, staff, payroll, finance, notifications, and reports.
- Create/edit forms use lookup dropdowns for related records while still submitting IDs to the API.
- Order details tabs for overview, items, costs, payments, staff, vendors, drivers, timeline, and profitability when permitted.
- CSV, Excel, and browser-print report outputs.

## Build

```powershell
npm run build
```
