# Contributing to Restaurant Automation System

This repository contains a Django REST Framework backend and React frontend for restaurant operations.

## Getting started

Follow the setup instructions in [README.md](README.md). Make changes in a feature branch and keep pull requests focused.

## What to test

- Run `python manage.py check` and the existing Django test suite from the backend project directory.
- Run the frontend's configured build/test commands when changing React code.
- If changing models, include and verify migrations against a fresh development database.
- Test permissions for manager, waiter, cashier, and other relevant roles.
- For order changes, check status transitions, totals, and inventory effects.
- For payment changes, verify that duplicate submissions cannot create duplicate receipts or payments.

## Data and security

Never commit production credentials, customer information, payment details, or real business records. Use synthetic fixtures for examples. Do not bypass authentication or role checks to make a UI flow appear to work.

## Pull request checklist

- [ ] Change and affected roles explained
- [ ] Backend checks/tests run
- [ ] Migrations verified if applicable
- [ ] Frontend checks run if applicable
- [ ] Screenshots supplied for UI changes
- [ ] No secrets or sensitive data included
