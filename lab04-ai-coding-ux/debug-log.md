# Debugging Log (5 ขั้นตอน) - Lab 04 (ขั้นที่ 10)

เอกสารบันทึกการสืบสวนและแก้ไขข้อผิดพลาดในโมดูล `discount.py` อย่างมีหลักฐานตามกระบวนการ 5 ขั้น: Reproduce -> Traceback -> Hypothesis -> Verify -> Fix & Re-run

---

## จุดที่ 1: `test_apply_discount_basic` (และส่งผลต่อ `test_bulk_total`)

### 1. Reproduce
- **คำสั่งที่รัน:** `python -m pytest tests/test_discount.py -k test_apply_discount_basic -v`
- **Assertion ที่ Fail:**
  ```text
  assert apply_discount(100.0, 10) == 90.0
  E assert 99.9 == 90.0
  E  + where 99.9 = apply_discount(100.0, 10)
  ```

### 2. Traceback
- **ตำแหน่งที่พบข้อผิดพลาด:**
  ```text
  tests\test_discount.py:8: in test_apply_discount_basic
      assert apply_discount(100.0, 10) == 90.0
  discount.py:5: in apply_discount
      return price - percent / 100
  ```

### 3. สมมติฐาน (Hypothesis)
ฟังก์ชัน `apply_discount()` เขียนสูตรคณิตศาสตร์ผิด โดยนำราคาเต็ม (`price`) มาลบกับสัดส่วนเปอร์เซ็นต์โดยตรง (`percent / 100`) โดยไม่ได้นำเปอร์เซ็นต์ไปคูณกับราคาเต็มก่อน ทำให้ส่วนลดที่ถูกหักออกมีค่าเพียง `10 / 100 = 0.1` บาท ไม่ใช่ 10% ของราคา 100 บาท (10 บาท) ผลลัพธ์จึงกลายเป็น `100.0 - 0.1 = 99.9` บาท

> **ข้อสังเกตเรื่องกับดัก (Intentional Trap):**  
> `test_apply_discount_zero` ผ่าน (`PASSED`) ทั้งที่สูตรผิด เพราะเมื่อ `percent = 0` พจน์ `0 / 100 = 0` ทำให้ `price - 0 = price` พอดี จึงเป็น False Positive ที่ผ่านเพราะความบังเอิญ

### 4. การยืนยัน (Verification)
ทำการพิสูจน์ด้วย Python REPL:
```python
price = 100.0
percent = 10
print("สูตรเดิม:", price - percent / 100)           # แสดงผล 99.9 (ผิด)
print("สูตรที่ถูกต้อง:", price - (price * percent / 100)) # แสดงผล 90.0 (ถูกต้อง)
```
เห็นได้ชัดว่าผลลัพธ์จากสูตรที่ถูกต้องตรงกับ Assertion 90.0 บาททุกประการ

### 5. Root cause และการแก้
- **Root Cause:** สูตรคำนวณส่วนลดขาดตัวแปรราคา `price` ในเทอมของการคิดอัตราส่วนลด ทำให้สูตรลดราคาผิดสเกลอย่างสิ้นเชิง
- **การแก้ไข:** แก้ไขบรรทัดที่ 5 ใน `discount.py` เป็น `return price - (price * (percent / 100))` หรือ `return price * (1.0 - percent / 100)`

---

## จุดที่ 2: `test_average_price_empty`

### 1. Reproduce
- **คำสั่งที่รัน:** `python -m pytest tests/test_discount.py -k test_average_price_empty -v`
- **Assertion / Exception ที่ Fail:**
  ```text
  tests\test_discount.py:28: in test_average_price_empty
      assert average_price([]) == 0.0
  discount.py:18: in average_price
      return sum(prices) / len(prices)
  E ZeroDivisionError: division by zero
  ```

### 2. Traceback
- **ตำแหน่งที่พบข้อผิดพลาด:**
  ```text
  discount.py:18: in average_price
  >   return sum(prices) / len(prices)
  E   ZeroDivisionError: division by zero
  ```

### 3. สมมติฐาน (Hypothesis)
ฟังก์ชัน `average_price()` ขาด Guard Clause สำหรับตรวจสอบกรณีที่ส่งรายการสินค้าเป็นลิสต์ว่าง `[]` เข้ามา ทำให้ `len(prices)` มีค่าเท่ากับ `0` และการนำ `sum(prices)` ซึ่งเป็น `0` ไปหารด้วย `0` ทำให้เกิด Exception `ZeroDivisionError` ส่งผลให้ระบบ Crash แทนที่จะคืนค่า `0.0` ตามข้อกำหนด

### 4. การยืนยัน (Verification)
ทดสอบตรวจสอบเงื่อนไขความยาวของลิสต์:
```python
prices = []
print("len:", len(prices)) # len: 0
# ทดสอบเติม guard clause:
result = 0.0 if not prices else sum(prices) / len(prices)
print("result:", result)   # result: 0.0
```
การใส่เงื่อนไขดักจับลิสต์ว่างสามารถป้องกัน `ZeroDivisionError` ได้อย่างสมบูรณ์

### 5. Root cause และการแก้
- **Root Cause:** ขาดการตรวจสอบความยาวของลิสต์ก่อนดำเนินการหาร (Missing input boundary validation for empty collection)
- **การแก้ไข:** เพิ่ม Guard Clause ที่ต้นฟังก์ชัน `average_price()` หาก `not prices` หรือ `len(prices) == 0` ให้คืนค่า `0.0` ทันที

```python
def average_price(prices: list) -> float:
    """คืนราคาเฉลี่ยของรายการสินค้า"""
    if not prices:
        return 0.0
    return sum(prices) / len(prices)
```

---

## จุดที่ 3: `test_cheapest_n`

### 1. Reproduce
- **คำสั่งที่รัน:** `python -m pytest tests/test_discount.py -k test_cheapest_n -v`
- **Assertion ที่ Fail:**
  ```text
  assert cheapest_n([50.0, 10.0, 30.0, 20.0], 2) == [10.0, 20.0]
  E assert [20.0] == [10.0, 20.0]
  E At index 0 diff: 20.0 != 10.0
  E Right contains one more item: 20.0
  E Full diff:
  E   [
  E -     10.0,
  E       20.0,
  E   ]
  ```

### 2. Traceback
- **ตำแหน่งที่พบข้อผิดพลาด:**
  ```text
  tests\test_discount.py:33: in test_cheapest_n
  >   assert cheapest_n([50.0, 10.0, 30.0, 20.0], 2) == [10.0, 20.0]
  discount.py:24: in cheapest_n
  >   return ordered[1:n]
  ```

### 3. สมมติฐาน (Hypothesis)
ฟังก์ชัน `cheapest_n()` เกิดข้อผิดพลาดแบบ Off-by-one Error ในการทำ List Slicing เนื่องจากโค้ดใช้ `ordered[1:n]` ซึ่งไปเริ่มดึงข้อมูลที่ Index `1` (ตำแหน่งที่สอง) ทำให้สมาชิกตัวแรกสุดที่ Index `0` ซึ่งเป็นสินค้าที่ราคาถูกที่สุดจริง ๆ ถูกตัดทิ้งไป และดึงถึงแค่ Index `n-1` สมาชิกจึงขาดหายไป 1 ตัว

### 4. การยืนยัน (Verification)
ทดสอบ Slice ลิสต์ที่เรียงลำดับแล้ว:
```python
prices = [50.0, 10.0, 30.0, 20.0]
ordered = sorted(prices)
print("ordered:", ordered)       # [10.0, 20.0, 30.0, 50.0]
print("ordered[1:2]:", ordered[1:2]) # [20.0]  (ผิด ข้าม 10.0)
print("ordered[:2]:", ordered[:2])   # [10.0, 20.0] (ถูกต้อง)
```
การเปลี่ยนจุดเริ่มต้นของ Slice ให้เป็น Index 0 (`[:n]`) คืนค่าลิสต์ที่ถูกต้องตาม Assertion

### 5. Root cause และการแก้
- **Root Cause:** สับสนเรื่อง 0-based indexing ในภาษา Python ทำให้ระบุ Slice ผิดเป็น `[1:n]` แทนที่จะเป็น `[:n]`
- **การแก้ไข:** แก้ไขบรรทัดที่ 24 ใน `discount.py` ให้เป็น `return ordered[:n]`
