# swe-inventory-67332310017-9

> **คลังโครงงานวิชา Software Engineering / Agile & CI/CD**  
> **รหัสนักศึกษา:** 67332310017-9 (นายธนภัทร)  
> **GitHub Repository:** [https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9](https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9) (Public)  
> **CI Actions Runs:** [https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9/actions](https://github.com/thanapatle-rmuti/swe-inventory-67332310017-9/actions)

---

## สารบัญโครงงานและเอกสารสำคัญ

### เอกสารหลักของโครงงาน
- [PROJECT.md](PROJECT.md) — แดชบอร์ดสรุปงาน 5 หัวข้อหลักสำหรับผู้สอน (Spec, Diagrams, UX, CI Tests, AI Ethics)
- [TEAM_CHARTER.md](TEAM_CHARTER.md) — ข้อตกลงทีมและนโยบาย AI

### งาน Lab 5: TDD, Refactor และ CI/CD
- [test-gap.md](test-gap.md) — ตารางเปรียบเทียบ Test Gap (AI Baseline vs Human Edits)
- [coverage-note.md](coverage-note.md) — บันทึกการวิเคราะห์ Test Coverage (99%)
- [smells.md](smells.md) — รายการ Code Smells 7 ข้อในโมดูลคิดราคาเดิม
- [ethics.md](ethics.md) — รายงานประเด็นจริยธรรม 4 ด้าน และแนวปฏิบัติของตนเอง
- [pricing.py](pricing.py) — โมดูลคิดราคาที่ผ่านการ Refactor อย่างปลอดภัย
- [tests/test_inventory.py](tests/test_inventory.py) — Unit Test ของ Inventory และ TDD ของ `low_stock_items`
- [tests/test_pricing.py](tests/test_pricing.py) — Characterization Test ยืนยันพฤติกรรมเดิม 100%
- [.github/workflows/ci.yml](.github/workflows/ci.yml) — GitHub Actions Workflow (Ruff + Pytest + Coverage >= 85%)
- [screenshots/](screenshots/) — ภาพหน้าจอผลรัน CI ทั้งตอนผ่าน ([ci-green.png](screenshots/ci-green.png)) และไม่ผ่าน ([ci-red.png](screenshots/ci-red.png))

### งาน Lab 4: UX, Code Review และ Debugging
- [lab04-ai-coding-ux/](lab04-ai-coding-ux/) — รายละเอียดงาน Lab 4 ครบชุด
  - [findings-lab04.md](lab04-ai-coding-ux/findings-lab04.md) — สรุปการสัมภาษณ์และ Point of View
  - [persona.md](lab04-ai-coding-ux/persona.md) — Persona และ User Journey Map
  - [code-review.md](lab04-ai-coding-ux/code-review.md) — รีวิวโค้ด `inventory_service.py` 6 เมธอด
  - [debug-log.md](lab04-ai-coding-ux/debug-log.md) — บันทึกการ Debug 5 ขั้นตอน (Pytest ผ่าน 6/6)
