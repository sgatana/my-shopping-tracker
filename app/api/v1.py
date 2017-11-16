import os
from flask import Blueprint, jsonify,request, g
from flask_restplus import Api, Resource, marshal
from app.Api_models import ns, register_model, login_model, shoppinglist_model, update_shoppinglist_model, \
    add_item_model, user_model
from app.Api_models.users import User
from app.Api_models.shoppinglist import ShoppingList
from app.Api_models.item import Item
from app.methods import register_user, add_shopping_list, add_item, delete_item, update_shopping_list
from flask_httpauth import HTTPBasicAuth
from app.api.parsers import item_parser, update_shoppinglist_parser


bp = Blueprint('api',__name__)
auth=HTTPBasicAuth()

api = Api(bp, version='1.0', title='ShoppingList  API',
          description='A simple ShoppingList API')

config=os.environ.get('FLASK_CONFIG')

# implement error handler
@bp.app_errorhandler(404)
def not_found(e):
    response = jsonify({'status': 404, 'error': 'not found', 'message': 'invalid resource url'})
    response.status_code = 404
    return response


@auth.error_handler
def unauthorized_access():
    response = jsonify({'status':401, 'message':'Invalid credentials'})
    return response


@bp.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify({'status':500, 'error':'internal server error'})
    response.status_code=500
    return response
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


@ns.route('/user')
class user(Resource):
    @auth.login_required
    def get(self):
        return marshal(g.user, user_model)

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
class Shopping_List(Resource):
    @ns.expect(shoppinglist_model)
    @auth.login_required
    def post(self):
        """
        Add Shopping List
        """
        add_shopping_list(request.json)
        return jsonify({'message':'shopping list add successfully'})

    @api.response(404, "ShoppingList Not Found")
    @auth.login_required
    def get(self):
        """
        Get Shopping Lists
        """
        shoppinglists = ShoppingList.query.filter_by(owner_id=g.user.id).all()
        if not shoppinglists:
            return jsonify({'message':'you have not crreated a shoppinglist'})
        shopping_lists=[]
        for shoppinglist in shoppinglists:
            shopping_list={}
            shopping_list['id']=shoppinglist.id
            shopping_list['name']=shoppinglist.name
            shopping_list['description']=shoppinglist.description
            shopping_list['onwer']=shoppinglist.owner_id
            shopping_list['date created']=shoppinglist.created_on
            shopping_list['modified date']=shoppinglist.modified_on
            shopping_lists.append(shopping_list)
        return jsonify({'Shopping List(s)':shopping_lists})


@ns.route('/ShoppingList/<int:id>')
class UpdateshoppingList(Resource):
    @auth.login_required
    @ns.expect(update_shoppinglist_model)
    def put(self, id):
        """
        Update Shopping List
        """
        args=update_shoppinglist_parser.parse_args()
        name=args.get('name')
        description=args.get('description')
        shoppinglist = ShoppingList.query.filter_by(id=id).filter_by(owner_id=g.user.id).first()
        if not shoppinglist:
            return jsonify({'message': 'no shopping list with the provided id', 'status': 404})
        update_shopping_list(shoppinglist, name, description)
        return jsonify({'message':'shopping list update successfully'})

    @auth.login_required
    def delete(self, id):
        """
        Delete Shopping List
        """
        shoppinglist=ShoppingList.query.filter_by(id=id).filter_by(owner_id=g.user.id).first()
        if not shoppinglist:
            return jsonify({'message':'no shopping list with the provided id','status': 404})
        delete_item(shoppinglist)
        return jsonify({'message':'shopping list deleted succssfully'})

    def get(self):
        """
        Find Shopping list by id
        """


@ns.route('/items')
@ns.expect(add_item_model)
class Items(Resource):
    @auth.login_required
    def post(self):
        """
        Add a ShoppingList Item
        """
        args = item_parser.parse_args()
        name = args.get('name')
        price = args.get('price')
        quantity = args.get('quantity')
        shoppinglist_id = args.get('shoppinglist_id')
        shoppinglist = ShoppingList.query.filter_by(id=shoppinglist_id).filter_by(owner_id=g.user.id).first()
        if shoppinglist:
            add_item(name=name, price=price, quantity=quantity, shoppinglist=shoppinglist, owner_id=g.user.id)
            return jsonify({'message':'item successfully added'})
        else:
            return jsonify({'message':'shopping not found'})

    @auth.login_required
    @ns.response(404, "Item(s) Not Found")
    def get(self):
        """
        Get Shoppinglist items
        """
        items=Item.query.filter_by(owner_id=g.user.id).all()
        if not items:
            return jsonify({'message':'item and shopping does not exist'})
        shoppinglist_items = []
        for item in items:
            all_items = {}
            all_items['name']=item.name
            all_items['id']=item.id
            all_items['price']=item.price
            all_items['quantity']=item.quantity
            all_items['shoppinglist_id']=item.shoppinglist_id
            all_items['date created']=item.created_on
            shoppinglist_items.append(all_items)
            return jsonify({'message':shoppinglist_items})

@ns.route('/item/<int:id>')
class item(Resource):
    def put(self):
        """
        Update Item
        """
    @auth.login_required
    def delete(self, id):
        """
        Delete Item
        """
        item=Item.query.filter_by(id=id).filter_by(owner_id=g.user.id).first()
        if not item:
            return jsonify({'message':'not item found with the provided id', 'status':404})
        delete_item(item)
        return jsonify({'message':'item deleted successfully'})


