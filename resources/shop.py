from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import ShopModel
from schemas import ShopSchema

blp = Blueprint("Shops", "shops", description="Operations on shops")

@blp.route("/shop/<string:shop_id>")
class Shop(MethodView):
    @jwt_required()
    @blp.response(200, ShopSchema)
    def get(self, shop_id):
        """
        Retrieve details about a specific shop

        This endpoint retrieves detailed information about the specified shop.

        :param shop_id: The ID of the shop.\n
        :return: Shop details.
        """
        shop = ShopModel.query.get_or_404(shop_id)
        return shop

    @jwt_required()
    def delete(self, shop_id):
        """
        Delete a shop

        This endpoint allows the deletion of a shop.

        :param shop_id: The ID of the shop.\n
        :return: Deletion confirmation.
        """
        shop = ShopModel.query.get_or_404(shop_id)
        db.session.delete(shop)
        db.session.commit()
        return {"message": "Shop deleted"}, 200


@blp.route("/shop")
class ShopList(MethodView):
    @jwt_required()
    @blp.response(200, ShopSchema(many=True))
    def get(self):
        """
        Retrieve a list of all shops

        This endpoint returns a list of all available shops.

        :return: List of shops.
        """
        return ShopModel.query.all()

    @jwt_required()
    @blp.arguments(ShopSchema)
    @blp.response(201, ShopSchema)
    def post(self, shop_data):
        """
        Create a new shop

        This endpoint creates a new shop using the provided shop data.

        :param shop_data: Shop data to be created.
        :return: Created shop details.
        """
        shop = ShopModel(**shop_data)
        try:
            db.session.add(shop)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A shop with that name already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the shop.")

        return shop
