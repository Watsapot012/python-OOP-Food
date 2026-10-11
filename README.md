# ระบบสั่งอาหารด้วย Python (Order Food)

โปรเจกต์ตัวอย่างสำหรับฝึกเขียนโปรแกรม Python โดยประยุกต์ใช้แนวคิด Object-Oriented Programming (OOP) ในระบบสั่งอาหารแบบ Console

## ผู้จัดทำ
- ชื่อ: นายวรรษพจน์ ศรีพลอยรุ่ง
- รหัสนักศึกษา: 674259012
- สาขาวิชา: วิศวกรรมซอฟต์แวร์

## ความสามารถ
- แสดงเมนูอาหารพร้อมราคาและประเภทอาหาร
- โหลดเมนูจากไฟล์ CSV ในโฟลเดอร์ data
- เลือกอาหารและระบุจำนวน
- เพิ่มอาหารลงตะกร้า (เพิ่มจำนวนรายการเดิมได้)
- แสดงใบสรุปรายการและคำนวณยอดรวม
- ยืนยันคำสั่งซื้อ
- ตรวจสอบข้อมูลนำเข้าที่ไม่ถูกต้องเบื้องต้น
- รองรับการแสดงภาษาไทยบน Windows ได้ดีขึ้น

## โครงสร้างโปรเจกต์
```text
order_food_py/
├── main.py
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── food_ordering.py
├── tests/
│   └── test_food_ordering.py
└── data/
    └── menu_sample.csv
```

## วิธีใช้งาน
ต้องติดตั้ง Python 3.10 ขึ้นไป

### เวอร์ชัน Console
```bash
python main.py
```

### เวอร์ชัน Web (Flask)
```bash
pip install -r requirements.txt
python app.py
```
แล้วเปิดเบราว์เซอร์ไปที่:
- http://localhost:5000
- http://localhost:5000/admin

หากต้องการสร้างฐานข้อมูลเริ่มต้นอีกครั้ง:
```bash
python init_demo_data.py
```

## แนวคิด OOP ที่ใช้
- **Class และ Object:** `Food`, `Menu`, `OrderItem`, `Order`, `FoodOrderingApp`
- **Encapsulation:** รวมข้อมูลและพฤติกรรมที่เกี่ยวข้องไว้ในแต่ละคลาส
- **Composition:** `Order` เก็บรายการ `OrderItem` และแต่ละรายการอ้างอิง `Food`
- **Properties:** ใช้ `subtotal` และ `total` คำนวณยอดโดยไม่เก็บค่าซ้ำ
- **Methods:** แยกหน้าที่ เช่น `show()`, `add_item()` และ `show_receipt()`

> หมายเหตุ: เป็นโปรแกรมตัวอย่างที่ทำงานผ่าน Terminal/Console ยังไม่ได้เชื่อมฐานข้อมูล ระบบชำระเงิน หรือหน้าร้านบนเว็บไซต์
