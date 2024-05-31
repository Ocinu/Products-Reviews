import pandas as pd
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    reviews = db.relationship('Review', backref='product', lazy=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    review = db.Column(db.Text, nullable=False)


def load_data():
    products_path = 'data/Products.csv'
    reviews_path = 'data/Reviews.csv'

    products_df = pd.read_csv(products_path)
    reviews_df = pd.read_csv(reviews_path)

    db.drop_all()
    db.create_all()

    products = [Product(asin=row['Asin'], title=row['Title']) for index, row in products_df.iterrows()]
    db.session.bulk_save_objects(products)
    db.session.commit()

    reviews = []
    for index, row in reviews_df.iterrows():
        product = Product.query.filter_by(asin=row['Asin']).first()
        if product:
            review = Review(product_id=product.id, review=row['Review'])
            reviews.append(review)

    db.session.bulk_save_objects(reviews)
    db.session.commit()
