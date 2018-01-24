import os, re
from sqlalchemy import func
from flask import Blueprint, jsonify, request, g, make_response, current_app, url_for
from flask_restplus import Api, Resource
from app.api_models import ns, register_model, login_model, shoppinglist_model, update_shoppinglist_model, \
    add_item_model, update_item_model
from app.api_models.users import User
from app.api_models.logout import BlacklistToken
from app.api_models.shoppinglist import ShoppingList
from app.api_models.item import Item
from app.validators import isValidEmail, validate_names, password_validator, validate_username
from app.methods import register_user, delete_item, update_shopping_list, \
    update_item
from app.api.parsers import update_shoppinglist_parser, update_item_parser
from app import db

bp = Blueprint('api', __name__)

api = Api(bp, version='1.0', title='ShoppingList  API',
          description='A simple ShoppingList API')

config = os.environ.get('FLASK_CONFIG')


# customize response for non-existing endpoint
@bp.app_errorhandler(404)
def not_found(e):
    response = make_response(jsonify({'message': 'This is not the page you are looking for'}), 404)
    return response


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

        # check if user has all required fields
        required_fields = ("email", "username", "password", "confirm")
        absent = []
        for field in required_fields:
            if not user.get(field, None):
                absent.append(f'{field} is required')
        if absent:
            return make_response(jsonify({'error': absent}), 400)

        # check if email supplied exists in the database,
        if isValidEmail(user['email']):
            if User.query.filter_by(email=user['email']).first() is not None:
                return make_response(jsonify({'error': 'email already exist'}), 409)
            # validate username should not contain special characters and spaces
            if not validate_username(user['username']):
                return make_response(jsonify({'error': 'please enter a valid name, empty and special characters not '
                                                       'allowed'}),401)
            # validate password
            if not password_validator(user['password']):
                error = 'should have a min length is 6, should have at least include a digit number' \
                         'should have an uppercase and a lowercase letter, should contain and a special characters'
                return make_response(jsonify({'error': error}),401)
            # make sure your passwords match
            if user['confirm'] != user['password']:
                return make_response(jsonify({'error': 'Your passwords did not match'}),401)
            # register user
            register_user(user)

            return make_response(jsonify({"message": "registration successful"}), 201)
        else:
            return make_response(jsonify({'error': 'enter a valid email address'}),401)


@ns.route('/user')
class CurrentUser(Resource):
    def get(self):
        """
        Get user details
        :return: name, email, date_created
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'error': 'You hav not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            try:
                user_id = User.decode_auth_token(token)
                if not isinstance(user_id, str):
                    # get user details
                    user = User.query.filter_by(id=user_id).first()
                    details = {
                        'name': user.username,
                        'date create': user.created_on,
                        'email': user.email
                    }
                    return make_response(jsonify({'user': details}), 200)


                else:
                    return make_response(jsonify({'error': 'Your token is invalid, please log in'}), 401)
            except Exception as e:
                return make_response(jsonify({'error': 'Failed to load user details'}), 404)
        else:
            return make_response(jsonify({'error': 'Please provide a valid token'}), 403)


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
        #  check if entered email exists in the database
        required_fields=('email','password')
        obj = []
        for field in required_fields:
            if not user_data.get(field, None):
                obj.append(f'{field} is required')

        if obj:
            return make_response(jsonify({'error': obj}), 400)

        user = User.query.filter_by(email=user_data['email']).first()
        if user:
            # verify login credentials (password)
            if user.verify_password(user_data['password']):
                g.user = user
                token = user.encode_auth_token(user.id)
                return make_response(jsonify({"message": 'you have successfully logged in', "token": token.decode()}),
                                     200)
            else:
                return make_response(jsonify({'error': "your email or password is incorrect"}), 401)
        else:
            return make_response(jsonify({'error': 'user with supplied email does not exist'}), 401)


@ns.route('/Shoppinglist', endpoint='sh_list')
class Shopping_List(Resource):
    @ns.expect(shoppinglist_model)
    def post(self):
        """
        Add Shopping List
        """
        shoppinglist = request.form
        #  Get auth token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'failed': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                # check if a user has entered required fields
                fields = ("name", "description")
                none = []
                for field in fields:
                    if not shoppinglist.get(field, None):
                        none.append(f'{field} is required')
                if none:
                    return make_response(jsonify({'error': none}), 403)
                #  check if shopping list already exists
                shopping_list = ShoppingList.query.filter(func.lower(ShoppingList.name)==func.lower
                (shoppinglist['name'])).filter_by(owner_id=user_id).first()
                if shopping_list:
                    return make_response(jsonify({'error': 'Shopping list already exists'}), 409)

                # validate inputs
                if not validate_names(shoppinglist['name']):
                    return make_response(jsonify({'error': 'Please enter a valid name'}), 403)
                if not validate_names(shoppinglist['description']):
                    return make_response(jsonify({'error': 'Please provide a valid description'}), 403)
                my_list = ShoppingList(name=shoppinglist['name'], description=shoppinglist['description'],
                                       owner=user_id)
                ShoppingList.save(my_list)

                return make_response(jsonify({'message': 'shopping list add successfully'}), 201)

            else:
                return make_response(jsonify({'error': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'error': 'Please provide a valid token'}), 403)

    @api.response(404, "Shopping list Not Found")
    def get(self):
        """
        search shoppinglist based on the provided search parameter
        """
        # Get the auth token
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return make_response(jsonify({'error': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                # get items using search parameter
                q = request.args.get('q')
                if q:
                    shopping_lists = ShoppingList.query.filter(
                        func.lower(ShoppingList.name).like('%' + func.lower(q) + '%')).filter_by(owner_id=user_id)
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

                        # display items using search parameter
                        return make_response(jsonify({
                            'shoppinglists': [
                                dict(name=shoppinglist.name, description=shoppinglist.description,
                                     id=shoppinglist.id,
                                     owner=user_id, last_modified=shoppinglist.modified_on)
                                for shoppinglist in shoppinglists],
                            'prev': prev,
                            'next': next,
                            'Total': pagination.total
                        }), 200)
                    return make_response(jsonify({'error': 'shopping list with such name does not exist'}), 404)

                else:
                    # user = User.query.filter_by()
                    # display all items without supplying search parameter
                    shopping_lists = ShoppingList.query.filter_by(owner_id=user_id)
                    page = request.args.get('page', 1, type=int)
                    limit = request.args.get('limit', current_app.config['FLASKY_POSTS_PER_PAGE'], type=int)
                    pagination = shopping_lists.paginate(
                        page, per_page=limit, error_out=False
                    )

                    # paginate shopping lists
                    shoppinglists = pagination.items
                    prev = None
                    if pagination.has_prev:
                        prev = url_for('api.sh_list', page=page - 1)
                    next = None
                    if pagination.has_next:
                        next = url_for('api.sh_list', page=page + 1)
                    if shoppinglists:
                        return make_response(jsonify({
                            'shoppinglists': [
                                dict(name=shoppinglist.name, description=shoppinglist.description,
                                     id=shoppinglist.id,
                                     owner=user_id, last_modified=shoppinglist.modified_on)
                                for shoppinglist in shoppinglists],
                            'prev': prev,
                            'next': next,
                            'items':len(shoppinglists),
                            'current': page,
                            'Total': pagination.total,
                            'user':user_id
                        }), 200)
                    else:
                        return make_response(jsonify({"error": "you have not added shopping list yet"}), 404)

            else:
                return make_response(jsonify({'error': 'your token is invalid, please log in '}), 401)
        else:
            return make_response(jsonify({'error': 'Please provide a valid token'}), 401)

    def delete(self):
        """
        delete all the shopping list and their dependent items
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'error': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
            if not token:
                return make_response(jsonify({'failed': 'Your token is invalid'}), 401)

        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                # delete all shopping lists
                shoppinglist = ShoppingList.query.filter_by(owner_id=user_id).all()
                if not shoppinglist:
                    return make_response(jsonify({'failed': 'No shopping list(s) found'}), 404)
                for shpl in shoppinglist:
                   delete_item(shpl)

                return make_response(jsonify({'message': 'shopping list(s) deleted successfully'}), 200)
            else:
                return make_response(jsonify({'error': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'error': 'Please provide a valid token'}), 403)


@ns.route('/Shoppinglist/<int:id>')
class UpdateshoppingList(Resource):
    @ns.expect(update_shoppinglist_model)
    def put(self, id):
        """
        Update Shopping List
        """
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):
                args = update_shoppinglist_parser.parse_args()
                name = args.get('name')
                description = args.get('description')

                # check if all fields are provided
                if not (name and description):
                    return make_response(jsonify({"error": "Please make sure name and description fields are not "
                                                           "missing"}), 403)

                # check if shopping list name already exist
                list_name = ShoppingList.query.filter(func.lower(ShoppingList.name)==func.lower(name)).\
                    filter_by(owner_id=user_id).first()
                if list_name:
                    return make_response(jsonify({'failed': 'shopping list with similar name exists'}), 409)

                shoppinglist = ShoppingList.query.filter_by(id=id).filter_by(owner_id=user_id).first()
                if not shoppinglist:
                    return make_response(jsonify({'error': 'no shopping list with the provided id'}), 404)

                # check if the name is provided
                if name == '' and description == '':
                    return make_response(jsonify({'message': 'No changes made on the shopping list'}),200)
                elif name != '' and description == '':
                    if not validate_names(name):
                        return make_response(jsonify({'error': 'please enter a valid name'}),403)
                    shoppinglist.name = name
                    db.session.commit()
                    return make_response(jsonify({'message': 'shopping list updated successfully'}), 200)

                # validate shopping list fields
                elif description != '' and name == '':
                    if not validate_names(description):
                        return make_response(jsonify({'error': 'please provide a valid description'}), 403)
                    shoppinglist.description = description
                    db.session.commit()
                    return make_response(jsonify({'message': 'shopping list updated successfully'}), 200)
                else:
                    if not validate_names(name) and not validate_names(description):
                        return make_response(jsonify({'error': 'please enter valid name and description'}), 403)
                    update_shopping_list(shoppinglist, name, description)
                    return make_response(jsonify({'message': 'shopping list updated successfully'}), 200)
            else:
                return make_response(jsonify({'error': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'failed': 'Please provide a valid token'}), 403)

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

                # delete shopping list using and id
                shoppinglist = ShoppingList.query.filter_by(id=id).filter_by(owner_id=user_id).first()
                if not shoppinglist:
                    return make_response(jsonify({'error': 'No shopping list with the provided id'}), 404)
                delete_item(shoppinglist)
                return make_response(jsonify({'message': 'shopping list deleted successfully'}), 200)
            else:
                return make_response(jsonify({'error': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'failed': 'Please provide a valid token'}), 403)

    def get(self, id):
        """
        Find Shopping list by id
        """
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return make_response(jsonify({'failed': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                # get a single shopping list
                user = user_id
                shoppinglist = ShoppingList.query.filter_by(id=id, owner_id=user_id).first()
                if not shoppinglist:
                    return make_response(jsonify({"error": "No Shopping list found with provided id"}), 404)
                shoppig_list = {}
                shoppig_list["name"] = shoppinglist.name
                shoppig_list["description"] = shoppinglist.description
                shoppig_list["last modified"] = shoppinglist.modified_on
                shoppig_list["owner"] = user
                return make_response(jsonify({"Shopping list": shoppig_list}))
            else:
                return make_response(jsonify({'error': 'your token is invalid'}), 401)
        else:
            return make_response(jsonify({'failed': 'Please provide a valid token'}), 403)


@ns.route('/Shoppinglist/<int:id>/Items')
class Items(Resource):
    @ns.expect(add_item_model)
    def post(self, id):
        """
        Add Items To Shopping List
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'failed': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                items = request.form
                item_name = items.get('name')
                price = items.get('price')
                quantity = items.get('quantity')
                unit = items.get('unit')
                owner = user_id

                # check if all fields are provided
                if not(item_name and price and quantity and unit):
                    return make_response(jsonify({'error': 'there are missing fields'}), 403)

                # check if the shoping list exists
                shoppinglistid = ShoppingList.query.filter_by(id=id).first()
                if not shoppinglistid:
                    return make_response(jsonify({'error': 'Shopping list with provided id does not exist'}),403)
                check_item = Item.query.filter(func.lower(Item.name)==item_name).filter_by(owner_id=owner).first()
                if check_item:
                    return make_response(jsonify({'error': 'Item with provided name already exist'}), 409)
                if not validate_names(item_name):
                    return make_response(jsonify({'failed': 'Please enter a valid Item name'}), 403)
                if [field for field in (price, quantity) if not re.match("^[0-9.]+$", field)]:
                    return make_response(jsonify({'failed': 'Please enter valid value for  price and quantity'}), 403)
                if not validate_names(unit):
                    return make_response(jsonify({'error': 'Please enter a valid unit value'}),403)

                shoppinglist_item = Item(name=item_name, price=price, quantity=quantity, shoppinglist_id=shoppinglistid.id,
                                         owner_id=owner, unit=unit)

                db.session.add(shoppinglist_item)
                db.session.commit()
                if shoppinglist_item:
                    return make_response(jsonify({'message': 'items added successfully'}), 201)
                return make_response(jsonify({'error': 'item was not added'}), 404)
            else:
                return make_response(jsonify({'failed': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'forbidden': 'Please provide a valid token'}), 403)

    @ns.response(404, "Item(s) Not Found")
    def get(self, id):
        """
        Get Shopping list items
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'message': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                # get all the items belonging to a specific shopping list
                items = Item.query.filter_by(shoppinglist_id=id).filter_by(owner_id=user_id).all()
                if not items:
                    return make_response(jsonify({'error': 'This Shoppinglist does not contain items, please add Items'}),
                                         403)
                shoppinglist_items = []
                for item in items:
                    all_items = {}
                    all_items['name'] = item.name
                    all_items['id'] = item.id
                    all_items['price'] = item.price
                    all_items['quantity'] = item.quantity
                    all_items['unit'] = item.unit
                    all_items['shoppinglist_id'] = item.shoppinglist_id

                    # get all items
                    shoppinglist_items.append(all_items)
                return make_response(jsonify({'shoppinglist_items': shoppinglist_items}), 200)
            else:
                return make_response(jsonify({'message': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'forbidden': 'Please provide a valid token'}), 403)

    def delete(self, id):
        """
        delete all items from a shopping list
        :param id:
        """

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'failed': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
            if not token:
                return make_response(jsonify({'error': 'Your token is invalid'}), 401)

        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                # delete all items belonging to a specific shopping list
                shoppinglist = Item.query.filter_by(shoppinglist_id=id, owner_id=user_id).all()
                if not shoppinglist:
                    return make_response(jsonify({'error': 'No item(s) found'}), 404)
                for item in shoppinglist:
                    delete_item(item)
                return make_response(jsonify({'message': 'items deleted successfully from the shopping list'}), 200)
            else:
                return make_response(jsonify({'failed': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'forbidden': 'Please provide a valid token'}), 403)


@ns.route('/Shoppinglist/<int:list_id>/Items/<int:id>')
class item(Resource):
    @ns.expect(update_item_model)
    def put(self, list_id, id):
        """
        Update Item
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'failed': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                args = update_item_parser.parse_args()
                name = args.get('name')
                price = args.get('price'),
                quantity = args.get('quantity')
                unit = args.get('unit')
                check_item = Item.query.filter(func.lower(Item.name)==func.lower(name)).filter_by(owner_id=user_id).\
                    first()
                if check_item:
                    return make_response(jsonify({'error': 'Item with provided name already exist'}), 409)

                # update an item
                new_item = Item.query.filter_by(id=id, shoppinglist_id=list_id, owner_id=user_id).first()
                if not new_item:
                    return make_response(jsonify({'error': 'item with such id does not exists'}), 403)

                # validate item's fields
                if name == '' and price == '' and quantity == '' and unit == '':
                    return make_response(jsonify({'message': 'No changes were made'}), 200)

                if not validate_names(name):
                    return make_response(jsonify({'error': 'Please enter a valid Item name'}), 403)
                if [field for field in price if not re.match("^[0-9.]+$", field)]:
                    return make_response(jsonify({'error': 'Please enter valid value for price '}), 403)
                if [field for field in quantity if not re.match("^[0-9.]+$", field)]:
                    return make_response(jsonify({'error': 'Please enter valid value for quantity'}), 403)
                if not validate_names(unit):
                    return make_response(jsonify({'error': 'Please provide a valid value for unit of measure'}))
                update_item(new_item, name, price, quantity, unit)
                return make_response(jsonify({'message': 'item successfully update'}), 200)
            else:
                return make_response(jsonify({'error': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'forbidden': 'Please provide a valid token'}), 403)

    def delete(self, list_id, id):
        """
        Delete an item from a shopping list
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'failed': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                # check if item exist in a database
                item = Item.query.filter_by(id=id, shoppinglist_id=list_id, owner_id=user_id).first()
                if not item:
                    return make_response(jsonify({'error': 'no item found with the provided id'}), 404)
                delete_item(item)
                return make_response(jsonify({'message': 'item deleted successfully'}), 200)
            else:
                return make_response(jsonify({'error': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'error': 'Please provide a valid token'}), 403)

    def get(self, list_id, id):
        """
        Get a specific item from a shopping list
        :param list_id:
        :param id:
        """

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'failed': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                # check if item exists in the database
                item = Item.query.filter_by(id=id, shoppinglist_id=list_id, owner_id=user_id).first()
                if not item:
                    return make_response(jsonify({'error': 'no item found with the provided id'}), 403)
                item_details = {
                    'name': item.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'unit of measurement': item.unit

                }
                return make_response(jsonify({'item': item_details}))
            else:
                return make_response(jsonify({'error': 'Your token is invalid, please log in'}), 401)
        else:
            return make_response(jsonify({'error': 'Please provide a valid token'}), 403)


@ns.route('/logout')
class Logout(Resource):
    def post(self):
        """
        Logout user by blacklisting the token
        """
        # get token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return make_response(jsonify({'error': 'You have not provided an authorization token'}), 401)

        else:
            token = auth_header.split(" ")[1]
        if token:
            user_id = User.decode_auth_token(token)
            if not isinstance(user_id, str):

                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=token)
                try:

                    # insert the token to blacklist table
                    db.session.add(blacklist_token)
                    db.session.commit()
                    return make_response(jsonify({'message': 'you have successfully logout'}),200)
                except Exception as e:
                    print(e)
                    return make_response(jsonify({'error': 'failed to logout, seems you already logged out'}), 403)
            else:
                return make_response(jsonify({'error': 'failed to logout, you are not logged in'}),403)

        else:
            return make_response(jsonify({'error': 'Please provide a valid token'}), 403)
