import os
from flask import Blueprint, jsonify,request, g
from flask_restplus import Api, Resource
from app.Api_models import ns, register_model, login_model, shoppinglist_model, update_shoppinglist_model
from app.Api_models.users import User
from app.methods import register_user
from flask_httpauth import HTTPBasicAuth

bp = Blueprint('api',__name__)
# app.wsgi_app = ProxyFix(app.wsgi_app)

auth=HTTPBasicAuth()

api = Api(bp, version='1.0', title='ShoppingList  API',
          description='A simple ShoppingList API')

config=os.environ.get('FLASK_CONFIG')
"""
implement verify password callback method to allow auth
(verify if user is logged in)
"""
@auth.verify_password
def verify_password(email_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(email_or_token, config=config)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True



@ns.route('/register')
@ns.expect(register_model)
class Users(Resource):
    @api.response(201, "User Registered Successfully")
    @api.response(409, "User already exists")
    def post(self):
        """
        Register a new user:
        """
        user = request.json
        if User.query.filter_by(email=user['email']).first() is not None:
            return jsonify({'message':'email already exist'})

        register_user(user)

        return jsonify({"message":"registration successful"})


@ns.route('/users')
class Users(Resource):
    @auth.login_required
    def get(self):
        """
        Get All users
        """
        users=User.query.all()
        all_users=[]
        for user in users:
            user_data = {}
            user_data['id']=user.id
            user_data['username']=user.username
            user_data['email'] = user.email
            user_data['password'] =user.password
            user_data['date'] =user.created_on
            user_data['modified'] =user.date_modified
            all_users.append(user_data)

        return jsonify({"users": all_users})

@ns.route('/users/<id>')
class user(Resource):
    @auth.login_required
    def get(self, id):
        """
        Get user using ID
        :param id:
        """
        user=User.query.filter(User.id==id).first()
        if not user:
            # raise "no"
            return jsonify({'message':'no user found'})
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['date'] = user.created_on
        user_data['modified'] = user.date_modified

        return jsonify({'user': user_data})
@ns.route('/login')
class Login(Resource):
    @api.response(200, "User logged in Successfully")
    @api.response(401, "Invalid Credentials")
    @ns.expect(login_model)
    def post(self):
        """
        User Login
        """
        user_data=request.json
        user=User.query.filter_by(email=user_data['email']).first()
        if user:
            if user.verify_password(user_data['password']):
                g.user=user
                token = g.user.generate_auth_token(config=config, expiration=600)
                return jsonify({"token": token.decode('ascii'),
                                "duration":600})
            else:
                return jsonify({'message':"wrong credentials"})
        else:
            return jsonify({'message':'user does not exist'})


@ns.route('/ShoppingList')
class ShoppigList(Resource):
    @ns.expect(shoppinglist_model)
    def post(self):
        """
        Add Shopping List
        """
    @api.response(404, "ShoppingList Not Found")
    def get(self):
        """
        Get Shopping Lists
        """
        return Users.query.all()

@ns.route('/ShoppingList/<int:id>')
@ns.expect(update_shoppinglist_model)
class UpdateshoppingList(Resource):
    def put(self):
        """
        Update Shopping List
        """


