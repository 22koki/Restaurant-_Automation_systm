# Restaurant Automation System

A full-stack restaurant operations platform built with Django REST Framework and React.

## Current foundation

The existing system supports menu items, orders, recipe ingredients, inventory, purchase orders, invoices, cheques, low-stock alerts, and basic reporting models.

Phase 1 focuses on stabilizing this foundation before the product expands into POS, table management, kitchen display, reservations, payments, customer ordering, staff workflows, and analytics.

## Architecture

- Backend: Django + Django REST Framework
- Frontend: React
- Development database: SQLite
- API client: Axios

## Local setup

### Backend

1. Create and activate a virtual environment.
2. Install the project dependencies.
3. Copy the values from `.env.example` into your local environment.
4. Run migrations.
5. Start Django with `python manage.py runserver`.

### Frontend

1. Enter `restaurant_automation_system/ras-frontend`.
2. Run `npm install`.
3. Set `REACT_APP_API_URL` if the backend is not at the default local URL.
4. Run `npm start`.

## Product direction

The target product connects customer ordering, POS, tables, kitchen operations, inventory, payments, reservations, staff workflows, and management reporting in one restaurant operating system.
