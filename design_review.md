# Design Review: การตรวจ SOLID Principles

> เอกสารการวิเคราะห์และตรวจสอบการปฏิบัติตามหลักการออกแบบ SOLID (Lab 3: ขั้นที่ 9 และ 10)

---

## ตารางประเมินหลักการ SOLID (5 ข้อ)

| หลัก SOLID | สถานะ | จุดที่เกี่ยวข้อง (Class / Method) | คำอธิบายเชิงสถาปัตยกรรมและผลกระทบ | การออกแบบที่ใช้แก้ไข / ป้องกัน |
| :--- | :---: | :--- | :--- | :--- |
| **S - Single Responsibility Principle (SRP)** | ✅ ไม่ละเมิด | `Product`, `InventoryService`, `EmailNotifier`, `SMSNotifier`, `NotifierFactory` | แต่ละ Class มีหน้าที่และความรับผิดชอบเพียงเรื่องเดียว:<br>• `Product`: จัดการสถานะและข้อมูลสินค้า<br>• `InventoryService`: จัดการ Business Transaction (รับ/จ่าย/รายงาน)<br>• `Notifier`: รับผิดชอบเรื่องการสื่อสารแจ้งเตือนเท่านั้น<br>• `NotifierFactory`: จัดการการสร้าง Object Notifier | แยก I/O (print/notification) ออกจาก Business Logic ของคลังสินค้า ไม่ปะปนกันใน Method เดียว |
| **O - Open/Closed Principle (OCP)** | ✅ ไม่ละเมิด | `InventoryService`, `Notifier` (Protocol), `NotifierFactory` | ระบบเปิดให้ขยายช่องทางแจ้งเตือนใหม่ (เช่น `LineNotifier`, `WebhookNotifier`) ได้ทันทีโดยสร้าง Class ใหม่ที่ Implement `Notifier` Protocol โดยไม่ต้องแก้ไข Code ภายใน `InventoryService` | ใช้ **Observer Pattern** และ **Factory Pattern** ทำให้ `InventoryService` ไม่ขึ้นกับจำนวนหรือประเภทของ Notifier |
| **L - Liskov Substitution Principle (LSP)** | ✅ ไม่ละเมิด | `EmailNotifier`, `SMSNotifier` $\rightarrow$ `Notifier` | ทั้ง `EmailNotifier` และ `SMSNotifier` สามารถทำงานทดแทน `Notifier` Protocol ได้สมบูรณ์ตาม Contract (`send(product, message)`) โดยไม่เกิด Side Effect หรือ Error ที่ไม่คาดคิด | การกำหนด Protocol Signature ให้ชัดเจนและสม่ำเสมอในทุก Notifier |
| **I - Interface Segregation Principle (ISP)** | ✅ ไม่ละเมิด | `Notifier` Protocol | `Notifier` Protocol มีเฉพาะ Method `send()` ซึ่งจำเป็นต่อการแจ้งเตือนเท่านั้น ไม่มีการบังคับให้ Implement Method ส่วนเกินที่ Notifier บางตัวไม่ได้ใช้ | ออกแบบ Interface ให้กระชับ (Thin Interface) ตรงตามวัตถุประสงค์การใช้งาน |
| **D - Dependency Inversion Principle (DIP)** | ✅ ไม่ละเมิด | `InventoryService.__init__`, `register_notifier()` | High-level module (`InventoryService`) ขึ้นตรงกับ Abstraction (`Notifier` Protocol) ไม่ได้ขึ้นตรงกับ Low-level modules (`EmailNotifier`, `SMSNotifier`) โดยตรง | ใช้ **Dependency Injection (DI)** ส่ง Notifier เข้ามาผ่าน Constructor หรือลงทะเบียนผ่าน `register_notifier()` |

---

## สรุปจุดปรับปรุงสถาปัตยกรรม (Design Improvements)

1. **Factory Pattern (`NotifierFactory`):**
   - รวมศูนย์การสร้าง Object ของ Notifier ไว้ที่เดียว ช่วยให้ Application Layer เรียกสร้าง Notifier ผ่านชื่อช่องทางได้อย่างยืดหยุ่น

2. **Observer Pattern (`InventoryService` as Subject, `Notifier` as Observer):**
   - `InventoryService` ทำหน้าที่เป็น Subject คอยเก็บรายชื่อ Observers (`_notifiers`)
   - รองรับการ `register_notifier()` และ `unregister_notifier()` แบบ Dynamic
   - เมื่อเกิดเหตุการณ์สต็อกต่ำกว่า Threshold จะ Broadcast แจ้งเตือนไปยังทุก Observer ที่ลงทะเบียนไว้พร้อมกันโดยอัตโนมัติ
