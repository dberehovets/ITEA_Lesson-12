from marshmallow import fields, Schema


class CategorySchema(Schema):
    title = fields.String()
    description = fields.String()
    parent = fields.Nested("self")
    is_root = fields.Boolean(default=False)


class AttributesSchema(Schema):
    height = fields.Float()
    weight = fields.Float()
    width = fields.Float()


class ProductSchema(Schema):
    title = fields.String(required=True)
    article = fields.String()
    description = fields.String(required=True)
    price = fields.Integer(required=True, min_value=0)
    in_stock = fields.Integer(min_value=0, default=0)
    discount_price = fields.Integer(min_value=1)
    attributes = fields.Nested(AttributesSchema, many=True)
    extra_data = fields.String()
    category = fields.Nested(CategorySchema, required=True)
    image = fields.String(required=True)