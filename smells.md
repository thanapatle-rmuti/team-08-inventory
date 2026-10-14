# รายการข้อบกพร่องของโค้ดเดิม (Code Smells in `pricing_legacy.py`) - Lab 5 (ขั้นที่ 6)

เอกสารบันทึกจุดที่อ่านยากและข้อบกพร่องเชิงสถาปัตยกรรมในไฟล์ `pricing_legacy.py` อย่างน้อย 5 ข้อ พร้อมระบุตำแหน่งบรรทัดและผลกระทบ

---

## ตารางสรุป Code Smells ที่ตรวจพบ (7 ข้อ)

| # | ตำแหน่งบรรทัด | ชนิดของ Code Smell | รายละเอียดปัญหาและผลกระทบ | แนวทาง Refactor |
| :-: | :--- | :--- | :--- | :--- |
| **1** | บรรทัดที่ 8, 9, 36, 55 | **Global Mutable State (Side Effect)** | มีการใช้ตัวแปรส่วนกลาง `member_points = {}` และ `LOG = []` ในระดับ Module ทำให้เกิด State Leak ข้ามการเรียกฟังก์ชัน ส่งผลให้ Unit Test ปนเปื้อนข้อมูลกัน และไม่รองรับ Concurrency | แปลงเป็น Class หรือส่ง State เข้ามาผ่าน Dependency Injection |
| **2** | บรรทัดที่ 17, 18, 22 | **Cryptic Variable Names (ชื่อตัวแปรสั้นเกินไป)** | ใช้ตัวแปรตัวอักษรเดี่ยว เช่น `t` (Total), `i` (Item tuple), `sub` (Subtotal) ซึ่งยากต่อการทำความเข้าใจบริบท | เปลี่ยนเป็นชื่อที่สื่อความหมาย เช่น `total_amount`, `item`, `subtotal` |
| **3** | บรรทัดที่ 20, 22 | **Primitive Obsession / Unnamed Tuple Indexing** | รับ `items` เป็นลิสต์ของ Tuple แล้วเข้าถึงด้วยตัวเลข Index `i[1]` (จำนวน) และ `i[2]` (ราคา) เสี่ยงต่อการสลับตำแหน่งข้อมูลและอ่านยาก | ใช้ NamedTuple, Dataclass หรือ Object `OrderItem` |
| **4** | บรรทัดที่ 24, 26, 34, 40, 48 | **Magic Numbers (ตัวเลขไร้ความหมาย)** | มีตัวเลขลอย ๆ ในโค้ด เช่น `0.9` (ลด 10%), `0.95` (ลด 5%), `100`, `50` โดยไม่มีค่าคงที่กำกับว่าคือกติกาโปรโมชันใด | ประกาศเป็นค่าคงที่ (Constants) เช่น `BULK_DISCOUNT_TIER_1 = 0.9` |
| **5** | บรรทัดที่ 12 - 57 | **God Function / Violation of SRP (ทำหน้าที่มากเกินไป)** | ฟังก์ชัน `calc()` ทำงานทุกอย่างในฟังก์ชันเดียว: คำนวณราคา, ลดขั้นบันได, จัดการแต้มสมาชิก, ตัดคูปอง, คิด VAT, บันทึก Log | แยกเป็นฟังก์ชันย่อยตามหน้าที่ (Single Responsibility Principle) |
| **6** | บรรทัดที่ 46 | **Hardcoded System Time Dependency** | เรียก `datetime.date.today()` โดยตรง ทำให้โค้ดขึ้นกับเวลาจริงของเครื่องจักร ไม่สามารถทำ Deterministic Test ได้ง่าย | ส่ง `today` ผ่านพารามิเตอร์ หรือใช้ Clock Abstraction |
| **7** | บรรทัดที่ 30, 38, 45 | **PEP 8 Violation (`!= None`)** | เปรียบเทียบกับ `None` ด้วยตัวดำเนินการ `!= None` และ `== None` แทนที่จะใช้ `is not None` และ `is None` | ปรับใช้ `if member is not None:` ตามมาตรฐานภาษา Python |
