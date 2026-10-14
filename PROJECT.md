# PROJECT.md: ระบบสต็อกสินค้า (Inventory Management System)

> **โครงงานรายวิชา Software Engineering / Agile & Database**  
> **รหัสนักศึกษา:** 67332310017-9  
> **GitHub Repository:** [https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9](https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9) (หรือ `team-08-inventory`)

---

## 1. ข้อมูลโครงงานและสมาชิก

| ข้อมูล | รายละเอียด |
| :--- | :--- |
| **ชื่อโครงงาน** | ระบบจัดการสต็อกสินค้า (Inventory Management System) |
| **รหัสนักศึกษา** | 67332310017-9 |
| **GitHub Username** | `thanapatle-rmuti` |
| **ทีม / กลุ่ม** | Team 08 |
| **สถานะ Repository** | Public |

---

## 2. ภาพรวมของระบบ (Project Overview)

ระบบบริหารจัดการสต็อกสินค้าและคลังสินค้า (Inventory Management) พัฒนาด้วยภาษา Python ออกแบบตามหลัก **Spec-Driven Development (SDD)**, **Test-Driven Development (TDD)** และ **SOLID Principles** เพื่อรองรับการทำงานของพนักงานคลังสินค้าและผู้จัดการ:
- บันทึกการรับเข้า (Receive) และจ่ายออก (Issue) สินค้าแบบเรียลไทม์
- ระบบแจ้งเตือนอัตโนมัติเมื่อสต็อกต่ำกว่าเกณฑ์ขั้นต่ำ (Low-stock Alert) ผ่าน Email และ SMS (จำลองผลลัพธ์)
- รองรับประเภทสินค้าที่หลากหลาย ทั้งสินค้าจับต้องได้ (Physical Product) และสินค้าดิจิทัล (Digital Product)
- สรุปรายงานมูลค่าสต็อกรวมและวิเคราะห์ข้อมูลคลังสินค้า

---

## 3. ขอบเขตการทำงาน (User Stories & Acceptance Criteria)

| รหัส | User Story | Acceptance Criteria (สรุป) |
| :--- | :--- | :--- |
| **US-01** | พนักงานต้องการบันทึกการรับ/จ่ายสินค้าพร้อมอัปเดตสต็อกทันที | สต็อกคำนวณถูกต้องตามจำนวนรับ/จ่าย, ปฏิเสธยอดจ่ายเกินคงเหลือ และปฏิเสธจำนวน $\le 0$ |
| **US-02** | ผู้จัดการต้องการรับการแจ้งเตือนทันทีเมื่อสินค้าต่ำกว่า threshold | ส่งแจ้งเตือนเมื่อ `quantity < threshold`, หากเท่ากับหรือมากกว่าจะไม่ส่งแจ้งเตือน |
| **US-03** | ผู้จัดการต้องการดูมูลค่ารวมของสต็อกแยกตามหมวดหมู่ | คำนวณผลรวมมูลค่าสต็อก (Quantity $\times$ Unit Price) ได้ถูกต้อง |
| **US-04** | ผู้จัดการต้องการตั้งค่า threshold รายสินค้า | กำหนดจุดสั่งซื้อซ้ำได้ ปฏิเสธค่าลบ |
| **US-05** | ผู้จัดการต้องการเลือกช่องทางแจ้งเตือน (Email / SMS) | เลือกลงทะเบียนหรือถอดถอน Notifier ได้แบบ Dynamic |

---

## 4. สถาปัตยกรรมและเทคโนโลยีที่ใช้ (Architecture & Design)

- **ภาษาที่ใช้:** Python 3.11+
- **การออกแบบเชิงสถาปัตยกรรม (Design Patterns & SOLID):**
  - **Factory Pattern:** `NotifierFactory` สำหรับรวมศูนย์การสร้างอ็อบเจกต์ Notifier ตามประเภท (Email, SMS)
  - **Observer Pattern:** `InventoryService` ทำหน้าที่เป็น Subject และ `Notifier` เป็น Observer แจ้งเตือนแบบ Publish-Subscribe
  - **SOLID Principles:** SRP, OCP, LSP, ISP, DIP ครบถ้วน ไม่ผูกติดกับ Concrete I/O
- **Quality Assurance & CI Pipeline:**
  - Automated Testing ด้วย `pytest` ครอบคลุม Unit Tests, Edge Cases และ Regression Tests
  - Linting & Code Formatting ด้วย `ruff` ผ่าน GitHub Actions Workflow (`ci.yml`)

---

## 5. โครงสร้างไฟล์ใน Repository

```text
├── .ai-rules.md              # กฎและ Context คุมคุณภาพ AI
├── .github/workflows/ci.yml  # Automated CI Pipeline (Ruff + Pytest)
├── AI_ITERATION_LOG.md       # บันทึกการปรับปรุงรอบ Iteration (SDD)
├── PROJECT.md                # รายละเอียดโครงงาน (ไฟล์นี้)
├── TEAM_CHARTER.md           # ข้อตกลงทีมและบทบาทการทำงาน
├── coverage-note.md          # บันทึก Test Coverage
├── design_review.md          # รายงานการตรวจสอบหลักการออกแบบ SOLID
├── ethics.md                 # รายงานประเด็นจริยธรรมในการพัฒนา AI
├── diagrams/                 # Class Diagram และ Sequence Diagram
├── specs/spec.md             # Functional Specification & Gherkin Scenarios
├── src/                      # Source Code (models, notifiers, service, main)
└── tests/                    # Automated Unit Tests
```

---

## 6. การติดตั้งและทดสอบ (Getting Started)

### ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### การรัน Automated Test
```bash
pytest -v
```

### การรันระบบ
```bash
python -m src.main
```
