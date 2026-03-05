from fastapi import FastAPI

app = FastAPI()

products = [
    {"id":1,"name":"Wireless Mouse","price":499,"category":"Electronics","in_stock":True},
    {"id":2,"name":"Notebook","price":99,"category":"Stationery","in_stock":True},
    {"id":3,"name":"USB Hub","price":799,"category":"Electronics","in_stock":False},
    {"id":4,"name":"Pen Set","price":49,"category":"Stationery","in_stock":True},
    {"id":5,"name":"Laptop Stand","price":1299,"category":"Electronics","in_stock":True},
    {"id":6,"name":"Mechanical Keyboard","price":2499,"category":"Electronics","in_stock":True},
    {"id":7,"name":"Webcam","price":1899,"category":"Electronics","in_stock":False}
]

# Q1
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

# Q2
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

# Q3
@app.get("/products/instock")
def get_instock():
    available = [p for p in products if p["in_stock"]]

    return {
        "in_stock_products": available,
        "count": len(available)
    }

# Q4
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p

    return {"error": "Product not found"}

# Q5
@app.get("/products/price/{price}")
def get_by_price(price: int):
    result = [p for p in products if p["price"] <= price]

    return {
        "products": result,
        "total": len(result)
    }
