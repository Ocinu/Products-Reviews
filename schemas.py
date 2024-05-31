from marshmallow import fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from db import Product, Review, db


class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_relationships = True


class ReviewSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        load_instance = True
        include_relationships = True
        sqla_session = db.session

    product_id = fields.Integer(required=True)
    review = fields.String(required=True, validate=validate.Length(min=1))

    @validates('product_id')
    def validate_product_id(self, value):
        if not db.session.get(Product, value):
            raise ValidationError('Product does not exist.')
