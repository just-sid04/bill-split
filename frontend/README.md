# Bill Split & Settlement System

A small financial system for tracking shared expenses, computing balances, and simplifying debt settlements.

Built as part of an Associate Software Engineer assessment.

---

## 🧠 Problem

Groups frequently share expenses (trips, rent, meals, etc.).  
Tracking who owes whom becomes complex as expenses grow.

This system provides:

- Expense creation
- Balance computation
- Debt simplification
- Settlement lifecycle management
- Deterministic financial correctness

---

## 🏗 Tech Stack

Backend:
- Python
- Flask (Factory pattern + Blueprints)
- SQLAlchemy
- Relational Database
- Decimal for financial precision

Frontend:
- React
- API abstraction layer

Database:
- Relational (SQLAlchemy ORM)

---

## 🧱 Architecture

### Backend Structure

### Key Design Decisions

### 1️⃣ Service Layer Separation

Business logic is isolated in services.

Routes only:
- Validate request
- Call service
- Return response

This prevents logic scattering and improves change resilience.

---

### 2️⃣ Application Factory Pattern

The system uses a `create_app()` factory.

Benefits:
- Clear initialization flow
- Environment flexibility
- Easy testability
- Clean extension registration

---

### 3️⃣ Decimal for Financial Precision

All financial values use `Decimal`, not float.

Reason:
- Prevents floating point rounding errors
- Ensures deterministic financial math
- Preserves invariant correctness

---

### 4️⃣ Settlement Lifecycle (Enum-Based)

Settlements move through controlled states:

- proposed
- confirmed
- completed
- disputed

Invalid transitions are not allowed.

This prevents inconsistent financial states.

---

### 5️⃣ Debt Simplification Algorithm

Balances are computed first.

Then a deterministic simplification algorithm:
- Matches largest debtors to largest creditors
- Minimizes transaction count
- Preserves zero-sum invariant

System invariant:
Total balances always sum to zero.

---

## 🔒 System Invariants

1. Sum of all balances = 0  
2. All financial values use Decimal  
3. Settlements cannot skip lifecycle states  
4. Simplified debts preserve net balances  
5. Business logic does not exist in route handlers  

---

## 🔄 Change Resilience

The system is designed so that:

- Adding new expense types does not impact settlement logic
- Changing debt simplification algorithm does not impact API layer
- UI changes do not affect backend invariants
- Financial rules are centralized in services

---

## 🧪 Verification Strategy

The system is structured to support automated tests.

Key behaviors verified:

- Expense creation correctness
- Balance computation accuracy
- Settlement lifecycle enforcement
- Debt simplification consistency
- Zero-sum invariant preservation

---

## 📊 Observability

- API returns structured JSON responses
- HTTP status codes reflect failure states
- Errors are surfaced to frontend clearly
- CORS configured for controlled access

---

## 🤖 AI Usage

AI tools were used to:
- Explore architectural tradeoffs
- Review edge cases in financial math
- Validate lifecycle constraints

All AI-generated code was manually reviewed and tested.

AI was treated as a collaborator, not an authority.

---

## ⚠️ Tradeoffs

- Focused on structural correctness over feature count
- UI intentionally minimal
- No authentication layer (out of scope)
- Simplification algorithm prioritizes determinism over optimal complexity

---

## 🚀 Possible Extensions

- Recurring expenses
- Partial settlements
- Multi-currency support
- Authentication & authorization
- Real-time updates
- Audit logs

The current structure supports these without major refactoring.

---

## 🏁 Conclusion

This system prioritizes:

- Correctness over cleverness
- Structure over feature volume
- Determinism over complexity
- Change resilience over quick hacks

It demonstrates how small systems can be designed safely and predictably.