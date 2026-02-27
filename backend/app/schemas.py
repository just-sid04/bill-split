from decimal import Decimal
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


# User Schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Group Schemas
class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class GroupCreate(GroupBase):
    member_ids: List[int] = Field(default_factory=list)


class GroupResponse(GroupBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    created_at: datetime
    members: List[UserResponse] = []


# Split Schemas
class SplitBase(BaseModel):
    user_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=10)


class SplitCreate(SplitBase):
    pass


class SplitResponse(SplitBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user: Optional[UserResponse] = None


# Expense Schemas
class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=10)
    category: str = Field(default='general', max_length=50)
    expense_date: Optional[datetime] = None


class ExpenseCreate(ExpenseBase):
    paid_by: int
    splits: List[SplitCreate]


class ExpenseResponse(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    group_id: int
    status: str
    is_recurring: bool
    created_at: datetime
    paid_by_user: Optional[UserResponse] = None
    splits: List[SplitResponse] = []


# Settlement Schemas
class SettlementBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=10)
    notes: Optional[str] = Field(None, max_length=500)


class SettlementCreate(SettlementBase):
    from_user_id: int
    to_user_id: int
    expense_id: Optional[int] = None


class SettlementResponse(SettlementBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    from_user: Optional[UserResponse] = None
    to_user: Optional[UserResponse] = None


# Recurring Rule Schemas
class RecurringRuleBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=10)
    category: str = Field(default='general', max_length=50)
    frequency: str = Field(..., pattern=r'^(daily|weekly|monthly)$')
    start_date: datetime
    end_date: Optional[datetime] = None


class RecurringRuleCreate(RecurringRuleBase):
    pass


class RecurringRuleResponse(RecurringRuleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    group_id: int
    is_active: bool
    last_generated: Optional[datetime] = None
    created_at: datetime


# Debt/Balance Schemas
class BalanceEntry(BaseModel):
    user_id: int
    user_name: str
    net_balance: Decimal  # Positive = owed to them, Negative = they owe


class SimplifiedDebt(BaseModel):
    from_user_id: int
    from_user_name: str
    to_user_id: int
    to_user_name: str
    amount: Decimal


class GroupBalancesResponse(BaseModel):
    group_id: int
    balances: List[BalanceEntry]
    simplified_debts: List[SimplifiedDebt]