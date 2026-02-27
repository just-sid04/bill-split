from decimal import Decimal
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Numeric, DateTime, Enum, Text, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class GroupStatus(PyEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ExpenseStatus(PyEnum):
    DRAFT = "draft"
    OPEN = "open"
    PARTIALLY_SETTLED = "partially_settled"
    SETTLED = "settled"
    ARCHIVED = "archived"


class SettlementStatus(PyEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    DISPUTED = "disputed"


class RecurringFrequency(PyEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Association table for many-to-many relationship
group_members = db.Table(
    'group_members',
    db.Column('group_id', db.Integer, ForeignKey('groups.id'), primary_key=True),
    db.Column('user_id', db.Integer, ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    groups = relationship('Group', secondary=group_members, back_populates='members')
    expenses_paid = relationship('Expense', back_populates='paid_by_user')
    splits = relationship('Split', back_populates='user')
    settlements_sent = relationship('Settlement', foreign_keys='Settlement.from_user_id', back_populates='from_user')
    settlements_received = relationship('Settlement', foreign_keys='Settlement.to_user_id', back_populates='to_user')
    
    def __repr__(self):
        return f'<User {self.name}>'


class Group(db.Model):
    __tablename__ = 'groups'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[GroupStatus] = mapped_column(Enum(GroupStatus), default=GroupStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    members = relationship('User', secondary=group_members, back_populates='groups')
    expenses = relationship('Expense', back_populates='group', cascade='all, delete-orphan')
    recurring_rules = relationship('RecurringRule', back_populates='group', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Group {self.name}>'


class Expense(db.Model):
    __tablename__ = 'expenses'
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_positive_amount'),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'), nullable=False)
    paid_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default='general')
    expense_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[ExpenseStatus] = mapped_column(Enum(ExpenseStatus), default=ExpenseStatus.OPEN)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship('Group', back_populates='expenses')
    paid_by_user = relationship('User', back_populates='expenses_paid')
    splits = relationship('Split', back_populates='expense', cascade='all, delete-orphan')
    settlements = relationship('Settlement', back_populates='expense')
    
    def __repr__(self):
        return f'<Expense {self.description}: {self.amount}>'


class Split(db.Model):
    __tablename__ = 'splits'
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_positive_split'),
        CheckConstraint('amount <= 100000', name='check_reasonable_split'),  # Max 100k to prevent errors
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(ForeignKey('expenses.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    expense = relationship('Expense', back_populates='splits')
    user = relationship('User', back_populates='splits')
    
    def __repr__(self):
        return f'<Split {self.user.name}: {self.amount}>'


class Settlement(db.Model):
    __tablename__ = 'settlements'
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_positive_settlement'),
        CheckConstraint('from_user_id != to_user_id', name='check_no_self_settlement'),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(ForeignKey('expenses.id'), nullable=True)  # Can be general settlement
    from_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    to_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[SettlementStatus] = mapped_column(Enum(SettlementStatus), default=SettlementStatus.PROPOSED)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    expense = relationship('Expense', back_populates='settlements')
    from_user = relationship('User', foreign_keys=[from_user_id], back_populates='settlements_sent')
    to_user = relationship('User', foreign_keys=[to_user_id], back_populates='settlements_received')
    
    def __repr__(self):
        return f'<Settlement {self.from_user.name} -> {self.to_user.name}: {self.amount}>'


class RecurringRule(db.Model):
    __tablename__ = 'recurring_rules'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default='general')
    frequency: Mapped[RecurringFrequency] = mapped_column(Enum(RecurringFrequency), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_generated: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship('Group', back_populates='recurring_rules')
    
    def __repr__(self):
        return f'<RecurringRule {self.description}: {self.amount} {self.frequency.value}>'