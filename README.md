# Flask Products Reviews API

## Task Description

Create a mini-application that:

1. Parses two CSV files (Products, Reviews) downloaded locally and saves the data to a database (Postgres).
2. Implements an API endpoint (GET) that returns data in JSON format:
   - By product id, return information about the product (ASIN, Title) and reviews of this product with pagination.
3. Implements a second API endpoint (POST) that adds a new review for a product (by its id).
4. The project should be Dockerized.

## Requirements

- Python 3
- Flask
- PEP 8
- Postgres DB (can be as a Docker container)
- `requirements.txt` or `Pipfile`


## Steps to Run the Project

1. **Rename .env.example to .env and setup variables**

2. **Start the Docker containers and fill db:**
   ```bash
   make setup

## Testing Instructions

1. **Run the tests:**
   ```bash
   pytest
   
## API Endpoints

### GET /products/<int:id>
Returns information about the product and its reviews with pagination.

**Request:**
```http
GET /products/1?page=1&per_page=10
```

**Responce:**
```http
{
  "asin": "B06X14Z8JP",
  "current_page": 1,
  "pages": 1,
  "per_page": 10,
  "reviews": [
    {
      "id": 1,
      "product": 1,
      "product_id": 1,
      "review": "Horrible product!!! Hasn\u2019t lasted 8 weeks! Battery does not hold a charge. Do Not Buy This Product!!!!"
    },
    {
      "id": 2,
      "product": 1,
      "product_id": 1,
      "review": "sound quality POOR"
    },
    {
      "id": 4,
      "product": 1,
      "product_id": 1,
      "review": "Broke after one use! I expected more more from This company but they were cheaply made and your better off getting a pair at the dollar tree!"
    }
  ],
  "title": "JVC Blue and Red Wireless Water Resistant Pivot Motion Sport Headphone with Locking Ear Fit HA-ET50BTA",
  "total_reviews": 3
}
```

### POST /reviews
Adds a new review for a product.

**Request:**
```http
POST /reviews
Content-Type: application/json

{
    "product_id": 1,
    "review": "Excellent!"
}

```

**Responce:**
```http
{
    "message": "Review added successfully"
}
```
