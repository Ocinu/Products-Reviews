import pytest
from core.app import create_app
from core.db import db as flask_db, Product, Review


@pytest.fixture(scope="module")
def app():
    test_config = {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    app = create_app(test_config)
    with app.app_context():
        flask_db.create_all()
        yield app
        flask_db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def init_database():
    product = Product(asin="B00136J4YU", title="Test Product")
    review1 = Review(product_id=1, review="Great product!")
    review2 = Review(product_id=1, review="Not bad.")

    flask_db.session.add(product)
    flask_db.session.add(review1)
    flask_db.session.add(review2)
    flask_db.session.commit()

    yield

    flask_db.session.remove()
    flask_db.drop_all()


def test_get_product(client, init_database):
    response = client.get("/products/1?page=1&per_page=1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["asin"] == "B00136J4YU"
    assert data["title"] == "Test Product"
    assert len(data["reviews"]) == 1
    assert data["total_reviews"] == 2
    assert data["pages"] == 2
    assert data["current_page"] == 1
    assert data["per_page"] == 1


def test_add_review(client, init_database):
    new_review = {"product_id": 1, "review": "Excellent!"}
    response = client.post("/reviews", json=new_review)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Review added successfully"

    response = client.get("/products/1")
    data = response.get_json()
    assert len(data["reviews"]) == 3


def test_add_review_invalid_product(client, init_database):
    new_review = {"product_id": 999, "review": "This product does not exist!"}
    response = client.post("/reviews", json=new_review)
    assert response.status_code == 400
    data = response.get_json()
    assert "product_id" in data
    assert data["product_id"][0] == "Product does not exist."


def test_add_review_invalid_data(client, init_database):
    new_review = {"product_id": 1, "review": ""}
    response = client.post("/reviews", json=new_review)
    assert response.status_code == 400
    data = response.get_json()
    assert "review" in data
    assert data["review"][0] == "Shorter than minimum length 1."
