# Code Review Report: `inventory_service.py` (Lab 04: ขั้นที่ 8)

> **Pull Request:** AI-Generated `InventoryService` implementation  
> **Reviewer:** ธนภัทร (67332310017-9)  
> **ผลการประเมินเบื้องต้น:** **Request Changes (ห้าม Merge เข้า Main Branch)**  
> โค้ดชุดนี้แม้จะ compile ผ่าน หน้าตาเป็นระเบียบ และมี docstring ดูครบถ้วน แต่จากการตรวจสอบเชิงลึกพบ Bug แฝงที่สร้างความเสียหายร้ายแรง (High Severity) ถึง 4 จุด และ Medium Severity อีก 2 จุด ซึ่งครอบคลุมทั้งปัญหา Non-atomic Transaction, Concurrency Race Condition, Unhandled Crash และ Logic ผิดเพี้ยนจากข้อกำหนด

---

## 1. รายละเอียดการ Review รายเมธอด (Detailed Review Comments)

### [จุดที่ 1] เมธอด `sell_batch` (บรรทัดที่ 16 - 22)
- **ตำแหน่ง:** เมธอด `sell_batch`, บรรทัดที่ 19–21
- **ทำไมถึงผิด:** ขาดคุณสมบัติความปลอดภัยของธุรกรรม (Lack of Atomicity / No Rollback) โค้ดวนลูปตัดสต็อกสินค้าทีละรายการผ่าน `self._inv.sell(name, amount)` หากสินค้าชิ้นแรก ๆ ตัดผ่าน แต่ชิ้นถัดไปเกิดข้อผิดพลาด (เช่น สินค้าไม่พอ หรือไม่พบชื่อสินค้า) ฟังก์ชันจะโยน Exception หลุดออกไปทันที โดยปล่อยให้สินค้าที่ตัดสำเร็จไปแล้วค้างอยู่ในสถานะตัดสต็อก ยอดสต็อกในระบบจึงไม่ตรงกับคำสั่งซื้อจริง
- **กรณีที่ทำให้พัง (พร้อมตัวอย่างค่า):**
  - สมมติในคลังมีสินค้า: `"ปากกา": 5 ชิ้น`, `"สมุด": 2 ชิ้น`
  - มีคำสั่งซื้อ batch: `orders = {"ปากกา": 3, "สมุด": 10}`
  - ในรอบแรก `"ปากกา"` ถูกตัดสำเร็จคงเหลือ 2 ชิ้น
  - ในรอบสอง `"สมุด"` มีแค่ 2 ชิ้น แต่ขอตัด 10 ชิ้น จึงเกิด `ValueError` จาก `Inventory.sell`
  - **ผลลัพธ์ที่พัง:** Transaction ล้มเหลว คำสั่งซื้อไม่สำเร็จ แต่ `"ปากกา"` ในคลังถูกตัดหายไปแล้ว 3 ชิ้นฟรี ๆ โดยไม่มีการคืนค่า (Inconsistent State)
- **ข้อเสนอแนะในการแก้ไข:**
  ทำการตรวจสอบความพร้อมของสต็อกสินค้าทุกรายการให้ครบถ้วนก่อนเริ่มตัดจริง (Dry-run Validation) หรือบันทึกรายการที่ตัดไปแล้ว หากเกิด Error ให้ทำ Rollback คืนสต็อกทั้งหมดก่อน raise Exception

```python
def sell_batch(self, orders: dict[str, int]) -> dict[str, int]:
    # 1. ตรวจสอบสต็อกทุกรายการก่อน (All-or-Nothing check)
    for name, amount in orders.items():
        if name not in self._inv._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
        if self._inv._items[name].quantity < amount:
            raise ValueError(f"สินค้า '{name}' มีไม่พอสำหรับการขาย {amount} ชิ้น")
            
    # 2. เมื่อมั่นใจว่าผ่านทุกรายการ จึงเริ่มตัดสต็อกจริง
    result = {}
    for name, amount in orders.items():
        result[name] = self._inv.sell(name, amount)
    return result
```

---

### [จุดที่ 2] เมธอด `reserve` (บรรทัดที่ 25 - 31)
- **ตำแหน่ง:** เมธอด `reserve`, บรรทัดที่ 27 และ 29–31
- **ทำไมถึงผิด:**
  1. เข้าถึง `self._inv._items[name]` โดยตรงโดยไม่ตรวจว่ามีสินค้านี้หรือไม่ หากไม่มีจะเกิด `KeyError` ที่ไม่มีข้อความอธิบาย
  2. ไม่มีการตรวจสอบ `amount <= 0`
  3. **Bug ร้ายแรงที่ทำให้เกิด Crash:** หากสินค้าเพิ่งถูกจองเป็นครั้งแรก (ยังไม่มี key ใน `self._reserved`) และผู้ใช้ขอจอง `amount` มากกว่าจำนวนคงเหลือ เงื่อนไขในบรรทัด 29 `amount <= item.quantity - already` จะเป็นเท็จ ทำให้ไม่เข้า if และไม่มีการสร้าง key ใน `self._reserved` เมื่อมาถึงบรรทัดที่ 31 `item.quantity - self._reserved[name]` จะเกิด `KeyError: name` ทำให้โปรแกรม Crash ทันที
- **กรณีที่ทำให้พัง (พร้อมตัวอย่างค่า):**
  - คลังมี `"ยางลบ"` 3 ชิ้น โดยยังไม่เคยมีการจองมาก่อน (`self._reserved` ว่างเปล่า)
  - ผู้ใช้เรียก `reserve("ยางลบ", 5)` (ขอจองเกินจำนวนที่มี)
  - `already = 0`, เงื่อนไข `5 <= 3 - 0` เป็นเท็จ (ไม่เข้า if)
  - บรรทัดที่ 31 สั่งคำนวณ `3 - self._reserved["ยางลบ"]`
  - **ผลลัพธ์ที่พัง:** เกิด `KeyError: 'ยางลบ'` ระบบล่มทันที แทนที่จะคืนค่าจำนวนที่ยังจองได้
- **ข้อเสนอแนะในการแก้ไข:**
  ใช้ `.get(name, 0)` สำหรับคำนวณค่าคงเหลือเสมอ และตรวจเช็ก `amount > 0` รวมถึงตรวจว่ามีสินค้าในคลังหรือไม่

```python
def reserve(self, name: str, amount: int) -> int:
    if name not in self._inv._items:
        raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
    if amount <= 0:
        raise ValueError("จำนวนที่จองต้องมากกว่าศูนย์")
        
    item = self._inv._items[name]
    already = self._reserved.get(name, 0)
    available = item.quantity - already
    
    if amount <= available:
        self._reserved[name] = already + amount
        return item.quantity - self._reserved[name]
    return available  # คืนจำนวนที่ยังจองได้
```

---

### [จุดที่ 3] เมธอด `items_in_price_range` (บรรทัดที่ 34 - 40)
- **ตำแหน่ง:** เมธอด `items_in_price_range`, บรรทัดที่ 38
- **ทำไมถึงผิด:** Docstring สัญกรณ์ทางคณิตศาสตร์ระบุว่า `[low, high]` ซึ่งหมายถึงช่วงปิด (Inclusive: รวมหัวและท้าย) แต่โค้ดในบรรทัดที่ 38 เขียนเป็นช่วงเปิด `low < item.price < high` (Strict Inequality) ทำให้สินค้าที่มีราคาเท่ากับ `low` หรือเท่ากับ `high` พอดีหลุดออกจากผลการค้นหา
- **กรณีที่ทำให้พัง (พร้อมตัวอย่างค่า):**
  - คลังมีสินค้า: `"ไม้บรรทัด"` ราคา 20.00 บาท และ `"กรรไกร"` ราคา 50.00 บาท
  - ผู้จัดการต้องการค้นหาช่วง `items_in_price_range(20.0, 50.0)`
  - **ผลลัพธ์ที่พัง:** ฟังก์ชันคืนค่าเป็น list ว่าง `[]` ทั้งที่มีสินค้าตรงช่วงราคาถึง 2 ชิ้น
- **ข้อเสนอแนะในการแก้ไข:**
  เปลี่ยนตัวดำเนินการเปรียบเทียบเป็น `<=`:

```python
def items_in_price_range(self, low: float, high: float) -> list:
    """คืนรายชื่อสินค้าที่ราคาอยู่ในช่วง [low, high] (รวมขอบเขตทั้งสองด้าน)"""
    if low > high:
        raise ValueError("ราคาเริ่มต้น (low) ต้องไม่มากกว่าราคาสิ้นสุด (high)")
    names = []
    for name, item in self._inv._items.items():
        if low <= item.price <= high:
            names.append(name)
    return names
```

---

### [จุดที่ 4] เมธอด `low_stock_report` (บรรทัดที่ 43 - 49)
- **ตำแหน่ง:** เมธอด `low_stock_report`, บรรทัดที่ 47
- **ทำไมถึงผิด:** Docstring ระบุชัดเจนว่า *"คืนรายชื่อสินค้าที่ stock ต่ำกว่าหรือเท่ากับเกณฑ์"* แต่โค้ดใช้เงื่อนไข `item.quantity < self.LOW_STOCK_THRESHOLD` (น้อยกว่าอย่างเดียว) ขาดกรณีเท่ากับไป
- **กรณีที่ทำให้พัง (พร้อมตัวอย่างค่า):**
  - ค่าคงที่ `LOW_STOCK_THRESHOLD = 5`
  - คลังมีสินค้า `"กระดาษ A4"` คงเหลือ 5 ริมพอดี
  - **ผลลัพธ์ที่พัง:** เมื่อเรียก `low_stock_report()` รายการ `"กระดาษ A4"` ไม่ปรากฏในรายงาน ทำให้ผู้จัดการไม่ทราบว่าสต็อกถึงจุดวิกฤตและไม่ได้สั่งของเพิ่ม จนของหมดคลังในที่สุด
- **ข้อเสนอแนะในการแก้ไข:**
  แก้ไขเงื่อนไขเป็น `<=` เพื่อให้ตรงตาม Requirement ใน Docstring:

```python
def low_stock_report(self) -> list:
    """คืนรายชื่อสินค้าที่ stock ต่ำกว่าหรือเท่ากับเกณฑ์"""
    report = []
    for name, item in self._inv._items.items():
        if item.quantity <= self.LOW_STOCK_THRESHOLD:
            report.append(name)
    return report
```

---

### [จุดที่ 5] เมธอด `concurrent_restock` (บรรทัดที่ 52 - 57)
- **ตำแหน่ง:** เมธอด `concurrent_restock`, บรรทัดที่ 54–56
- **ทำไมถึงผิด:** เกิดข้อบกพร่องเรื่องความพร้อมกัน (Concurrency Bug / Race Condition / Lost Update) เนื่องจากบรรทัดที่ 54 ทำการอ่านค่า `current = self._inv._items[name].quantity` **อยู่นอกบล็อก `with self._lock:`** ทำให้การทำงานขาดความเป็น Atomic Operation หากมีหลาย Thread เข้ามาทำงานพร้อมกัน จะได้ค่า `current` เดียวกันไปคำนวณและเขียนทับผลลัพธ์ของกันและกัน
- **กรณีที่ทำให้พัง (พร้อมตัวอย่างค่า):**
  - สินค้า `"ปากกาลูกลื่น"` มีสต็อกเดิม 10 ชิ้น
  - พนักงาน 2 คน (Thread A และ Thread B) กดยืนยันเติมสต็อกคนละ 5 ชิ้นในเวลาเดียวกัน
  - Thread A และ B อ่าน `current` ได้ค่า 10 เท่ากันก่อนเข้า Lock
  - Thread A เข้า Lock คำนวณ `10 + 5 = 15` แล้วบันทึก
  - Thread B เข้า Lock คำนวณ `10 + 5 = 15` แล้วเขียนทับ
  - **ผลลัพธ์ที่พัง:** ยอดคงเหลือกลายเป็น 15 ชิ้น แทนที่จะเป็น 20 ชิ้น ยอดสินค้าหายไป 5 ชิ้น
- **ข้อเสนอแนะในการแก้ไข:**
  ย้ายการอ่านค่า `current` เข้าไปอยู่ภายใต้ `with self._lock:` หรือเรียกใช้ `self._inv.restock()` ภายใน Lock เพื่อให้มี Input Validation ไปในตัว

```python
def concurrent_restock(self, name: str, amount: int) -> int:
    """เติม stock โดยป้องกัน race condition"""
    with self._lock:
        if name not in self._inv._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่เติมต้องมากกว่าศูนย์")
        self._inv._items[name].quantity += amount
        return self._inv._items[name].quantity
```

---

### [จุดที่ 6] เมธอด `average_unit_value` (บรรทัดที่ 60 - 64)
- **ตำแหน่ง:** เมธอด `average_unit_value`, บรรทัดที่ 63–64
- **ทำไมถึงผิด:**
  1. **Crash จากตัวหารเป็น 0 (ZeroDivisionError):** หากคลังยังไม่มีสินค้า (`len(self._inv._items) == 0`) บรรทัดที่ 64 จะเกิด `ZeroDivisionError`
  2. **คำนวณผิดความหมายทางธุรกิจ (Logical Bug):** Docstring ระบุว่า *"มูลค่าเฉลี่ยต่อชิ้น"* แต่โค้ดนำมูลค่ารวมไปหารด้วย `len(self._inv._items)` ซึ่งคือ "จำนวนรายการสินค้า/SKU" ไม่ใช่ "จำนวนชิ้นสินค้าทั้งหมดในคลัง"
- **กรณีที่ทำให้พัง (พร้อมตัวอย่างค่า):**
  - **กรณี Crash:** เปิดระบบครั้งแรก `_items` ว่างเปล่า เรียก `average_unit_value()` เกิด `ZeroDivisionError: division by zero` ทันที
  - **กรณีคำนวณผิด:** คลังมีสินค้า 2 ชนิด:
    - ปากกา 100 ด้าม ด้ามละ 10 บาท (มูลค่า 1,000 บาท)
    - กล้องส่อง 1 ตัว ราคา 1,000 บาท (มูลค่า 1,000 บาท)
    - มูลค่ารวม = 2,000 บาท, จำนวนชิ้นทั้งหมด = 101 ชิ้น (เฉลี่ยชิ้นละ ~19.80 บาท)
    - แต่โค้ดเดิมคำนวณ `2,000 / 2 = 1,000 บาท/ชิ้น` ซึ่งผิดพลาดจากความเป็นจริงเกือบ 50 เท่า
- **ข้อเสนอแนะในการแก้ไข:**
  หาผลรวมของจำนวนชิ้นสินค้าทั้งหมด (`total_units`) หากเป็น 0 ให้คืนค่า `0.0` เพื่อป้องกัน Crash

```python
def average_unit_value(self) -> float:
    """คืนมูลค่าเฉลี่ยต่อชิ้นของสินค้าทั้งคลัง"""
    total_value = self._inv.get_total_value()
    total_units = sum(item.quantity for item in self._inv._items.values())
    if total_units == 0:
        return 0.0
    return total_value / total_units
```

---

## 2. ตารางสรุปการจัดหมวดและระดับความรุนแรงของปัญหา (Bug Summary Table)

| # | เมธอด | หมวด (Category) | ระดับ (Severity) | สรุปปัญหา | กรณีที่ทำให้พัง |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | `sell_batch` | `correctness` | `high` | ขาดคุณสมบัติ Atomicity หากเกิดข้อผิดพลาดกลางคัน สินค้าชิ้นก่อนหน้าถูกตัดค้างไว้โดยไม่ Rollback | สั่งซื้อ 2 รายการ ชิ้นแรกพอแต่ชิ้นสองไม่พอ ชิ้นแรกโดนตัดสต็อกฟรีแต่คำสั่งซื้อล้มเหลว |
| **2** | `reserve` | `correctness` | `high` | เมื่อจองสินค้าครั้งแรกเกินจำนวนคงเหลือ จะเกิด `KeyError` Crash ทันที และไม่มีการตรวจ `amount <= 0` | สินค้ามี 3 ชิ้น จองครั้งแรก 5 ชิ้น โปรแกรมล่มด้วย `KeyError` |
| **3** | `items_in_price_range` | `correctness` | `medium` | ใช้เงื่อนไขช่วงเปิด `<` แทนช่วงปิดตาม Docstring `[low, high]` ทำให้สินค้าที่มีราคาตรงกับขอบตกหล่น | ค้นหาช่วง 20-50 บาท สินค้าราคา 20 บาท หรือ 50 บาท ไม่แสดงในผลลัพธ์ |
| **4** | `low_stock_report` | `correctness` | `medium` | ใช้ `<` แทน `<=` ทำให้สินค้าที่สต็อกเหลือเท่ากับ `LOW_STOCK_THRESHOLD` พอดีไม่ถูกรายงาน | สต็อกเหลือ 5 ชิ้นพอดี (เท่ากับเกณฑ์) ไม่แสดงในรายงานเตือนของใกล้หมด |
| **5** | `concurrent_restock` | `concurrency` | `high` | อ่านค่า `current` อยู่นอกบล็อก Lock ทำให้เกิด Race Condition (Lost Update) ข้อมูลสูญหาย | มี 2 Thread เติมของชิ้นละ 5 ชิ้นพร้อมกัน ยอดเพิ่มขึ้นแค่ 5 แทนที่จะเป็น 10 |
| **6** | `average_unit_value` | `correctness` | `high` | เกิด `ZeroDivisionError` เมื่อคลังว่าง และสูตรนำไปหารด้วยจำนวนชนิดสินค้า (SKU) แทนจำนวนชิ้นรวม | คลังว่างโปรแกรมล่มทันที หรือคำนวณราคาเฉลี่ยต่อชิ้นเพี้ยนอย่างมหาศาล |
