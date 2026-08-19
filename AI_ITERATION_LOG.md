# AI Iteration & Context Engineering Log

บันทึกการทำงานและการทดลองตามกระบวนการ Spec-Driven Development (SDD) และ Context Engineering (Lab 3)

---

## 1. ตารางเปรียบเทียบผลลัพธ์: ก่อนมี Context vs หลังมี Context

| ประเด็น | ก่อนมี context (ขั้นที่ 4: `inventory_no_context.py`) | หลังมี context (ขั้นที่ 6: `models.py`, `notifiers.py`, `service.py`) |
| :--- | :--- | :--- |
| **การแยกไฟล์ / ความรับผิดชอบ** | รวมทุกอย่างไว้ในไฟล์เดียว (`inventory_no_context.py`) ทั้ง model, notification, logic, reporting | แยกไฟล์ตามหน้าที่อย่างชัดเจน: `models.py` (Data Model), `notifiers.py` (Notification logic), `service.py` (Business Logic) |
| **Type Hints & Docstring** | ไม่มี Type hint ใน signature และไม่มี docstring อธิบายเมธอด | มี Type hint ครบถ้วนทุกฟังก์ชันตาม Python 3.11+ และมี docstring ภาษาไทยกำกับทุก public method |
| **Service ผูกกับ Notifier ตรง ๆ หรือไม่** | ผูกตรงและ import `smtplib` มาส่งจริงใน method `issue()` (ละเมิด DIP และ SRP) | ไม่ผูกกับ concrete class โดยตรง แต่ใช้ `Notifier` Protocol และรับผ่าน Constructor (Dependency Injection) |
| **Hardcode Config หรือไม่** | Hardcode อีเมล `admin@shop.com`, `manager@shop.com`, เบอร์โทร `0812345678` ใน business logic | ไม่ hardcode ใน service โดย config ถูกส่งผ่าน Factory/Constructor จากภายนอก |
| **การส่ง Email/SMS จริง** | เรียก `smtplib.SMTP` พยายามเชื่อมต่อเซิร์ฟเวอร์จริง (เสี่ยง error/fail) | ใช้การจำลองผลลัพธ์ผ่าน `print("[EMAIL] ...")` และ `print("[SMS] ...")` ตามกฎ |

---

## 2. บันทึกการปรับปรุงรอบ Iteration (อย่างน้อย 2 รอบ)

### รอบที่ 1: เงื่อนไขแจ้งเตือนสต็อกต่ำ และการส่ง Email จริง
- **ผลลัพธ์ที่ผิดปกติ:** โค้ดจาก AI ก่อนหน้านี้ใช้เงื่อนไข `<= threshold` (ทำให้สต็อกเท่ากับ threshold ก็ส่งแจ้งเตือน) และมีการพยายาม import `smtplib` เพื่อส่งอีเมลจริง
- **สาเหตุอยู่ที่:**
  1. `spec.md` เดิมไม่ได้ระบุชัดเจนว่า "สต็อกเท่ากับ threshold" ต้องทำอย่างไร
  2. ยังไม่มี `.ai-rules.md` ห้ามการเชื่อมต่อ I/O ส่งเมลจริง
- **การแก้ไขที่ต้นทาง (Spec & Context):**
  1. เพิ่ม Acceptance Criteria ใน `spec.md`: Scenario "สต็อกเท่ากับ threshold พอดี" ระบุชัดเจนว่าต้องไม่แจ้งเตือน (strictly less than `<`)
  2. กำหนดใน `.ai-rules.md` ห้ามส่ง email/sms จริง ให้ใช้ `print` จำลองเท่านั้น
- **ผลลัพธ์หลังแก้ไข:** AI สร้างโค้ดที่ใช้ `quantity < threshold` และจำลองแจ้งเตือนผ่าน print ถูกต้อง 100%

---

### รอบที่ 2: การจัดการค่าตัวเลขติดลบและจำนวน 0 (Input Validation)
- **ผลลัพธ์ที่ผิดปกติ:** ฟังก์ชันรับ/จ่ายสินค้า และการตั้งค่า threshold ยอมรับค่าติดลบหรือ 0 ทำให้สต็อกและ threshold ติดลบได้
- **สาเหตุอยู่ที่:** `spec.md` เดิมยังขาด Acceptance Criteria สำหรับ Edge Case เช่น จำนวนรับ/จ่ายเป็น 0 หรือตั้ง threshold ค่าลบ
- **การแก้ไขที่ต้นทาง (Spec):**
  1. เพิ่ม Scenario ใน US-01: "บันทึกจำนวนเป็น 0 หรือค่าลบ" ต้องปฏิเสธและ raise ValueError
  2. เพิ่ม Scenario ใน US-04: "ตั้ง threshold เป็นค่าลบ" ต้องปฏิเสธ
- **ผลลัพธ์หลังแก้ไข:** `Product.set_threshold()` และ `InventoryService.receive()/issue()` มีการตรวจสอบความถูกต้องและแจ้งเตือนข้อผิดพลาดตาม spec

---

## 3. รายละเอียด Prompt และช่องทาง AI ที่ใช้งาน

- **AI Model / Tool ที่ใช้:** Google Antigravity / Gemini & Claude
- **Prompts ที่ใช้:**
  1. *Prompt Step 3 (Review Spec):* "ฉันกำลังทำ Spec-Driven Development ช่วยรีวิว spec ด้านล่างนี้ในฐานะ senior software engineer ตอบเป็นภาษาไทย..."
  2. *Prompt Step 4 (No Context):* "จาก spec นี้ ช่วยเขียนโค้ด Python สำหรับฟีเจอร์แจ้งเตือนสต็อกต่ำ [spec.md]"
  3. *Prompt Step 6 (With Context):* "คุณคือ AI coding agent ของโปรเจกต์นี้ ทำตามกฎใน .ai-rules.md อย่างเคร่งครัด implement ฟีเจอร์ตาม spec ด้านล่าง โดยแยกไฟล์ตามที่กฎกำหนด..."
