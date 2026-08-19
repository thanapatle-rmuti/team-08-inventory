# Sequence Diagram

แผนภาพ Sequence Diagram แสดงลำดับการทำงานเมื่อพนักงานบันทึกจ่ายสินค้าจนสต็อกต่ำกว่า threshold

```mermaid
sequenceDiagram
    autonumber
    actor Staff as พนักงานคลังสินค้า
    participant Service as InventoryService
    participant Product as Product
    participant Trans as StockTransaction
    participant Notifier as Notifier (Email/SMS)

    Staff->>Service: issue("สายไฟ 2.5 sq.mm", 8)
    activate Service

    Service->>Service: get_product("สายไฟ 2.5 sq.mm")
    Service->>Product: quantity (ตรวจสต็อกว่าพอจ่ายหรือไม่)
    Product-->>Service: คืนค่า 20

    Note over Service,Product: 20 >= 8 (สต็อกเพียงพอ ทำการจ่ายออก)

    Service->>Product: ลดจำนวน quantity -= 8
    Product-->>Service: quantity ปัจจุบัน = 12

    Service->>Trans: บันทึกประวัติ (StockTransaction)

    Service->>Product: is_below_threshold()
    Product-->>Service: คืนค่า True (12 < 15)

    opt สต็อกต่ำกว่า threshold (is_below_threshold == True)
        Service->>Service: _notify_low_stock(product)
        loop แจ้งเตือนทุก Notifier ที่ลงทะเบียนไว้
            Service->>Notifier: send(product, message)
            activate Notifier
            Note over Notifier: print("[EMAIL]/[SMS] สต็อกต่ำ...")
            Notifier-->>Service: ส่งเสร็จสิ้น
            deactivate Notifier
        end
    end

    Service-->>Staff: ทำการจ่ายสำเร็จ (สต็อกคงเหลือ 12)
    deactivate Service
```
