# การเปรียบเทียบ Prompt Engineering vs Context Engineering (Lab 04: ขั้นที่ 7)

เอกสารบันทึกการทดลองสั่งงาน AI เพื่อพัฒนาฟังก์ชันลดสต็อกสินค้า (Sell/Reduce Stock) โดยเปรียบเทียบระหว่างการสั่งคำสั่งสั้น (Zero/Few Context) กับการแนบ Context ครบถ้วน (Context Engineering)

---

## 1. รอบที่ 1: การสั่งงานแบบ Prompt สั้น (Prompt Engineering อย่างเดียว)

### Prompt ที่ใช้สั่ง AI:
```text
เขียน function ลด stock สินค้าในระบบ inventory ในภาษา Python
```

### ผลลัพธ์ (Code Output) ที่ AI สร้าง:
```python
def reduce_stock(stock_dict, item_name, count):
    if item_name in stock_dict:
        stock_dict[item_name] -= count
        print(f"Stock reduced. Remaining: {stock_dict[item_name]}")
        return stock_dict[item_name]
    else:
        print("Item not found")
        return None
```

### ปัญหาและจุดบกพร่องที่พบ:
1. **Interface ไม่ตรงกับโปรเจกต์เดิม:** AI สร้างเป็น standalone function รับ dictionary ธรรมดา แทนที่จะเป็น method ในคลาส `Inventory` หรือทำงานร่วมกับอ็อบเจกต์ `InventoryItem`
2. **ขาด Validation ขอบเขต:** ไม่ตรวจกรณี `count <= 0` และไม่ตรวจกรณีที่ `count > stock` ทำให้สต็อกสามารถติดลบได้ (Negative stock bug)
3. **ใช้ Side-effect (`print`):** แทนที่จะ raise Exception ตามหลัก OOP กลับใช้ `print` และ `return None` ซึ่งทำให้ Caller จัดการ Error ได้ยาก
4. **ไม่มี Type Hints และ Docstring:** ขาดเอกสารกำกับและชนิดตัวแปร

---

## 2. รอบที่ 2: การสั่งงานพร้อมแนบ Context ครบถ้วน (Context Engineering)

### Prompt และ Context ที่แนบให้ AI:
```text
บทบาท: คุณคือ Software Engineer ทำหน้าที่พัฒนา method เพิ่มเติมในระบบ Inventory
งาน: เพิ่มฟังก์ชันขาย/ลดสต็อกสินค้าในคลาส Inventory

[Context 1: โค้ดเดิมของระบบ]
class InventoryItem:
    def __init__(self, name: str, quantity: int, price: float):
        self.name = name
        self.quantity = quantity
        self.price = price

class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}

[Context 2: เกณฑ์ที่ต้องผ่าน (Acceptance Criteria)]
1. ตรวจสอบว่ามีชื่อสินค้านี้ในระบบหรือไม่ หากไม่มีให้ raise KeyError
2. จำนวนที่ขาย/ลด (amount) ต้องเป็นตัวเลขมากกว่าศูนย์ (amount > 0) หากน้อยกว่าหรือเท่ากับ 0 ให้ raise ValueError
3. หากจำนวนที่ขอลดมากกว่าสต็อกคงเหลือที่มีอยู่ ให้ปฏิเสธและ raise ValueError พร้อมระบุข้อความชัดเจนว่าไม่พอ ห้ามให้สต็อกติดลบเด็ดขาด
4. อัปเดตจำนวนคงเหลือและคืนค่า (return) เป็นจำนวนสต็อกคงเหลือใหม่ (int)

[Context 3: ข้อจำกัดทางเทคนิคและสไตล์โค้ด]
- ใช้ Type hints ครบถ้วนตาม Python 3.11+
- มี Docstring ภาษาไทยอธิบายพฤติกรรม
- ห้ามใช้ไลบรารีภายนอก
```

### ผลลัพธ์ (Code Output) ที่ AI สร้าง:
```python
class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}

    def sell(self, name: str, amount: int) -> int:
        """ลดจำนวนสินค้าในคลังเมื่อมีการจำหน่าย

        Args:
            name: ชื่อสินค้าที่ต้องการขาย
            amount: จำนวนที่ต้องการขาย (ต้องมากกว่า 0)

        Returns:
            int: จำนวนสินค้าคงเหลือหลังการขาย

        Raises:
            KeyError: เมื่อไม่พบชื่อสินค้าในคลัง
            ValueError: เมื่อจำนวนที่ขาย <= 0 หรือสินค้าคงเหลือไม่เพียงพอ
        """
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
        
        item = self._items[name]
        if item.quantity < amount:
            raise ValueError(
                f"สินค้า '{name}' คงเหลือ {item.quantity} ชิ้น "
                f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
            )
        
        item.quantity -= amount
        return item.quantity
```

---

## 3. บทสรุปการเปรียบเทียบและวิเคราะห์ปัจจัยที่ทำให้ผลลัพธ์ต่างกัน

| ประเด็น | รอบที่ 1: Prompt สั้น | รอบที่ 2: มี Context ครบ |
| :--- | :--- | :--- |
| **ความเข้ากันได้กับระบบเดิม (Compatibility)** | ❌ ใช้งานร่วมกับโค้ดเดิมไม่ได้ ต้องเขียนกาวเชื่อมใหม่ | ✅ เข้ากับโครงสร้างคลาส `Inventory` และ `InventoryItem` ได้ 100% |
| **การจัดการขอบเขตและข้อผิดพลาด (Robustness)** | ❌ สต็อกติดลบได้, กลืน Error ด้วย print | ✅ มี Guard Clause ตรวจสอบครบทุกกรณีตาม AC และ raise Exception ถูกประเภท |
| **คุณภาพเอกสารและโค้ด (Readability & Style)** | ❌ ไม่มี docstring / type hint | ✅ มี docstring ภาษาไทย และ Type Annotations สมบูรณ์ |

### อะไรทำให้ผลลัพธ์ต่างกัน?
1. **การจำกัดขอบเขตของโมเดล (Grounding):** เมื่อไม่มี Context โมเดล AI จะต้อง "เดา" บริบทเองจากค่าสถิติ ทำให้สร้างฟังก์ชันแบบกว้าง ๆ แต่เมื่อได้รับโค้ดเดิม โมเดลจะล็อกขอบเขตของคลาสและตัวแปรตามสถาปัตยกรรมเดิมทันที
2. **Acceptance Criteria ที่ชัดเจน:** การให้เงื่อนไขเป็น Given-When-Then หรือรายการข้อจำกัด ทำหน้าที่เหมือน "Prompt Contract" ป้องกันไม่ให้ AI สร้างโค้ดที่มี Logic ผิดพลาดหรือละเลย Edge Case
3. **Technical Constraints:** การระบุสไตล์และข้อห้ามอย่างชัดเจนช่วยลดเวลาในการ Refactor โค้ดหลัง AI สร้าง
