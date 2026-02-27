from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Tuple
from collections import defaultdict


def calculate_net_balances(balances: Dict[int, Decimal]) -> Dict[int, Decimal]:
    """
    Calculate net balance for each user.
    Positive = user is owed money
    Negative = user owes money
    """
    return {user_id: balance for user_id, balance in balances.items()}


def simplify_debts(balances: Dict[int, Decimal]) -> List[Tuple[int, int, Decimal]]:
    """
    Simplify debts to minimize number of transactions.
    
    Args:
        balances: Dict mapping user_id -> net_balance
        
    Returns:
        List of (from_user_id, to_user_id, amount) representing optimized transactions
    
    Algorithm:
    1. Separate creditors (positive balance) and debtors (negative balance)
    2. Match largest debtor with largest creditor
    3. Create transaction for min(abs(debt), credit)
    4. Update balances and repeat until all settled
    """
    # Round to 2 decimal places to avoid floating point issues
    balances = {
        user_id: balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        for user_id, balance in balances.items()
        if balance != 0  # Skip zero balances
    }
    
    if not balances:
        return []
    
    transactions = []
    
    # Create working copies
    debtors = []  # (user_id, amount_owed) - negative balances
    creditors = []  # (user_id, amount_owed) - positive balances
    
    for user_id, balance in balances.items():
        if balance < 0:
            debtors.append((user_id, -balance))  # Store as positive amount owed
        elif balance > 0:
            creditors.append((user_id, balance))
    
    # Sort by amount (largest first) for optimal matching
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)
    
    # Match debtors with creditors
    while debtors and creditors:
        debtor_id, debt_amount = debtors[0]
        creditor_id, credit_amount = creditors[0]
        
        # Determine transaction amount
        transaction_amount = min(debt_amount, credit_amount)
        
        if transaction_amount > 0:
            transactions.append((debtor_id, creditor_id, transaction_amount))
        
        # Update remaining amounts
        new_debt = debt_amount - transaction_amount
        new_credit = credit_amount - transaction_amount
        
        # Remove settled accounts and add back partials
        debtors = debtors[1:]
        creditors = creditors[1:]
        
        if new_debt > 0:
            debtors.append((debtor_id, new_debt))
            debtors.sort(key=lambda x: x[1], reverse=True)
        
        if new_credit > 0:
            creditors.append((creditor_id, new_credit))
            creditors.sort(key=lambda x: x[1], reverse=True)
    
    return transactions


def validate_split_total(expense_amount: Decimal, splits: List[Decimal]) -> Tuple[bool, Decimal]:
    """
    Validate that splits sum to expense amount.
    
    Returns:
        (is_valid, difference)
    """
    total = sum(splits)
    difference = (total - expense_amount).quantize(Decimal('0.01'))
    return difference == 0, difference


def calculate_group_balances(expenses, settlements) -> Dict[int, Decimal]:
    """
    Calculate net balances for all users in a group.
    
    Args:
        expenses: List of Expense objects with splits and paid_by
        settlements: List of Settlement objects (confirmed only)
        
    Returns:
        Dict mapping user_id -> net_balance
    """
    balances = defaultdict(Decimal)
    
    # Process expenses
    for expense in expenses:
        if expense.status.value not in ['open', 'partially_settled']:
            continue
            
        # Payer is owed money (positive)
        balances[expense.paid_by] += expense.amount
        
        # Each split user owes money (negative)
        for split in expense.splits:
            balances[split.user_id] -= split.amount
    
    # Process confirmed settlements
    for settlement in settlements:
       if settlement.status.value == 'completed':
            # From user paid (reduced their debt)
            balances[settlement.from_user_id] += settlement.amount
            # To user received (reduced what they're owed)
            balances[settlement.to_user_id] -= settlement.amount
    
    return dict(balances)