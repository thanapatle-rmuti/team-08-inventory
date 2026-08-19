"""ระบบจัดการสต็อกสินค้า - implement จาก spec โดยไม่มี context/rules"""


class InventorySystem:
    def __init__(self):
        self.products = {}

    def add_product(self, name, category, quantity, price, threshold=10):
        self.products[name] = {
            "category": category,
            "quantity": quantity,
            "price": price,
            "threshold": threshold,
        }

    def receive(self, name, qty):
        self.products[name]["quantity"] += qty
        print(f"รับเข้า {name} จำนวน {qty}")

    def issue(self, name, qty):
        product = self.products[name]
        if product["quantity"] < qty:
            print("สต็อกไม่เพียงพอ")
            return False
        product["quantity"] -= qty
        # ตรวจ threshold
        if product["quantity"] <= product["threshold"]:
            # ส่งแจ้งเตือน email
            import smtplib
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.sendmail("admin@shop.com", "manager@shop.com",
                            f"แจ้งเตือน: {name} สต็อกต่ำ เหลือ {product['quantity']}")
            # ส่งแจ้งเตือน sms
            print(f"SMS ไปที่ 0812345678: {name} สต็อกเหลือ {product['quantity']}")
        return True

    def set_threshold(self, name, value):
        self.products[name]["threshold"] = value

    def report(self):
        result = {}
        for name, info in self.products.items():
            cat = info["category"]
            val = info["quantity"] * info["price"]
            if cat in result:
                result[cat] += val
            else:
                result[cat] = val
        total = 0
        for cat, val in result.items():
            print(f"{cat}: {val} บาท")
            total += val
        print(f"รวมทั้งหมด: {total} บาท")
        return result


if __name__ == "__main__":
    inv = InventorySystem()
    inv.add_product("สายไฟ 2.5 sq.mm", "Electrical", 20, 50, 15)
    inv.add_product("คีมตัด", "Tools", 10, 300, 5)

    inv.receive("สายไฟ 2.5 sq.mm", 30)
    inv.issue("สายไฟ 2.5 sq.mm", 8)
    inv.report()
