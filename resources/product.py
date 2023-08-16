from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

from db import db
from models import ProductModel
from schemas import ProductSchema, ProductUpdateSchema

blp = Blueprint("Products", "products", description="Operations on products")


@blp.route("/product/<string:product_id>")
class Product(MethodView):
    @jwt_required()
    @blp.response(200, ProductSchema)
    def get(self, product_id):
        """
        Retrieve details about a specific product

        This endpoint retrieves detailed information about the specified product.

        :param product_id: The ID of the product.\n
        :return: Product details.
        """
        product = ProductModel.query.get_or_404(product_id)
        return product

    @jwt_required()
    def delete(self, product_id):
        """
        Delete a product

        This endpoint allows the deletion of a product.

        :param product_id: The ID of the product.\n
        :return: Deletion confirmation.
        """
        product = ProductModel.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted."}

    @jwt_required()
    @blp.arguments(ProductUpdateSchema)
    @blp.response(200, ProductSchema)
    def put(self, product_data, product_id):
        """
        Update or create a product

        This endpoint updates the details of an existing product or creates a new product if it doesn't exist.

        :param product_data: Updated product data.\n
        :param product_id: The ID of the product.\n
        :return: Updated or created product details.
        """
        product = ProductModel.query.get(product_id)

        if product:
            product.price = product_data["price"]
            product.name = product_data["name"]
        else:
            product = ProductModel(id=product_id, **product_data)

        db.session.add(product)
        db.session.commit()

        return product


@blp.route("/product")
class ProductList(MethodView):
    @jwt_required()
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """
        Retrieve a list of all products

        This endpoint returns a list of all available products.

        :return: List of products.
        """
        return ProductModel.query.all()

    @jwt_required()
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data):
        """
        Create a new product

        This endpoint creates a new product using the provided product data.

        :param product_data: Product data to be created.\n
        :return: Created product details.\n
        """
        product = ProductModel(**product_data)

        try:
            db.session.add(product)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the product.")

        return product
