import os, re
from flask import Blueprint, jsonify, request, g, make_response, current_app, url_for
from flask_restplus import Api, Resource
from app.Api_models import ns, register_model, login_model, shoppinglist_model, update_shoppinglist_model, \
    add_item_model, update_item_model
from app.Api_models.users import User
from app.Api_models.logout import BlacklistToken
from app.Api_models.shoppinglist import ShoppingList
from app.Api_models.item import Item
from app.methods import register_user, delete_item, update_shopping_list, \
    update_item
from app.api.parsers import update_shoppinglist_parser, update_item_parser
from app import db

bp = Blueprint('api', __name__)

api = Api(bp, version='1.0', title='ShoppingList  API',
          description='A simple ShoppingList API')

config = os.environ.get('FLASK_CONFIG')


# implement error handler
@bp.app_errorhandler(404)
def not_found(e):
    response = make_response(jsonify({'message': 'This is not the page you are looking for'}), 404)
    return response


@bp.app_errorhandler(405)
def not_allowed(e):
    response = make_response(jsonify({'message': 'This is request method is not allowed for this endpoint'}), 405)
    return response


@bp.app_errorhandler(500)
def internal_server_error(e):
    response = make_response(jsonify({'message': 'Your application cannot communicate with the server'}), 500)
    return response


def isValidEmail(email):
    exp = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
    return re.match(exp, email)


def ValidateStrInputs(str):
   exp = "^[A-Za-z0-9]*$"
   return re.match(exp, str)


def password_validator(password):
    reg_pass = '^(?=\S{6,}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])'
    return re.match(reg_pass, password)


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
        required_fields = ("email", "username", "password", "confirm")
        absent = []
        for field in required_fields:
            if not user.get(field, None):
                absent.append(f'{field} is required')
        if absent:
            return make_response(jsonify({'message': absent}), 400)

        if isValidEmail(user['email']):
            if User.query.filter_by(email=user['email']).first() is not None:
                return make_response(jsonify({'message': 'email already exist'}), 409)
            if not ValidateStrInputs(user['username']):
                return make_response(jsonify({'message': 'please enter a valid name, empty and special characters not '
                                                         'allowed'}),401)
            if not password_validator(user['password']):
                return make_response(jsonify({'message': 'password should have a min length is 6, at least include a '
                                                         'digit number, uppercase and a lowercase letter and a special'
                                                         'characters'}),401)
            if user['confirm'] != user['password']:
                return make_response(jsonify({'message': 'Your passwords did not match'}),401)
            register_user(user)

            return make_response(jsonify({"message": "registration successful"}), 201)
        else:
            return make_response(jsonify({'message': 'enter a valid email address'}),401)


@ns.route('/user')
class CurrentUser(Resource):
    def get(self):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You hav not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            try:
                user_id = User.decode_auth_token(token)
                if not isinstance(user_id, str):
                    user = User.query.filter_by(id=user_id).first()
                    details = {
                        'name': user.username,
                        'date create': user.created_on,
                        'email': user.email
                    }
                    return make_response(jsonify({'user': details}), 200)


                else:
                    return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
            except Exception as e:
                return make_response(jsonify({'message': 'Failed to load user details'}), 404)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)


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
                token = user.encode_auth_token(user.id)
                print(token)
                return make_response(jsonify({"message": 'you have successfully logged in', "token": token.decode()}),
                                     200)
            else:
                return make_response(jsonify({'message': "your email or password is incorrect"}), 401)
        else:
            return make_response(jsonify({'message': 'user with supplied email does not exist'}), 404)


@ns.route('/Shoppinglist', endpoint='sh_list')
class Shopping_List(Resource):
    @ns.expect(shoppinglist_model)
    def post(self):
        """
        Add Shopping List
        """
        shoppinglist = request.form

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                shopping_list = ShoppingList.query.filter_by(name=shoppinglist['name'], owner_id=user_id).first()
                if shopping_list:
                    return make_response(jsonify({'message': 'Shoppinglist Already exists'}), 409)
                if not ValidateStrInputs(shoppinglist['name']):
                    return make_response(jsonify({'message': 'Name cannot be empty, please enter a valid name'}))
                if shoppinglist['description'] == '' or len(shoppinglist['description'].strip()) == 0:
                    return make_response(jsonify({'message': 'description cannot be empty'}))
                my_list = ShoppingList(name=shoppinglist['name'], description=shoppinglist['description'],
                                       owner=user_id)
                ShoppingList.save(my_list)

                return make_response(jsonify({'message': 'shopping list add successfully'}), 201)

            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)

    @api.response(404, "ShoppingList Not Found")
    def get(self):
        """
        search shoppinglist based on the provided search parameter
        """
        # Get the auth token
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return make_response(jsonify({'message': 'You hav not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                q = request.args.get('q')
                if q:
                    shopping_lists = ShoppingList.query.filter(ShoppingList.name.like('%' + q + '%')).filter_by \
                        (owner_id=user_id)
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
                                dict(name=shoppinglist.name, description=shoppinglist.description,
                                     id=shoppinglist.id,
                                     owner=user_id, last_modified=shoppinglist.modified_on)
                                for shoppinglist in shoppinglists],
                            'prev': prev,
                            'next': next,
                            'Total': pagination.total
                        })
                    return make_response(jsonify({'message': 'no shoppinglist found'}))
                else:
                    shopping_lists = ShoppingList.query.filter_by(owner_id=user_id)
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
                                    dict(name=shoppinglist.name, description=shoppinglist.description,
                                         id=shoppinglist.id,
                                         owner=user_id, last_modified=shoppinglist.modified_on)
                                    for shoppinglist in shoppinglists],
                                'prev': prev,
                                'next': next,
                                'Total': pagination.total
                            })
                    return make_response(jsonify({'message': 'no shopping list(s) found'}))

            else:
                return make_response(jsonify({'message': 'your token is invalid, please log in '}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)

    def delete(self):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
            if not token:
                return make_response(jsonify({'message': 'Your token is invalid'}), 401)

        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                shoppinglist = ShoppingList.query.filter_by(owner_id=user_id).delete()
                if not shoppinglist:
                    return make_response(jsonify({'message': 'No shopping list(s) found'}), 404)
                db.session.commit()
                return make_response(jsonify({'message': 'shopping list deleted succssfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)


@ns.route('/Shoppinglist/<int:id>')
class UpdateshoppingList(Resource):
    @ns.expect(update_shoppinglist_model)
    def put(self, id):
        """
        Update Shopping List
        """
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return make_response(jsonify({'message': 'You hav not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                args = update_shoppinglist_parser.parse_args()
                name = args.get('name')
                description = args.get('description')
                shoppinglist = ShoppingList.query.filter_by(id=id).filter_by(owner_id=user_id).first()
                if not shoppinglist:
                    return make_response(jsonify({'message': 'no shopping list with the provided id'}), 404)
                if name == '' or len(name.strip()) == 0:
                    return make_response(jsonify({'message': 'Name cannot be empty, please enter a valid name'}))
                if description == '' or len(description.strip()) == 0:
                    return make_response(jsonify({'message': 'description cannot be empty'}))
                update_shopping_list(shoppinglist, name, description)
                return make_response(jsonify({'message': 'shopping list update successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)

    def delete(self, id):
        """
        Delete Shopping List
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]

        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                shoppinglist = ShoppingList.query.filter_by(id=id).filter_by(owner_id=user_id).first()
                if not shoppinglist:
                    return make_response(jsonify({'message': 'No shopping list with the provided id'}), 404)
                delete_item(shoppinglist)
                return make_response(jsonify({'message': 'shopping list deleted succssfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)

    def get(self, id):
        """
        Find Shopping list by id
        """
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return make_response(jsonify({'message': 'You hav not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                user = user_id
                shoppinglist = ShoppingList.query.filter_by(id=id, owner_id=user_id).first()
                if not shoppinglist:
                    return make_response(jsonify({"message": "No Shopping list found with provided id"}), 404)
                shoppig_list = {}
                shoppig_list["name"] = shoppinglist.name
                shoppig_list["description"] = shoppinglist.description
                shoppig_list["last modified"] = shoppinglist.modified_on
                shoppig_list["owner"] = user
                return make_response(jsonify({"Shopping list": shoppig_list}))
            else:
                return make_response(jsonify({'message': 'your token is invalid'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)



@ns.route('/Shoppinglist/<int:id>/Items')
class Items(Resource):
    @ns.expect(add_item_model)
    def post(self, id):
        """
        Add Items To Shopping List
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                items = request.form
                item_name = items.get('name')
                price = items.get('price')
                quantity = items.get('quantity')
                owner = user_id
                shoppinglistid = ShoppingList.query.filter_by(id=id).first()
                if not shoppinglistid:
                    return make_response(jsonify({'message': 'Shopping list with provided id does not exist'}),404 )
                check_item = Item.query.filter_by(name=item_name, owner_id=owner).first()
                if check_item:
                    return make_response(jsonify({'message': 'Item with provided name already exist'}), 409)
                if item_name == '' or len(item_name.strip()) == 0:
                    return jsonify({'message': 'name cannot be empty'})
                if price == '':
                    return jsonify({'message': 'price cannot be empty'})
                if quantity == '':
                    return jsonify({'message': 'quantity cannot be empty'})
                if [field for field in (price, quantity) if re.search("[^0-9.]+", field)]:
                    return make_response(jsonify({'message': 'price and quantity should not be a string'}))

                shoppinglist_item = Item(name=item_name, price=price, quantity=quantity, shoppinglist_id=shoppinglistid.id,
                                         owner_id=owner)

                db.session.add(shoppinglist_item)
                db.session.commit()
                if shoppinglist_item:
                    return make_response(jsonify({'message': 'items added successfully'}), 201)
                return make_response(jsonify({'message': 'item was not added'}), 404)
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)

    @ns.response(404, "Item(s) Not Found")
    def get(self, id):
        """
        Get Shoppinglist items
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                items = Item.query.filter_by(shoppinglist_id=id).filter_by(owner_id=user_id).all()
                if not items:
                    return make_response(jsonify({'message': 'Shopping list with provided id does not contain items'}),
                                         404 )
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
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)

    def delete(self, id):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
            if not token:
                return make_response(jsonify({'message': 'Your token is invalid'}), 401)

        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                shoppinglist = Item.query.filter_by(shoppinglist_id=id, owner_id=user_id).delete()
                if not shoppinglist:
                    return make_response(jsonify({'message': 'No item(s) found'}), 404)
                db.session.commit()
                return make_response(jsonify({'message': 'items deleted succssfully from the shopping list'}), 200)
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)



@ns.route('/Shoppinglist/<int:list_id>/item/<int:id>')
class item(Resource):
    @ns.expect(update_item_model)
    def put(self, list_id, id):
        """
        Update Item
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                args = update_item_parser.parse_args()
                name = args.get('name')
                price = args.get('price'),
                quantity = args.get('quantity')
                new_item = Item.query.filter_by(id=id, shoppinglist_id=list_id, owner_id=user_id).first()
                if not new_item:
                    return make_response(jsonify({'message': 'item with such id does not exists'}), 404)
                if name == '' or len(name.split()) == 0:
                    return make_response(jsonify({'message': 'name cannot be empty'}))
                if price == '':
                    return make_response(jsonify({'message': 'price cannot be empty'}))
                if quantity == '':
                    return make_response(jsonify({'message': 'quantity cannot be empty'}))
                update_item(new_item, name, price, quantity)
                return make_response(jsonify({'message': 'item successfully update'}), 200)
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)

    def delete(self, list_id, id):
        """
        Delete Item
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                item = Item.query.filter_by(id=id, shoppinglist_id=list_id, owner_id=user_id).first()
                if not item:
                    return make_response(jsonify({'message': 'no item found with the provided id'}), 404)
                delete_item(item)
                return make_response(jsonify({'message': 'item deleted successfully'}), 200)
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)


@ns.route('/logout')
class Logout(Resource):
    def post(self):
        # get token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    return make_response(jsonify({'message': 'you have successfully logout'}),200)
                except Exception as e:
                    return make_response(jsonify({'message': 'failed to logout, try again'}), 200)
            else:
                return make_response(jsonify({'message': 'failed to logout, try again'}),400)

        else:
            return make_response(jsonify({'message': 'Please provide a valid token'}), 403)
