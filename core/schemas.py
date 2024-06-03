"""
This module defines the schemas for serialization and deserialization of Product and Review models.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError, validate
from .db import Product, Review
from .db import db


class ProductSchema(SQLAlchemyAutoSchema):
    """
    Schema for Product model.
    """

    class Meta:
        model = Product
        load_instance = True
        include_relationships = True
        sqla_session = db.session


class ReviewSchema(SQLAlchemyAutoSchema):
    """
    Schema for Review model.
    """

    product_asin = fields.Method("get_product_asin")

    class Meta:
        model = Review
        load_instance = True
        include_relationships = True
        sqla_session = db.session
        exclude = ("product",)

    product_id = fields.Integer(required=True)
    review = fields.String(required=True, validate=validate.Length(min=1))

    @validates("product_id")
    def validate_product_id(self, value):
        if not db.session.get(Product, value):
            raise ValidationError("Product does not exist.")

    def get_product_asin(self, obj):
        return obj.product.asin
