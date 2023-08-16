from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TagModel, ShopModel, ProductModel
from schemas import TagSchema, TagAndProductSchema

blp = Blueprint("Tags", "tags", description="Operations on tags")


@blp.route("/shop/<string:shop_id>/tag")
class TagsInshop(MethodView):
    @jwt_required
    @blp.response(200, TagSchema(many=True))
    def get(self, shop_id):
        """
        Retrieve all tags associated with a specific shop

        This endpoint returns a list of tags associated with the provided shop.

        :param shop_id: The ID of the shop.\n
        :return: List of tags associated with the shop.
        """
        shop = ShopModel.query.get_or_404(shop_id)

        return shop.tags.all()

    @jwt_required
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, shop_id):
        """
        Create a new tag within the specified shop

        This endpoint creates a new tag within the provided shop. The 'name' field of the tag
        should be unique within the shop.

        :param tag_data: Tag data to be created.\n
        :param shop_id: The ID of the shop.\n
        :return: Created tag.
        """
        if TagModel.query.filter(TagModel.shop_id == shop_id, TagModel.name == tag_data["name"]).first():
            abort(400, message="A tag with that name already exists in that shop.")

        tag = TagModel(**tag_data, shop_id=shop_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e),
            )

        return tag


@blp.route("/product/<string:product_id>/tag/<string:tag_id>")
class LinkTagsToProduct(MethodView):
    @jwt_required
    @blp.response(201, TagSchema)
    def post(self, product_id, tag_id):
        """
        Link a tag to a product

        This endpoint links a tag to a specific product.

        :param product_id: The ID of the product.\n
        :param tag_id: The ID of the tag.\n
        :return: Linked tag.
        """
        product = ProductModel.query.get_or_404(product_id)
        tag = TagModel.query.get_or_404(tag_id)

        product.tags.append(tag)

        try:
            db.session.add(product)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag

    @jwt_required
    @blp.response(200, TagAndProductSchema)
    def delete(self, product_id, tag_id):
        """
        Unlink a tag from a product

        This endpoint removes the association between a tag and a specific product.

        :param product_id: The ID of the product.\n
        :param tag_id: The ID of the tag.\n
        :return: Information about the unlinked tag and product.
        """
        product = ProductModel.query.get_or_404(product_id)
        tag = TagModel.query.get_or_404(tag_id)

        product.tags.remove(tag)

        try:
            db.session.add(product)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return {"message": "Product removed from tag", "product": product, "tag": tag}


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @jwt_required
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        """
        Retrieve details about a specific tag

        This endpoint retrieves detailed information about the specified tag.

        :param tag_id: The ID of the tag.\n
        :return: Tag details.
        """
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @jwt_required
    @blp.response(
        202,
        description="Deletes a tag if no product is tagged with it.",
        example={"message": "Tag deleted."},
    )
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more products. In this case, the tag is not deleted.",
    )
    def delete(self, tag_id):
        """
        Delete a tag

        This endpoint allows the deletion of a tag if it's not associated with any products.
        If the tag is associated with products, the deletion is prevented.

        :param tag_id: The ID of the tag.
        :return: Deletion status or error message.
        """
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.products:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any products, then try again.",  # noqa: E501
        )
