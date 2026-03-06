from fastapi import FastAPI

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


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    return {"error": "Product not found"}

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