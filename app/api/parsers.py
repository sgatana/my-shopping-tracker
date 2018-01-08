from flask_restplus import reqparse

update_shoppinglist_parser = reqparse.RequestParser()
update_shoppinglist_parser.add_argument('name', type=str,
                                        help='New Shoppinglist Name')
update_shoppinglist_parser.add_argument('description', type=str,
                                        help='Shoppinglist description should not be blank')

update_item_parser = reqparse.RequestParser()
update_item_parser.add_argument('name', type=str, required=True, help='Item name should be provided')
update_item_parser.add_argument('price', required=True, help='Item price should be provided')
update_item_parser.add_argument('quantity', required=True, help='Item quantity should be provided')
update_item_parser.add_argument('unit', required=True, help='enter a unit of measurement')
