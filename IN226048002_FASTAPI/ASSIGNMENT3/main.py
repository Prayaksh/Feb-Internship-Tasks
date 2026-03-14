from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Initial product data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]


# Model for adding product
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: Optional[bool] = True


# Utility function
def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# Root
@app.get("/")
def home():
    return {"message": "Welcome to the Product API"}


# Get all products
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# Category filter
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    return {"products": filtered, "count": len(filtered)}


# In-stock filter
@app.get("/products/instock")
def get_instock():
    filtered = [p for p in products if p["in_stock"]]
    return {"products": filtered, "count": len(filtered)}


# Search product
@app.get("/products/search/{product_name}")
def search_product(product_name: str):
    result = [p for p in products if product_name.lower() in p["name"].lower()]
    return {"results": result, "count": len(result)}


# Price filter
@app.get("/products/price/{max_price}")
def price_filter(max_price: int):
    filtered = [p for p in products if p["price"] <= max_price]
    return {"products": filtered, "count": len(filtered)}


# Query filter
@app.get("/products/filter")
def filter_products(category: Optional[str] = None, max_price: Optional[int] = None):
    filtered = products

    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]

    if max_price:
        filtered = [p for p in filtered if p["price"] <= max_price]

    return {"products": filtered, "count": len(filtered)}


# Summary
@app.get("/products/summary")
def summary():
    total_value = sum(p["price"] for p in products)
    return {"total_products": len(products), "total_value": total_value}


# ----------- Q5 REQUIRED ENDPOINT -----------

@app.get("/products/audit")
def product_audit():
    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }


# ----------- BONUS ENDPOINT -----------

@app.put("/products/discount")
def bulk_discount(
    category: str = Query(...),
    discount_percent: int = Query(..., ge=1, le=99)
):

    updated = []

    for p in products:
        if p["category"].lower() == category.lower():
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"message": f"No products found in category: {category}"}

    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_count": len(updated),
        "updated_products": updated
    }


# Get product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    return product


# Add product
@app.post("/products")
def add_product(product: NewProduct, response: Response):

    for p in products:
        if p["name"].lower() == product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product with this name already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    response.status_code = status.HTTP_201_CREATED
    return {"message": "Product added", "product": new_product}


# Update product
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: Optional[int] = None,
    in_stock: Optional[bool] = None,
    response: Response = None
):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}


# Delete product
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}