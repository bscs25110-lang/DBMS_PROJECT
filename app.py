from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from init_db import init_database

# Initialize database on startup
init_database()
app = Flask(__name__)

# ─────────────────────────────────────────────
#  DATABASE CONNECTION
# ─────────────────────────────────────────────
import os
from urllib.parse import urlparse

# Parse Railway's MYSQL_URL
mysql_url = os.getenv('MYSQL_URL', 'mysql://root:miHObTyrvWuaZOgsCJjyKOlSUSYgMJcY@shortline.proxy.rlwy.net:58203/railway')   
parsed = urlparse(mysql_url)

DB_CONFIG = {
    "host": parsed.hostname,
    "port": 3306,
    "user": parsed.username,
    "password": parsed.password,
    "database": parsed.path.lstrip('/')
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@app.route("/")
@app.route("/home.html")
def home():
    return render_template("home.html")


@app.route("/records.html")
def records():
    search = request.args.get("search", "").strip()
    db = get_db()
    cursor = db.cursor()

    if search:
        cursor.execute(
            """
            SELECT p.Product_ID, p.product_name, c.CATEGORY_NAME, p.PRICE, p.STOCKS
            FROM PRODUCT p
            LEFT JOIN CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
            WHERE p.product_name LIKE %s
            ORDER BY p.Product_ID
            """,
            (f"%{search}%",)
        )
    else:
        cursor.execute(
            """
            SELECT p.Product_ID, p.product_name, c.CATEGORY_NAME, p.PRICE, p.STOCKS
            FROM PRODUCT p
            LEFT JOIN CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
            ORDER BY p.Product_ID
            """
        )

    products = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("records.html", products=products)


@app.route("/add.html", methods=["GET", "POST"])
def add_product():
    message = ""
    error = ""

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        price    = request.form.get("price", "").strip()
        category = request.form.get("category", "").strip()
        stocks   = request.form.get("stocks", "").strip()

        if not all([name, price, category, stocks]):
            error = "All fields are required."
        else:
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO PRODUCT (product_name, PRICE, CATEGORY_ID, STOCKS) VALUES (%s, %s, %s, %s)",
                    (name, float(price), int(category), int(stocks))
                )
                db.commit()
                cursor.close()
                db.close()
                message = f'Product "{name}" added successfully!'
            except mysql.connector.Error as e:
                error = f"Database error: {e}"

    return render_template("add.html", message=message, error=error)


@app.route("/ReadMe.html")
def readme():
    return render_template("ReadMe.html")


# ─────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
  if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
