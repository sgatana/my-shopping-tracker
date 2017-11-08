from flask_restplus import reqparse


item_parser = reqparse.RequestParser()
item_parser.add_argument('name', type=str, required=True,
                         help='Item Name')
item_parser.add_argument('price', required=True,
                         help='Item Price should not be a string')
item_parser.add_argument('quantity', required=True,
                         help='Item Quantity should not be a string')
item_parser.add_argument('shoppinglist_id', type=int, required=True,
                         help='Shoppinglist(id) to add item to Required')