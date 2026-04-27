from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import traceback
 
app = Flask(__name__)
 
# ─────────────────────────────────────────────
#  DATABASE CONNECTION
#  Update these credentials to match your setup
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "Ijcrs@123",
    "database": "stupify",
    "autocommit": True
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
    try:
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
    
    except Exception as e:
        print(f"\n\n❌ ERROR in /records.html: {e}")
        traceback.print_exc()
        return f"<h1>Database Error</h1><p style='color:red;'><strong>{str(e)}</strong></p><p>Check your terminal for details.</p>", 500
 
 
@app.route("/add.html", methods=["GET", "POST"])
def add_product():
    message = ""
    error = ""
 
    if request.method == "POST":
        try:
            name     = request.form.get("name", "").strip()
            price    = request.form.get("price", "").strip()
            category = request.form.get("category", "").strip()
            stocks   = request.form.get("stocks", "").strip()
 
            if not all([name, price, category, stocks]):
                error = "All fields are required."
            else:
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
                print(f"✓ Product added: {name}")
        except Exception as e:
            print(f"\n\n❌ ERROR in /add.html: {e}")
            traceback.print_exc()
            error = f"Database error: {str(e)}"
 
    return render_template("add.html", message=message, error=error)
 
 
@app.route("/ReadMe.html")
def readme():
    return render_template("ReadMe.html")
 
 
# ─────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
