from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from .models import User, Transaction
from . import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/register', methods=['POST'])
def register ():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'message': 'Dados obrigatórios não foram enviados'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Nome de usuário já existe'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify ({'message': 'Email já cadastrado'}), 409
    
    new_user = User(
        username=data['username'],
        email=data['email']
    )

    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify ({'message': 'Usuário criado com sucesso!'}), 201


@main_bp.route('/login', methods=['POST'])
def login ():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Dados obrigatórios não foram enviados'}), 400
    
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data.get('password')):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)
    else:
        return jsonify({'message': 'Credenciais inválidas'}), 401


@main_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "Usuário não encontrado"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })


@main_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    current_user_id = get_jwt_identity()

    data = request.get_json()

    if not data or not data.get('description') or not data.get('amount') or not data.get('transaction_type') or not data.get('date'):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    nova_transacao = Transaction(
        description=data['description'],
        amount=data['amount'],
        transaction_type=data['transaction_type'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        user_id=current_user_id
    )

    db.session.add(nova_transacao)
    db.session.commit()

    return jsonify({'message': 'Transação criada com sucesso!'}), 201


@main_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()
    
    user_transactions = Transaction.query.filter_by(user_id=current_user_id).all()

    results = [
        {
            "id": trans.id,
            "description": trans.description,
            "amount": str(trans.amount),
            "transaction_type": trans.transaction_type,
            "date": trans.date.isoformat()
        }
        for trans in user_transactions
    ]

    return jsonify(results), 200


@main_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction_detail(transaction_id):
    current_user_id = get_jwt_identity()

    transacao_encontrada = Transaction.query.get(transaction_id)

    if transacao_encontrada and transacao_encontrada.user_id == int(current_user_id):
        result = {
            "id": transacao_encontrada.id,
            "description": transacao_encontrada.description,
            "amount": str(transacao_encontrada.amount),
            "transaction_type": transacao_encontrada.transaction_type,
            "date": transacao_encontrada.date.isoformat()
            }
        
        return jsonify(result), 200
    else:
        return jsonify({'message': 'Transação não encontrada'}), 404
    
@main_bp.route('/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    current_user_id = get_jwt_identity()

    transacao_encontrada = Transaction.query.get(transaction_id)


    if transacao_encontrada and transacao_encontrada.user_id == int(current_user_id):
        data = request.get_json()
        
        transacao_encontrada.description = data.get('description', transacao_encontrada.description)
        transacao_encontrada.amount = data.get('amount', transacao_encontrada.amount)
        transacao_encontrada.transaction_type = data.get('transaction_type', transacao_encontrada.transaction_type)
        
        if 'date' in data:
            transacao_encontrada.date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        db.session.commit()

        return jsonify({
            "id": transacao_encontrada.id,
            "description": transacao_encontrada.description,
            "amount": str(transacao_encontrada.amount),
            "transaction_type": transacao_encontrada.transaction_type,
            "date": transacao_encontrada.date.isoformat()
        }), 200
    else:
        return jsonify({'message': 'Transação não encontrada'}), 404