from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

cart = []
orders = []
order_counter = 1


class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: Optional[bool] = True


class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


def calculate_total(product, quantity):
    return product["price"] * quantity


@app.get("/")
def home():
    return {"message": "Welcome to the Product API"}


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    return {"products": filtered, "count": len(filtered)}


@app.get("/products/instock")
def get_instock():
    filtered = [p for p in products if p["in_stock"]]
    return {"products": filtered, "count": len(filtered)}


@app.get("/products/search/{product_name}")
def search_product(product_name: str):
    result = [p for p in products if product_name.lower() in p["name"].lower()]
    return {"results": result, "count": len(result)}


@app.get("/products/price/{max_price}")
def price_filter(max_price: int):
    filtered = [p for p in products if p["price"] <= max_price]
    return {"products": filtered, "count": len(filtered)}


@app.get("/products/filter")
def filter_products(category: Optional[str] = None, max_price: Optional[int] = None):
    filtered = products

    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]

    if max_price:
        filtered = [p for p in filtered if p["price"] <= max_price]

    return {"products": filtered, "count": len(filtered)}


@app.get("/products/summary")
def summary():
    total_value = sum(p["price"] for p in products)
    return {"total_products": len(products), "total_value": total_value}


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


@app.put("/products/discount")
def bulk_discount(category: str = Query(...), discount_percent: int = Query(..., ge=1, le=99)):
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


@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    return product


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


@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None, response: Response = None):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}


@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    subtotal = calculate_total(product, quantity)

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {"message": "Added to cart", "cart_item": cart_item}


@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Product removed from cart"}

    raise HTTPException(status_code=404, detail="Product not in cart")


@app.post("/cart/checkout")
def checkout(order: Checkout):

    global order_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    placed_orders = []
    grand_total = 0

    for item in cart:

        order_data = {
            "order_id": order_counter,
            "customer_name": order.customer_name,
            "delivery_address": order.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }

        orders.append(order_data)
        placed_orders.append(order_data)

        grand_total += item["subtotal"]
        order_counter += 1

    cart.clear()

    return {
        "message": "Order placed successfully",
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }


@app.get("/orders")
def get_orders():
    return {"orders": orders, "total_orders": len(orders)}