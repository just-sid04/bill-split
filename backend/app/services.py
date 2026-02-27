from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict

from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from app.extensions import db
from app.models import (
    User, Group, Expense, Split, Settlement, RecurringRule,
    ExpenseStatus, SettlementStatus, GroupStatus
)
from app.utils import (
    simplify_debts, validate_split_total, calculate_group_balances
)


class ValidationError(Exception):
    pass


class NotFoundError(Exception):
    pass


class UserService:
    @staticmethod
    def create_user(name: str, email: str) -> User:
        if User.query.filter_by(email=email).first():
            raise ValidationError(f"User with email {email} already exists")

        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    @staticmethod
    def list_users() -> List[User]:
        return User.query.all()


class GroupService:
    @staticmethod
    def create_group(name: str, description: str, member_ids: List[int]) -> Group:
        group = Group(name=name, description=description)

        for member_id in member_ids:
            user = User.query.get(member_id)
            if not user:
                raise NotFoundError(f"User {member_id} not found")
            group.members.append(user)

        db.session.add(group)
        db.session.commit()
        return group

    @staticmethod
    def get_group(group_id: int) -> Optional[Group]:
        return Group.query.options(
            joinedload(Group.members),
            joinedload(Group.expenses).joinedload(Expense.splits),
            joinedload(Group.expenses).joinedload(Expense.paid_by_user)
        ).get(group_id)

    @staticmethod
    def list_groups() -> List[Group]:
        return Group.query.filter_by(status=GroupStatus.ACTIVE).all()

    @staticmethod
    def get_group_balances(group_id: int) -> Dict:
        group = GroupService.get_group(group_id)
        if not group:
            raise NotFoundError(f"Group {group_id} not found")

        # Get open / partially settled expenses
        expenses = Expense.query.filter(
            Expense.group_id == group_id,
            Expense.status.in_([ExpenseStatus.OPEN, ExpenseStatus.PARTIALLY_SETTLED])
        ).all()

        expense_ids = [e.id for e in expenses]

        # 🔥 FIX: Include BOTH expense-linked AND direct settlements
        settlements = Settlement.query.filter(
            Settlement.status == SettlementStatus.COMPLETED,
            or_(
                Settlement.expense_id.in_(expense_ids),
                Settlement.expense_id.is_(None)
            )
        ).all()

        # Calculate balances
        balances = calculate_group_balances(expenses, settlements)

        user_names = {u.id: u.name for u in group.members}

        balance_entries = [
            {
                "user_id": user_id,
                "user_name": user_names.get(user_id, "Unknown"),
                "net_balance": balance
            }
            for user_id, balance in balances.items()
        ]

        balance_entries.sort(key=lambda x: x["net_balance"], reverse=True)

        simplified = simplify_debts(balances)

        simplified_debts = [
            {
                "from_user_id": from_id,
                "from_user_name": user_names.get(from_id, "Unknown"),
                "to_user_id": to_id,
                "to_user_name": user_names.get(to_id, "Unknown"),
                "amount": amount
            }
            for from_id, to_id, amount in simplified
        ]

        return {
            "group_id": group_id,
            "balances": balance_entries,
            "simplified_debts": simplified_debts
        }


class ExpenseService:
    @staticmethod
    def create_expense(
        group_id: int,
        paid_by: int,
        description: str,
        amount: Decimal,
        splits: List[Dict],
        category: str = "general",
        expense_date: Optional[datetime] = None
    ) -> Expense:

        group = Group.query.get(group_id)
        if not group:
            raise NotFoundError(f"Group {group_id} not found")

        if paid_by not in [m.id for m in group.members]:
            raise ValidationError("Payer must be a group member")

        split_amounts = [Decimal(str(s["amount"])) for s in splits]
        is_valid, diff = validate_split_total(amount, split_amounts)
        if not is_valid:
            raise ValidationError(f"Splits must sum to expense amount. Difference: {diff}")

        expense = Expense(
            group_id=group_id,
            paid_by=paid_by,
            description=description,
            amount=amount,
            category=category,
            expense_date=expense_date or datetime.utcnow(),
            status=ExpenseStatus.OPEN
        )

        db.session.add(expense)
        db.session.flush()

        for split_data in splits:
            user_id = split_data["user_id"]
            split_amount = Decimal(str(split_data["amount"]))

            if user_id not in [m.id for m in group.members]:
                raise ValidationError(f"User {user_id} is not a group member")

            split = Split(
                expense_id=expense.id,
                user_id=user_id,
                amount=split_amount
            )

            db.session.add(split)

        db.session.commit()
        return expense


class SettlementService:
    @staticmethod
    def create_settlement(
        from_user_id: int,
        to_user_id: int,
        amount: Decimal,
        expense_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Settlement:

        if from_user_id == to_user_id:
            raise ValidationError("Cannot settle with yourself")

        settlement = Settlement(
            expense_id=expense_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            amount=amount,
            notes=notes,
            status=SettlementStatus.PROPOSED
        )

        db.session.add(settlement)
        db.session.commit()
        return settlement

    @staticmethod
    def confirm_settlement(settlement_id: int) -> Settlement:
        settlement = Settlement.query.get(settlement_id)
        if not settlement:
            raise NotFoundError(f"Settlement {settlement_id} not found")

        if settlement.status != SettlementStatus.PROPOSED:
            raise ValidationError("Settlement must be proposed before confirmation")

        settlement.status = SettlementStatus.CONFIRMED
        settlement.confirmed_at = datetime.utcnow()

        db.session.commit()
        return settlement

    @staticmethod
    def complete_settlement(settlement_id: int) -> Settlement:
        settlement = Settlement.query.get(settlement_id)
        if not settlement:
            raise NotFoundError(f"Settlement {settlement_id} not found")

        if settlement.status != SettlementStatus.CONFIRMED:
            raise ValidationError("Settlement must be confirmed before completion")

        settlement.status = SettlementStatus.COMPLETED
        db.session.commit()
        return settlement

    @staticmethod
    def dispute_settlement(settlement_id: int, reason: Optional[str] = None) -> Settlement:
        settlement = Settlement.query.get(settlement_id)
        if not settlement:
            raise NotFoundError(f"Settlement {settlement_id} not found")

        settlement.status = SettlementStatus.DISPUTED
        if reason:
            settlement.notes = f"{settlement.notes or ''} | Dispute: {reason}"

        db.session.commit()
        return settlement