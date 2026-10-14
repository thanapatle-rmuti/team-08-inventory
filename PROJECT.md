# PROJECT.md: ระบบสต็อกสินค้า (Inventory & Pricing System)

> **โครงงานรายวิชา Software Engineering / Agile & CI/CD**  
> **รหัสนักศึกษา:** 67332310017-9 (นายธนภัทร)  
> **GitHub Repository:** [https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9](https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9) (Public)  
> **CI Actions URL:** [https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9/actions](https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9/actions)

---

## 1. จุดตรวจงาน 5 หัวข้อหลักสำหรับผู้สอน (Grading Navigation)

| # | หัวข้อประเมิน | เอกสารและลิงก์ไปยังไฟล์ใน Repository |
| :-: | :--- | :--- |
| **1** | **Spec ของระบบ** | • [specs/spec.md](specs/spec.md) — Functional Specification และ Acceptance Criteria (Given-When-Then) |
| **2** | **Class Diagram & Sequence Diagram** | • [diagrams/class.md](diagrams/class.md) — แผนภาพ Class Diagram (Factory & Observer Pattern)<br>• [diagrams/sequence.md](diagrams/sequence.md) — แผนภาพ Sequence Diagram การรับ/จ่าย/แจ้งเตือน |
| **3** | **งานฝั่งผู้ใช้ (UX/UI)** | • [lab04-ai-coding-ux/persona.md](lab04-ai-coding-ux/persona.md) — Persona "สมศรี" และ User Journey Map<br>• [lab04-ai-coding-ux/assets/wireframe-ai.md](lab04-ai-coding-ux/assets/wireframe-ai.md) — Text Wireframe 3 หน้าจอ<br>• [lab04-ai-coding-ux/accessibility-review.md](lab04-ai-coding-ux/accessibility-review.md) — แบบตรวจ Accessibility (WCAG 2.1 AA) |
| **4** | **Test อัตโนมัติ และผลการรัน CI** | • [tests/test_inventory.py](tests/test_inventory.py) — Unit Test ของ Inventory และ TDD ของ `low_stock_items`<br>• [tests/test_pricing.py](tests/test_pricing.py) — Characterization Test ของโมดูลคิดราคา<br>• [.github/workflows/ci.yml](.github/workflows/ci.yml) — GitHub Actions CI Workflow (Ruff + Pytest + Coverage >= 85%)<br>• [screenshots/ci-green.png](screenshots/ci-green.png) — ภาพ Check ผ่าน (สีเขียว)<br>• [screenshots/ci-red.png](screenshots/ci-red.png) — ภาพ Check ไม่ผ่าน (สีแดง) |
| **5** | **บันทึกการใช้ AI และจริยธรรม** | • [test-gap.md](test-gap.md) — ตาราง 3 คอลัมน์วิเคราะห์ Test Gap ที่ AI ขาดไป<br>• [coverage-note.md](coverage-note.md) — รายงานวิเคราะห์ Code Coverage 3 คำถาม<br>• [smells.md](smells.md) — รายการ Code Smells 7 ข้อในโค้ดเดิม<br>• [ethics.md](ethics.md) — รายงานจริยธรรมยุค AI 4 ประเด็น + Personal Policy 190 คำ<br>• [AI_ITERATION_LOG.md](AI_ITERATION_LOG.md) — บันทึก Context Engineering & SDD Iterations |

---

## 2. ภาพรวมระบบและการปรับปรุง (Lab 5 Summary)

### 2.1 TDD Safety Net (`low_stock_items`)
- เขียน Test สีแดงล่วงหน้า 6 กรณีครอบคลุมทุก Boundary Condition (สินค้าหมด, เท่ากับ threshold พอดี, เรียงชื่อ ก-ฮ, ค่าลบ, คลังว่าง)
- พัฒนาโค้ดให้ผ่าน (Green) และ Refactor โค้ดให้อ่านง่าย กระชับ ด้วย Sorted List Comprehension

### 2.2 Refactoring Legacy Code (`pricing_legacy.py` -> `pricing.py`)
- บันทึกพฤติกรรมเดิมด้วย Characterization Tests 11 ข้อ ใน `tests/test_pricing_legacy.py`
- แยกความรับผิดชอบย่อยตามหลัก SRP (คำนวณราคาสินค้า, ลดซื้อเหมา, จัดการคะแนนสมาชิก, คูปองโปรโมชัน, ภาษีมูลค่าเพิ่ม)
- ปราศจาก Magic Numbers และขจัด Global Mutable State

### 2.3 Automated CI/CD Workflow
- ควบคุมคุณภาพโค้ดด้วย `ruff` linter และ `pytest` พร้อมตั้งเกณฑ์ Code Coverage ขั้นต่ำ 85% (`--cov-fail-under=85`)
- ผลการวัด Coverage ปัจจุบันอยู่ที่ **99%**

---

## 3. คำสั่งสำหรับการติดตั้งและทดสอบ (Commands)

```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# ตรวจสอบรูปแบบโค้ดด้วย ruff
ruff check .

# รัน Automated Test พร้อมวัด Coverage
pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=85
```
