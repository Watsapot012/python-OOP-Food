import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.food_ordering import Food, Menu, Order

class FoodOrderingTests(unittest.TestCase):
    def test_add_item_and_total(self):
        food = Food(1, "ข้าวกะเพราหมู", 55)
        order = Order("ทดสอบ")
        order.add_item(food, 2)
        self.assertEqual(order.total, 110)

    def test_same_food_merges_quantity(self):
        food = Food(1, "ข้าวกะเพราหมู", 55)
        order = Order("ทดสอบ")
        order.add_item(food, 1)
        order.add_item(food, 2)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 3)
        self.assertEqual(order.total, 165)

    def test_menu_find(self):
        menu = Menu()
        self.assertEqual(menu.find(1).name, "ข้าวกะเพราหมู")
        self.assertIsNone(menu.find(999))

    def test_quantity_must_be_positive(self):
        order = Order("ทดสอบ")
        with self.assertRaises(ValueError):
            order.add_item(Food(1, "ข้าว", 40), 0)

if __name__ == "__main__":
    unittest.main()
