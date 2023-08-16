from db import db


class ProductsTag(db.Model):
    __tablename__ = "products_tags"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))
