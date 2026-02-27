from decimal import Decimal
from flask import Blueprint, request, jsonify

from app.services import (
    UserService, GroupService, ExpenseService, SettlementService,
    ValidationError, NotFoundError
)
from app.schemas import (
    UserCreate, UserResponse,
    GroupCreate, GroupResponse,
    ExpenseCreate, ExpenseResponse,
    SettlementCreate, SettlementResponse
)
from app.extensions import db

api = Blueprint('api', __name__, url_prefix='/api/v1')


# Error handlers
@api.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({'error': 'Validation Error', 'message': str(e)}), 400


@api.errorhandler(NotFoundError)
def handle_not_found_error(e):
    return jsonify({'error': 'Not Found', 'message': str(e)}), 404


@api.errorhandler(Exception)
def handle_generic_error(e):
    db.session.rollback()
    return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


# Health check
@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


# User routes
@api.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user_data = UserCreate(**data)
    
    user = UserService.create_user(user_data.name, user_data.email)
    return jsonify(UserResponse.model_validate(user).model_dump()), 201


@api.route('/users', methods=['GET'])
def list_users():
    users = UserService.list_users()
    return jsonify([UserResponse.model_validate(u).model_dump() for u in users]), 200


@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(UserResponse.model_validate(user).model_dump()), 200


# Group routes
@api.route('/groups', methods=['POST'])
def create_group():
    data = request.get_json()
    group_data = GroupCreate(**data)
    
    group = GroupService.create_group(
        name=group_data.name,
        description=group_data.description or '',
        member_ids=group_data.member_ids
    )
    return jsonify(GroupResponse.model_validate(group).model_dump()), 201


@api.route('/groups', methods=['GET'])
def list_groups():
    groups = GroupService.list_groups()
    return jsonify([GroupResponse.model_validate(g).model_dump() for g in groups]), 200


@api.route('/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    group = GroupService.get_group(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    return jsonify(GroupResponse.model_validate(group).model_dump()), 200


@api.route('/groups/<int:group_id>/balances', methods=['GET'])
def get_group_balances(group_id):
    try:
        balances = GroupService.get_group_balances(group_id)
        return jsonify(balances), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404


# Expense routes
@api.route('/expenses', methods=['POST'])
def create_expense():
    data = request.get_json()
    expense_data = ExpenseCreate(**data)
    
    expense = ExpenseService.create_expense(
        group_id=data.get('group_id'),
        paid_by=expense_data.paid_by,
        description=expense_data.description,
        amount=expense_data.amount,
        splits=[s.model_dump() for s in expense_data.splits],
        category=expense_data.category,
        expense_date=expense_data.expense_date
    )
    return jsonify(ExpenseResponse.model_validate(expense).model_dump()), 201


@api.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    expense = ExpenseService.get_expense(expense_id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    return jsonify(ExpenseResponse.model_validate(expense).model_dump()), 200


@api.route('/groups/<int:group_id>/expenses', methods=['GET'])
def list_group_expenses(group_id):
    expenses = ExpenseService.list_group_expenses(group_id)
    return jsonify([ExpenseResponse.model_validate(e).model_dump() for e in expenses]), 200


# Settlement routes
@api.route('/settlements', methods=['POST'])
def create_settlement():
    data = request.get_json()
    settlement_data = SettlementCreate(**data)
    
    settlement = SettlementService.create_settlement(
        from_user_id=settlement_data.from_user_id,
        to_user_id=settlement_data.to_user_id,
        amount=settlement_data.amount,
        expense_id=settlement_data.expense_id,
        notes=settlement_data.notes
    )
    return jsonify(SettlementResponse.model_validate(settlement).model_dump()), 201


@api.route('/settlements/<int:settlement_id>/confirm', methods=['POST'])
def confirm_settlement(settlement_id):
    try:
        settlement = SettlementService.confirm_settlement(settlement_id)
        return jsonify(SettlementResponse.model_validate(settlement).model_dump()), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404


@api.route('/settlements/<int:settlement_id>/complete', methods=['POST'])
def complete_settlement(settlement_id):
    try:
        settlement = SettlementService.complete_settlement(settlement_id)
        return jsonify(SettlementResponse.model_validate(settlement).model_dump()), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404


@api.route('/settlements/<int:settlement_id>/dispute', methods=['POST'])
def dispute_settlement(settlement_id):
    data = request.get_json() or {}
    reason = data.get('reason')
    
    try:
        settlement = SettlementService.dispute_settlement(settlement_id, reason)
        return jsonify(SettlementResponse.model_validate(settlement).model_dump()), 200
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404