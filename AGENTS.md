# AGENTS.md

AI Guidance & System Guardrails

This file defines constraints for AI-assisted development.

---

## 🔒 Core Invariants

1. All financial values must use Decimal.
2. Total group balance must always equal zero.
3. Settlement lifecycle must follow enum order.
4. Business logic must live in service layer only.
5. Routes must not contain financial logic.
6. No float usage in financial computations.
7. Deterministic outputs required for debt simplification.

---

## 🧱 Architectural Rules

- Do not move logic into Flask route handlers.
- Do not bypass service layer.
- Do not access database directly from routes.
- All new financial features must preserve zero-sum invariant.
- All new endpoints must return structured JSON.

---

## 🧪 Testing Requirements

For any financial modification:

- Add test verifying balance correctness.
- Add test verifying zero-sum invariant.
- Add test for invalid state transitions.

No financial feature should be added without verification.

---

## 🤖 AI Usage Constraints

When generating code:

- AI suggestions must be reviewed.
- Financial logic must be deterministic.
- No implicit type coercion allowed.
- No float arithmetic allowed.
- Simplicity preferred over abstraction.

AI is used to accelerate reasoning, not replace validation.

---

## 🔄 Change Safety

Before implementing new features:

- Identify impacted services.
- Verify invariants.
- Confirm lifecycle integrity.
- Ensure no cross-layer leakage.

---

This system prioritizes correctness, clarity, and controlled evolution.