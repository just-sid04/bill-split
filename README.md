# Bill Split & Settlement System

A small financial system for tracking shared expenses, computing balances, simplifying debts, and enforcing structured settlements.

Built as part of the Associate Software Engineer assessment.

---

# 1. Problem

When multiple people share expenses (e.g., trips, rent, meals), tracking who owes whom becomes increasingly complex as transactions grow.

This system provides:

- Expense creation
- Balance computation
- Deterministic debt simplification
- Structured settlement lifecycle
- Financial correctness guarantees

The focus is structural clarity, correctness, and safe evolution — not feature count.

---

# 2. Tech Stack

## Backend
- Python
- Flask (Application Factory Pattern)
- SQLAlchemy (Relational ORM)
- Decimal for financial precision

## Frontend
- React
- API abstraction layer

## Database
- SQLite (development & testing)

## Testing
- Pytest
- In-memory SQLite for isolated, repeatable test runs

---

# 3. How To Run

## Backend

    cd backend
    pip install -r requirements.txt
    flask run

Runs on:
    http://localhost:5000

---

## Frontend

    cd frontend
    npm install
    npm start

Runs on:
    http://localhost:3000

---

## Run Tests

    cd backend
    pytest

All tests should pass successfully.

---

# 4. Architecture Overview

## Backend Structure

    app/
    ├── models/
    ├── services/
    ├── routes/
    ├── extensions.py
    └── __init__.py (Application Factory)

### Service Layer Separation

All business logic resides in the service layer.

Routes:
- Validate input
- Delegate to services
- Return structured JSON responses

Routes do not contain financial logic.

This separation prevents logic leakage and improves maintainability and change resilience.

---

### Application Factory Pattern

The application uses a create_app() factory.

Benefits:
- Clean configuration management
- Test isolation
- Extension initialization control
- Environment flexibility

---

# 5. Financial Correctness

## Why Decimal?

All financial values use Decimal, not float.

Reason:
- Prevents floating point rounding errors
- Ensures deterministic calculations
- Protects accounting invariants

---

## Core System Invariants

1. The sum of all group balances must always equal zero.
2. All financial calculations use Decimal.
3. Settlement lifecycle must follow controlled state transitions.
4. Simplified debts must preserve net balances.
5. Business logic must not exist in route handlers.

These invariants are enforced structurally and verified through automated tests.

---

# 6. Debt Simplification Strategy

Balances are computed first.

A deterministic simplification algorithm then:

- Matches debtors to creditors
- Reduces the number of transactions
- Preserves total accounting integrity

The algorithm prioritizes clarity and determinism over theoretical optimal complexity.

---

# 7. Settlement Lifecycle

Settlements move through controlled states:

- proposed
- confirmed
- completed
- disputed

Invalid transitions are rejected.

This prevents inconsistent financial states.

Both expense-linked settlements and direct group-level settlements are supported.

---

# 8. Verification Strategy

The system includes automated tests verifying:

- Zero-sum invariant preservation
- Settlement lifecycle enforcement
- Debt simplification behavior
- Validation rule enforcement

Tests run against an in-memory database to ensure repeatability and isolation.

Verification focuses on behavior and invariants — not implementation details.

---

# 9. Observability

- Structured JSON API responses
- Meaningful HTTP status codes
- Clear validation error messages
- Frontend surfaces backend failures
- CORS configured for controlled cross-origin access

Failures are visible and diagnosable.

---

# 10. Change Resilience

The system is structured so that:

- New financial rules do not affect routing logic.
- Algorithm changes are isolated to services.
- UI changes do not impact backend invariants.
- New endpoints do not require cross-layer refactoring.

The architecture supports safe incremental evolution.

---

# 11. AI Usage

AI tools were used to:

- Explore architectural tradeoffs
- Validate financial edge cases
- Stress-test invariant enforcement
- Improve structural clarity

All AI-generated suggestions were manually reviewed and verified.

AI was treated as an assistant — not an authority.

---

# 12. Tradeoffs

- Prioritized structural clarity over UI polish.
- Focused on correctness over feature breadth.
- No authentication layer (out of scope for this assessment).
- Simplification algorithm optimized for determinism, not global optimality.

---

# 13. Possible Extensions

- Recurring expenses
- Partial settlements
- Multi-currency support
- Authentication & authorization
- Audit logs
- Real-time updates

The current architecture supports these without major refactoring.

---

# Conclusion

This system prioritizes:

- Simplicity over cleverness
- Correctness over speed
- Structure over feature volume
- Verification over assumption

It demonstrates how small systems can remain understandable, deterministic, and resilient as they evolve.