import os, re
from flask import Blueprint, jsonify,request, g, make_response, current_app, url_for
from flask_restplus import Api, Resource, marshal
from app.Api_models import ns, register_model, login_model, shoppinglist_model, update_shoppinglist_model, \
    add_item_model, user_model, update_item_model
from app.Api_models.users import User
from app.Api_models.shoppinglist import ShoppingList
from app.Api_models.item import Item
from app.methods import register_user, add_shopping_list, delete_item, update_shopping_list, \
    update_item
from flask_httpauth import HTTPBasicAuth
from app.api.parsers import update_shoppinglist_parser, update_item_parser
from app import db


bp = Blueprint('api',__name__)
auth=HTTPBasicAuth()

api = Api(bp, version='1.0', title='ShoppingList  API',
          description='A simple ShoppingList API')

config=os.environ.get('FLASK_CONFIG')


# implement error handler
@bp.app_errorhandler(404)
def not_found(e):
    response = make_response(jsonify({'message': 'This is not the page you are looking for'}), 404)
    return response


@auth.error_handler
def unauthorized_access():
    response = make_response(jsonify({'message':'you token is not valid or has expired, please login to generate '
                                                'a new token'}), 401)
    return response


@bp.app_errorhandler(500)
def internal_server_error(e):
    response = make_response(jsonify({'message':'internal server error'}),500)
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


def isValidEmail(email):
    exp = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
    return re.match(exp, email)


def validateNames(name):
    pass


@ns.route('/register')
@ns.expect(register_model)
class Users(Resource):
    @api.response(201, "User Registered Successfully")
    @api.response(409, "User already exists")
    def post(self):
        """
        Register a new user:
        """
        user = request.form
        if isValidEmail(user['email']):

            if User.query.filter_by(email=user['email']).first() is not None:
                return make_response(jsonify({'message': 'email already exist'}), 409)
            if user['username'] == '' or len(user['username'].strip()) == 0:
                return jsonify({'message': 'please enter a valid name'})
            if user['password'] == '' or len(user['password'].strip()) == 0:
                return jsonify({'message': 'please enter a valid password'})
            if user['confirm'] != user['password']:
                return jsonify({'message':'Your passwords did not match'})
            register_user(user)
            if len(user['password'].strip()) < 6:
                return jsonify({'message': 'Password must have at least 6 characters'})
            return make_response(jsonify({"message": "registration successful"}), 201)
        else:
            return jsonify({'message': 'enter a valid email address'})


@ns.route('/user')
class CurrentUser(Resource):
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
        user_data = request.form
        user = User.query.filter_by(email=user_data['email']).first()
        if user:
            if user.verify_password(user_data['password']):
                g.user = user
                name = user.username
                token = g.user.generate_auth_token(config=config, expiration=600)
                return make_response(jsonify({"Hello " +name+" your Authentication token is": token.decode('ascii')}),
                                     200)
            else:
                return make_response(jsonify({'message': "your email or password is incorrect"}),401)
        else:
            return make_response(jsonify({'message': 'user with supplied email does not exist'}), 404)


@ns.route('/Shoppinglist', endpoint='sh_list')
class Shopping_List(Resource):
    @ns.expect(shoppinglist_model)
    @auth.login_required
    def post(self):
        """
        Add Shopping List
        """
        shoppinglist=request.form

        shopping_list = ShoppingList.query.filter_by(name=shoppinglist['name']).filter_by(owner_id=g.user.id).first()
        if shopping_list:
            return make_response(jsonify({'message': 'Shoppinglist Already exists'}), 409)
        if shoppinglist['name']=='' or len(shoppinglist['name'].strip())==0:
            return make_response(jsonify({'message': 'Name cannot be empty, please enter a valid name'}))
        if shoppinglist['description']=='' or len(shoppinglist['description'].strip())==0:
            return make_response(jsonify({'message': 'description cannot be empty'}))
        add_shopping_list(shoppinglist)
        return make_response(jsonify({'message': 'shopping list add successfully'}), 201)

    @api.response(404, "ShoppingList Not Found")
    @auth.login_required
    def get(self):
        """
        search shoppinglist based on the provided search parameter
        """
        owner=g.user.username
        q = request.args.get('q')
        if q:
            shopping_lists = ShoppingList.query.filter_by(owner_id=g.user.id).filter(ShoppingList.name.like
                                                                                     ('%{0}%'.format(q)))
        else:
            return make_response(jsonify({'message': 'no shoppinglist found with provided parameter'}))
        if shopping_lists:
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', current_app.config['FLASKY_POSTS_PER_PAGE'], type=int)
            pagination = shopping_lists.paginate(
                page, per_page=limit, error_out=False
            )
            shoppinglists = pagination.items
            prev = None
            if pagination.has_prev:
                prev = url_for('api.sh_list', page=page - 1)
            next = None
            if pagination.has_next:
                next = url_for('api.sh_list', page=page + 1)
            if shoppinglists:
                return jsonify({
                    'shoppinglist(s)': [
                        dict(name=shoppinglist.name, description=shoppinglist.description, id=shoppinglist.id,
                             owner=owner, last_modified=shoppinglist.modified_on)
                        for shoppinglist in shoppinglists],
                    'prev': prev,
                    'next': next,
                    'Total': pagination.total
                })
        else:
            return make_response(jsonify({'message': 'sorry you do not have shoppinglist'}))


@ns.route('/Shoppinglist/<int:id>')
class UpdateshoppingList(Resource):
    @auth.login_required
    @ns.expect(update_shoppinglist_model)
    def put(self, id):
        """
        Update Shopping List
        """
        args = update_shoppinglist_parser.parse_args()
        name = args.get('name')
        description = args.get('description')
        shoppinglist = ShoppingList.query.filter_by(id=id).filter_by(owner_id=g.user.id).first()
        if not shoppinglist:
            return make_response(jsonify({'message': 'no shopping list with the provided id'}), 404)
        if name == '' or len(name.strip()) == 0:
            return make_response(jsonify({'message': 'Name cannot be empty, please enter a valid name'}))
        if description == '' or len(description.strip()) == 0:
            return make_response(jsonify({'message': 'description cannot be empty'}))
        update_shopping_list(shoppinglist, name, description)
        return make_response(jsonify({'message': 'shopping list update successfully'}), 200)

    @auth.login_required
    def delete(self, id):
        """
        Delete Shopping List
        """
        shoppinglist = ShoppingList.query.filter_by(id=id).filter_by(owner_id=g.user.id).first()
        if not shoppinglist:
            return make_response(jsonify({'message': 'No shopping list with the provided id'}), 404)
        delete_item(shoppinglist)
        return make_response(jsonify({'message': 'shopping list deleted succssfully'}), 200)

    @auth.login_required
    def get(self, id):
        """
        Find Shopping list by id
        """
        user = g.user.username
        shoppinglist = ShoppingList.query.filter_by(id=id, owner_id=g.user.id).first()
        if not shoppinglist:
            return make_response(jsonify({"message": "No Shopping list found with provided id"}), 404)
        shoppig_list = {}
        shoppig_list["name"] = shoppinglist.name
        shoppig_list["description"] = shoppinglist.description
        shoppig_list["last modified"] = shoppinglist.modified_on
        shoppig_list["owner"] = user
        return make_response(jsonify({"Shopping list":shoppig_list}))


@ns.route('/Shoppinglist/<int:id>/Items')
class Items(Resource):
    @ns.expect(add_item_model)
    @auth.login_required
    def post(self, id):
        """
        Add Items To Shopping List
        """
        items=request.form
        print(items)
        item_name = items.get('name')
        print(item_name)
        price = items.get('price')
        quantity = items.get('quantity')
        owner = g.user.id
        check_item = Item.query.filter_by(name=item_name).first()
        if check_item:
            return make_response(jsonify({'message': 'Item with provided name already exist'}), 409)
        if item_name=='' or len(item_name.strip()) == 0:
            return jsonify({'message': 'name cannot be empty'})
        if price=='':
            return jsonify({'message': 'price cannot be empty'})
        if quantity=='':
            return jsonify({'message': 'quantity cannot be empty'})
        # if type(price) == str and type(quantity) == str:
        #     return make_response(jsonify({'message': 'price and quantity should not be a string'}))
        shoppinglistid = ShoppingList.query.filter_by(id=id).first()
        shoppinglist_item = Item(name=item_name, price=price, quantity=quantity, shoppinglist=shoppinglistid,
                                 owner_id=owner)

        db.session.add(shoppinglist_item)
        db.session.commit()
        if shoppinglist_item:
            return make_response(jsonify({'message': 'items added successfully'}), 201)
        return make_response(jsonify({'message': 'item was not added'}), 404)

    @auth.login_required
    @ns.response(404, "Item(s) Not Found")
    def get(self, id):
        """
        Get Shoppinglist items
        """
        items = Item.query.filter_by(shoppinglist_id=id).filter_by(owner_id=g.user.id).all()
        if not items:
            return jsonify({'message': 'item and shopping does not exist'})
        shoppinglist_items = []
        for item in items:
            all_items = {}
            all_items['name'] = item.name
            all_items['id'] = item.id
            all_items['price'] = item.price
            all_items['quantity'] = item.quantity
            all_items['shoppinglist_id'] = item.shoppinglist_id
            # all_items['date created'] = item.created_on
            shoppinglist_items.append(all_items)
        return jsonify({'message': shoppinglist_items})


@ns.route('/Shoppinglist/<int:list_id>/item/<int:id>')
class item(Resource):
    @ns.expect(update_item_model)
    @auth.login_required
    def put(self, list_id, id):
        """
        Update Item
        """
        args = update_item_parser.parse_args()
        name = args.get('name')
        price = args.get('price'),
        quantity = args.get('quantity')
        new_item = Item.query.filter_by(id=id, shoppinglist_id=list_id, owner_id=g.user.id).first()
        if not new_item:
            return make_response(jsonify({'message': 'item with such id does not exists'}), 404)
        update_item(new_item, name, price, quantity)
        return make_response(jsonify({'message': 'item successfully update'}), 200)

    @auth.login_required
    def delete(self, list_id, id):
        """
        Delete Item
        """

        item = Item.query.filter_by(id=id, shoppinglist_id=list_id, owner_id=g.user.id).first()
        if not item:
            return make_response(jsonify({'message': 'no item found with the provided id'}),404)
        delete_item(item)
        return make_response(jsonify({'message': 'item deleted successfully'}), 200)


