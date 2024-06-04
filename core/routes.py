"""
This module defines the routes for the Flask application.
"""

import logging
from flask import Blueprint, request, jsonify
from flask_caching import Cache
from core.db import db, Product, Review
from core.schemas import ReviewSchema


bp = Blueprint("core", __name__)
cache = Cache()

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)


@bp.route("/")
def home():
    """
    Home endpoint.
    """

    logging.info("Home endpoint accessed")
    return "Welcome to products reviews!"


@bp.route("/products/<int:product_id>", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def get_product(product_id):
    """
    Get product details and reviews.

    :param product_id: Product ID
    :return: Product details and reviews
    """

    logging.info(f"Product endpoint accessed with product_id: {product_id}")
    product = db.session.get(Product, product_id)
    if not product:
        logging.warning(f"Product with product_id {product_id} not found")
        return jsonify({"message": "Product not found"}), 404

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    reviews_query = Review.query.filter_by(product_id=product_id)
    reviews_paginated = reviews_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    reviews = reviews_schema.dump(reviews_paginated.items)

    return jsonify(
        {
            "id": product.id,
            "asin": product.asin,
            "title": product.title,
            "reviews": reviews,
            "total_reviews": reviews_paginated.total,
            "pages": reviews_paginated.pages,
            "current_page": reviews_paginated.page,
            "per_page": reviews_paginated.per_page,
        }
    )


@bp.route("/reviews", methods=["POST"])
def add_review():
    """
    Add a new review for a product.

    :return: Success message
    """

    data = request.get_json()
    logging.info("Add review endpoint accessed")
    errors = review_schema.validate(data)
    if errors:
        logging.warning(f"Validation errors: {errors}")
        return jsonify(errors), 400
    new_review = review_schema.load(data, session=db.session)
    db.session.add(new_review)
    db.session.commit()
    cache.delete(f"view/{new_review.product_id}")
    logging.info(f"Review added: {new_review}")
    return jsonify({"message": "Review added successfully"}), 201
