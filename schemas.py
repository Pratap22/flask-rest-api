from marshmallow import Schema, fields


class PlainProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainShopSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class ProductSchema(PlainProductSchema):
    shop_id = fields.Int(required=True, load_only=True)
    shop = fields.Nested(PlainShopSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class ProductUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()


class ShopSchema(PlainShopSchema):
    products = fields.List(fields.Nested(PlainProductSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    shop_id = fields.Int(load_only=True)
    products = fields.List(fields.Nested(PlainProductSchema()), dump_only=True)
    shop = fields.Nested(PlainShopSchema(), dump_only=True)


class TagAndProductSchema(Schema):
    message = fields.Str()
    product = fields.Nested(ProductSchema)
    tag = fields.Nested(TagSchema)

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    password = fields.Str(load_only=True)