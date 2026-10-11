"""ระบบสั่งอาหารผ่านเมนูบนหน้าจอ (Console application)."""
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


def ensure_utf8_console():
    """ตั้งค่า console ให้รองรับภาษาไทยบน Windows ได้ดีขึ้น"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")


@dataclass
class Food:
    food_id: int
    name: str
    price: float
    category: str = "อาหารจานหลัก"
    image_url: str = ""

    def display(self) -> str:
        return f"{self.food_id:>2}. {self.name:<25} {self.price:>7.2f} บาท"


@dataclass
class OrderItem:
    food: Food
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.food.price * self.quantity


class Menu:
    """เก็บรายการอาหารและให้ค้นหา/แสดงเมนู"""

    DEFAULT_ITEMS = [
        Food(1, "ข้าวกะเพราหมู", 55, "อาหารจานเดียว"),
        Food(2, "ข้าวผัดไก่", 50, "อาหารจานเดียว"),
        Food(3, "ผัดไทย", 60, "เส้น"),
        Food(4, "ก๋วยเตี๋ยวหมู", 50, "เส้น"),
        Food(5, "ข้าวไข่เจียว", 40, "อาหารจานเดียว"),
        Food(6, "ชาเย็น", 25, "เครื่องดื่ม"),
        Food(7, "น้ำเปล่า", 10, "เครื่องดื่ม"),
    ]

    def __init__(self, foods: Optional[Iterable[Food]] = None, csv_path: Optional[str] = None):
        if foods is not None:
            self.foods = list(foods)
            return

        menu_path = Path(csv_path) if csv_path else Path(__file__).resolve().parents[1] / "data" / "menu_sample.csv"
        self.foods = self._load_from_csv(menu_path)

    def _load_from_csv(self, csv_path: Path):
        try:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                loaded = [
                    Food(
                        food_id=int(row["food_id"]),
                        name=row["name"].strip(),
                        price=float(row["price"]),
                        category=row.get("category", "อาหารจานหลัก").strip() or "อาหารจานหลัก",
                    )
                    for row in reader
                ]
            if loaded:
                return loaded
        except (FileNotFoundError, ValueError, KeyError):
            pass
        return self.DEFAULT_ITEMS

    def show(self):
        print("\n========== เมนูอาหาร ==========")
        current_category = None
        for food in self.foods:
            if current_category != food.category:
                current_category = food.category
                print(f"\n[{current_category}]")
            print(food.display())
        print("===============================")

    def find(self, food_id: int):
        return next((food for food in self.foods if food.food_id == food_id), None)


class Order:
    """จัดการตะกร้าและคำนวณยอดสั่งซื้อ"""

    def __init__(self, customer_name: str):
        self.customer_name = customer_name
        self.items: List[OrderItem] = []

    def add_item(self, food: Food, quantity: int):
        if quantity <= 0:
            raise ValueError("จำนวนต้องมากกว่า 0")
        for item in self.items:
            if item.food.food_id == food.food_id:
                item.quantity += quantity
                return
        self.items.append(OrderItem(food, quantity))

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def show_receipt(self):
        if not self.items:
            print("ยังไม่มีสินค้าในตะกร้า")
            return
        print("\n========== ใบสรุปรายการ ==========")
        print(f"ลูกค้า: {self.customer_name}")
        for item in self.items:
            print(f"{item.food.name} x {item.quantity} = {item.subtotal:.2f} บาท")
        print("---------------------------------")
        print(f"ยอดรวม: {self.total:.2f} บาท")
        print("=================================")


class FoodOrderingApp:
    def __init__(self):
        ensure_utf8_console()
        self.menu = Menu()
        self.order = None

    @staticmethod
    def read_int(prompt: str):
        try:
            return int(input(prompt))
        except ValueError:
            print("กรุณากรอกตัวเลขจำนวนเต็ม")
            return None

    def run(self):
        print("=================================")
        print("       ระบบสั่งอาหาร Python       ")
        print("=================================")
        name = input("กรุณากรอกชื่อลูกค้า: ").strip() or "ลูกค้าทั่วไป"
        self.order = Order(name)
        while True:
            print("\n1. ดูเมนูอาหาร\n2. เพิ่มอาหารลงตะกร้า\n3. ดูรายการและยอดรวม\n4. ยืนยันคำสั่งซื้อ\n0. ออกจากโปรแกรม")
            choice = input("เลือกเมนู: ").strip()
            if choice == "1":
                self.menu.show()
            elif choice == "2":
                self.menu.show()
                food_id = self.read_int("รหัสอาหารที่ต้องการ: ")
                if food_id is None:
                    continue
                food = self.menu.find(food_id)
                if not food:
                    print("ไม่พบรหัสอาหารนี้")
                    continue
                quantity = self.read_int("จำนวนที่ต้องการ: ")
                if quantity is None or quantity <= 0:
                    print("จำนวนต้องเป็นเลขมากกว่า 0")
                    continue
                self.order.add_item(food, quantity)
                print(f"เพิ่ม {food.name} จำนวน {quantity} รายการแล้ว")
            elif choice == "3":
                self.order.show_receipt()
            elif choice == "4":
                if not self.order.items:
                    print("กรุณาเลือกอาหารก่อนยืนยันคำสั่งซื้อ")
                    continue
                self.order.show_receipt()
                print("รับคำสั่งซื้อเรียบร้อย ขอบคุณที่ใช้บริการ!")
                break
            elif choice == "0":
                print("ขอบคุณที่ใช้บริการ")
                break
            else:
                print("กรุณาเลือกเมนู 0-4")
