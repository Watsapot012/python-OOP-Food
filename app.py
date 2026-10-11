import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

from src.food_ordering import Food, Menu

app = Flask(__name__)
app.secret_key = "food_order_demo_key"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "food_order.db"
CSV_PATH = BASE_DIR / "data" / "menu_sample.csv"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS foods (
                food_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                image_url TEXT NOT NULL DEFAULT ''
            )
            """
        )
        food_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(foods)").fetchall()
        }
        if "image_url" not in food_columns:
            conn.execute("ALTER TABLE foods ADD COLUMN image_url TEXT NOT NULL DEFAULT ''")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                items TEXT NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        food_count = conn.execute("SELECT COUNT(*) FROM foods").fetchone()[0]
        if food_count == 0:
            menu = Menu(csv_path=str(CSV_PATH)).foods
            conn.executemany(
                "INSERT INTO foods (food_id, name, price, category) VALUES (?, ?, ?, ?)",
                [(food.food_id, food.name, food.price, food.category) for food in menu],
            )


def get_menu():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM foods ORDER BY food_id").fetchall()
    if rows:
        return [
            Food(
                row["food_id"],
                row["name"],
                row["price"],
                row["category"],
                row["image_url"],
            )
            for row in rows
        ]
    return Menu(csv_path=str(CSV_PATH)).foods


def build_cart_items():
    cart = session.get("cart", {})
    menu_by_id = {food.food_id: food for food in get_menu()}
    items = []
    total = 0.0
    for food_id_str, quantity in cart.items():
        food = menu_by_id.get(int(food_id_str))
        if not food:
            continue
        qty = int(quantity)
        subtotal = food.price * qty
        total += subtotal
        items.append({
            "food_id": food.food_id,
            "name": food.name,
            "quantity": qty,
            "price": food.price,
            "subtotal": subtotal,
        })
    return items, total


@app.route("/")
def index():
    cart_items, total = build_cart_items()
    return render_template("index.html", menu=get_menu(), cart_items=cart_items, total=total)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    food_id = int(request.form.get("food_id"))
    quantity = int(request.form.get("quantity", 1))
    if quantity <= 0:
        return redirect(url_for("index"))

    cart = session.setdefault("cart", {})
    cart[str(food_id)] = cart.get(str(food_id), 0) + quantity
    session["cart"] = cart
    return redirect(url_for("index"))


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", {})
    customer_name = (request.form.get("customer_name") or "ลูกค้าทั่วไป").strip() or "ลูกค้าทั่วไป"
    if not cart:
        return redirect(url_for("index"))

    menu_by_id = {food.food_id: food for food in get_menu()}
    items = []
    total = 0.0
    for food_id_str, quantity in cart.items():
        food = menu_by_id.get(int(food_id_str))
        if not food:
            continue
        qty = int(quantity)
        subtotal = food.price * qty
        total += subtotal
        items.append({
            "food_id": food.food_id,
            "name": food.name,
            "quantity": qty,
            "price": food.price,
            "subtotal": subtotal,
        })

    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO orders (customer_name, items, total) VALUES (?, ?, ?)",
            (customer_name, json.dumps(items, ensure_ascii=False), total),
        )
    session["cart"] = {}
    return render_template("receipt.html", customer_name=customer_name, items=items, total=total)


@app.route("/admin")
def admin():
    with get_db_connection() as conn:
        orders = conn.execute(
            "SELECT * FROM orders ORDER BY id DESC LIMIT 20"
        ).fetchall()
    history = []
    for order in orders:
        history.append({
            "customer_name": order["customer_name"],
            "items": json.loads(order["items"]),
            "total": order["total"],
            "created_at": order["created_at"],
        })
    return render_template("admin.html", menu=get_menu(), history=history)


@app.route("/admin/menu/add", methods=["GET", "POST"])
def add_menu_item():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            price = float(request.form.get("price", 0) or 0)
        except ValueError:
            return render_template(
                "add_menu_item.html",
                error="กรุณากรอกราคาเป็นตัวเลข",
                form=request.form,
            ), 400
        category = request.form.get("category", "อาหารจานหลัก").strip() or "อาหารจานหลัก"
        image_url = request.form.get("image_url", "").strip()
        if not name or price <= 0:
            return render_template(
                "add_menu_item.html",
                error="กรุณากรอกชื่อเมนูและราคาที่มากกว่า 0",
                form=request.form,
            ), 400
        if image_url and not image_url.startswith(("https://", "http://")):
            return render_template(
                "add_menu_item.html",
                error="ลิงก์รูปต้องขึ้นต้นด้วย http:// หรือ https://",
                form=request.form,
            ), 400
        with get_db_connection() as conn:
            next_id = conn.execute("SELECT COALESCE(MAX(food_id), 0) + 1 FROM foods").fetchone()[0]
            conn.execute(
                "INSERT INTO foods (food_id, name, price, category, image_url) VALUES (?, ?, ?, ?, ?)",
                (next_id, name, price, category, image_url),
            )
        return redirect(url_for("admin"))

    return render_template("add_menu_item.html", error=None, form={})


init_db()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
