from fastapi import FastAPI

from fastapi import Query

from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {
        "id": 1,
        "name": "Notebook",
        "price": 50,
        "category": "Stationery",
        "in_stock": True
    },
    {
        "id": 2,
        "name": "Pen",
        "price": 10,
        "category": "Stationery",
        "in_stock": True
    },
    {
        "id": 3,
        "name": "Monitor",
        "price": 8999,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 4,
        "name": "Mouse",
        "price": 499,
        "category": "Electronics",
        "in_stock": False
    },
    {
        "id": 5,
        "name": "Laptop Stand",
        "price": 1299,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 6,
        "name": "Mechanical Keyboard",
        "price": 2499,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 7,
        "name": "Webcam",
        "price": 1899,
        "category": "Electronics",
        "in_stock": False
    }
]



@app.get("/")
def home():
    return {"message": "Welcome to the Product API"}


@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):

    result = [p for p in products if p["category"] == category_name]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }


@app.get("/products/instock")
def get_instock_products():

    instock = [p for p in products if p["in_stock"] == True]

    return {
        "in_stock_products": instock,
        "total": len(instock)
    }

@app.get("/products/search/{product_name}")
def search_product(product_name: str):

    result = [
        p for p in products
        if product_name.lower() in p["name"].lower()
    ]

    if not result:
        return {"error": "No products found"}

    return {
        "search_term": product_name,
        "products": result,
        "total": len(result)
    }


@app.get("/products/price/{max_price}")
def products_under_price(max_price: int):

    result = [p for p in products if p["price"] <= max_price]

    if not result:
        return {"error": "No products found under this price"}

    return {
        "max_price": max_price,
        "products": result,
        "total": len(result)
    }

@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    max_price: int = Query(None),
    min_price: int = Query(None)
):
    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return {"products": result}

@app.get("/products/summary")
def product_summary():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {
            "name": expensive["name"],
            "price": expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }




@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    return {"error": "Product not found"}

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}


@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock = len([p for p in products if p["in_stock"]])
    out_of_stock = total_products - in_stock

    total_value = sum(p["price"] for p in products)

    return {
        "total_products": total_products,
        "in_stock_products": in_stock,
        "out_of_stock_products": out_of_stock,
        "total_store_value": total_value
    }

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

feedback = []

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next(
            (p for p in products if p["id"] == item.product_id),
            None
        )

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })

        elif not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })

        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal

            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }