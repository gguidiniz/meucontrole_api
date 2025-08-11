from flask import request, jsonify, Blueprint
from .models import User
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