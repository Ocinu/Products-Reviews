import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, request, jsonify
from flask_caching import Cache
from db import db, Product, Review
from schemas import ReviewSchema
from dotenv import load_dotenv

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CACHE_TYPE'] = 'SimpleCache'

    if test_config:
        app.config.update(test_config)

    cache = Cache(app)
    db.init_app(app)

    review_schema = ReviewSchema()
    reviews_schema = ReviewSchema(many=True)

    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_filename = datetime.now().strftime("logs/app_%Y-%m-%d.log")
    handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1)
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))

    if not app.debug:
        app.logger.addHandler(handler)
        app.logger.addHandler(logging.StreamHandler())

    @app.route('/')
    def home():
        app.logger.info("Home endpoint accessed")
        return "Welcome to products reviews!"

    @app.route('/products/<int:id>', methods=['GET'])
    @cache.cached(timeout=60, query_string=True)
    def get_product(id):
        app.logger.info(f"Product endpoint accessed with id: {id}")
        product = db.session.get(Product, id)
        if not product:
            app.logger.warning(f"Product with id {id} not found")
            return jsonify({'message': 'Product not found'}), 404

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        reviews_query = Review.query.filter_by(product_id=id)
        reviews_paginated = reviews_query.paginate(page=page, per_page=per_page, error_out=False)

        reviews = reviews_schema.dump(reviews_paginated.items)

        return jsonify({
            'asin': product.asin,
            'title': product.title,
            'reviews': reviews,
            'total_reviews': reviews_paginated.total,
            'pages': reviews_paginated.pages,
            'current_page': reviews_paginated.page,
            'per_page': reviews_paginated.per_page
        })

    @app.route('/reviews', methods=['POST'])
    def add_review():
        data = request.get_json()
        app.logger.info("Add review endpoint accessed")
        errors = review_schema.validate(data)
        if errors:
            app.logger.warning(f"Validation errors: {errors}")
            return jsonify(errors), 400
        new_review = review_schema.load(data, session=db.session)
        db.session.add(new_review)
        db.session.commit()
        app.logger.info(f"Review added: {new_review}")
        return jsonify({'message': 'Review added successfully'}), 201

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', True))
