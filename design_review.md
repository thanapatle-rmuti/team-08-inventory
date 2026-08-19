# Design Review: การตรวจ SOLID Principles ด้วยตัวเอง

> **คำแนะนำ:** ตารางนี้สำหรับนักศึกษาตรวจทานโค้ดและ diagram ด้วยตัวเอง (ตามข้อกำหนดขั้นที่ 9 ของ Lab 3)

| หลัก SOLID | ละเมิดหรือไม่ | จุดที่เกี่ยวข้อง (class/method) | อธิบาย/ผลกระทบ | ข้อเสนอปรับปรุง |
| :--- | :--- | :--- | :--- | :--- |
| **S (Single Responsibility Principle)** | ไม่ละเมิด / ละเมิด | `InventoryService`, `Product`, `Notifier` | แยกหน้าที่ชัดเจน `Product` เก็บข้อมูล, `Notifiers` ส่งแจ้งเตือน, `InventoryService` จัดการ transaction | - |
| **O (Open/Closed Principle)** | ไม่ละเมิด / ละเมิด | `NotifierFactory`, `InventoryService` | สามารถเพิ่ม Notifier ช่องทางใหม่ (เช่น LINE, Webhook) ได้โดยสร้าง class ที่ implement Notifier protocol โดยไม่ต้องแก้โค้ดภายใน `InventoryService` | - |
| **L (Liskov Substitution Principle)** | ไม่ละเมิด / ละเมิด | `EmailNotifier`, `SMSNotifier` | ทุก Concrete Notifier สามารถแทนที่ `Notifier` Protocol ได้โดยไม่ทำให้การทำงานผิดพลาด | - |
| **I (Interface Segregation Principle)** | ไม่ละเมิด / ละเมิด | `Notifier` Protocol | มีเฉพาะ method `send()` ที่จำเป็น ไม่บังคับให้ implement method ส่วนเกิน | - |
| **D (Dependency Inversion Principle)** | ไม่ละเมิด / ละเมิด | `InventoryService.__init__` | `InventoryService` ขึ้นกับ `Notifier` Protocol (Abstraction) ไม่ได้ขึ้นกับ `EmailNotifier` หรือ `SMSNotifier` โดยตรง และรับผ่าน Dependency Injection | - |
