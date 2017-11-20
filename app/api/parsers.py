from flask_restplus import reqparse


item_parser = reqparse.RequestParser()
item_parser.add_argument('name', type=str, required=True,
                         help='Item Name')
item_parser.add_argument('price', required=True,
                         help='Item Price should not be a string')
item_parser.add_argument('quantity', required=True,
                         help='Item Quantity should not be a string')
item_parser.add_argument('shoppinglist_id', type=int, required=True,
                         help='Shoppinglist id is Required')

update_shoppinglist_parser = reqparse.RequestParser()
update_shoppinglist_parser.add_argument('name', type=str,
                                        help='New Shoppinglist Name')
update_shoppinglist_parser.add_argument('description', type=str,
                                 help='Shoppinglist description should not be blank')

pagination_parser=reqparse.RequestParser()
pagination_parser.add_argument('page', type='int', required=False, help='page number')
pagination_parser.add_argument('bool', type='bool', required=False, help='page number')
pagination_parser.add_argument('limit', type='int', required=False, help='limit per page',
                               default=10)