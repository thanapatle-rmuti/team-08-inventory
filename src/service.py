"""InventoryService — business logic ของระบบจัดการสต็อก พร้อม Observer Pattern"""

from __future__ import annotations

from typing import Protocol

from models import Category, DigitalProduct, OrderResult, Product, StockTransaction

# ---------------------------------------------------------------------------
# Notifier Protocol (Observer Interface)
# ---------------------------------------------------------------------------


class Notifier(Protocol):
    """โปรโตคอลสำหรับช่องทางแจ้งเตือน (Observer)"""

    def send(self, product: Product, message: str) -> None:
        """ส่งข้อความแจ้งเตือน"""
        ...


# ---------------------------------------------------------------------------
# InventoryService (Subject / Business Logic)
# ---------------------------------------------------------------------------


class InventoryService:
    """บริการจัดการสต็อกสินค้า — รับ/จ่าย, แจ้งเตือน (Subject), รายงาน"""

    def __init__(self, notifiers: list[Notifier] | None = None) -> None:
        """สร้าง InventoryService พร้อมรับ notifier ผ่าน Dependency Injection"""
        self._products: dict[str, Product] = {}
        self._notifiers: list[Notifier] = list(notifiers) if notifiers else []
        self._transactions: list[StockTransaction] = []

    # -- Observer Pattern Management (Subject methods) --

    def register_notifier(self, notifier: Notifier) -> None:
        """ลงทะเบียน Notifier (Observer) เข้าระบบ"""
        if notifier not in self._notifiers:
            self._notifiers.append(notifier)

    def unregister_notifier(self, notifier: Notifier) -> None:
        """ยกเลิกการลงทะเบียน Notifier (Observer)"""
        if notifier in self._notifiers:
            self._notifiers.remove(notifier)

    # -- จัดการสินค้า --

    def add_product(self, product: Product) -> None:
        """เพิ่มสินค้าเข้าระบบ"""
        self._products[product.name] = product

    def get_product(self, name: str) -> Product:
        """ดึงข้อมูลสินค้าตามชื่อ"""
        if name not in self._products:
            raise KeyError(f"ไม่พบสินค้า: {name}")
        return self._products[name]

    # -- รับ/จ่ายสินค้า --

    def receive(self, product_name: str, quantity: int) -> None:
        """บันทึกรับสินค้าเข้าคลัง"""
        if quantity <= 0:
            raise ValueError("จำนวนต้องมากกว่า 0")
        product = self.get_product(product_name)
        product.quantity += quantity
        self._transactions.append(
            StockTransaction(product_name, "receive", quantity, product.quantity)
        )

    def issue(self, product_name: str, quantity: int) -> None:
        """บันทึกจ่ายสินค้าออกจากคลัง และแจ้งเตือน Observer หากสต็อกต่ำ"""
        if quantity <= 0:
            raise ValueError("จำนวนต้องมากกว่า 0")
        product = self.get_product(product_name)
        if product.quantity < quantity:
            raise ValueError("สต็อกไม่เพียงพอ")
        product.quantity -= quantity
        self._transactions.append(
            StockTransaction(product_name, "issue", quantity, product.quantity)
        )
        # ตรวจสอบ threshold หลังจ่าย
        if product.is_below_threshold():
            self._notify_low_stock(product)

    def sell(
        self, product_name: str, quantity: int, confirmed: bool = True
    ) -> OrderResult:
        """ขายสินค้าตามกฎของแต่ละชนิดสินค้า (Physical vs Digital)"""
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise TypeError("จำนวนต้องเป็นตัวเลขจำนวนเต็ม (int)")
        if quantity <= 0:
            raise ValueError("จำนวนต้องมากกว่า 0")

        product = self.get_product(product_name)

        if isinstance(product, DigitalProduct):
            # สินค้าดิจิทัล: ขายแล้วยอดคงเหลือไม่ลด
            return OrderResult(
                product_name=product.name,
                quantity=quantity,
                confirmed=confirmed,
                download_url=product.download_url,
            )

        # สินค้าจับต้องได้: ตรวจสอบสต็อก ตัดสต็อก และแจ้งเตือน threshold
        if product.quantity < quantity:
            raise ValueError("สต็อกไม่เพียงพอ")
        product.quantity -= quantity
        self._transactions.append(
            StockTransaction(product_name, "issue", quantity, product.quantity)
        )
        if product.is_below_threshold():
            self._notify_low_stock(product)

        return OrderResult(
            product_name=product.name,
            quantity=quantity,
            confirmed=confirmed,
            download_url=None,
        )

    # -- แจ้งเตือน Observer (Broadcast) --

    def _notify_low_stock(self, product: Product) -> None:
        """แจ้งเตือน observer ทุกตัวเมื่อสต็อกต่ำกว่า threshold"""
        message = (
            f"สต็อกต่ำ: {product.name} เหลือ {product.quantity} "
            f"(threshold = {product.threshold})"
        )
        for notifier in self._notifiers:
            notifier.send(product, message)

    # -- รายงาน --

    def stock_value_report(self) -> dict[str, float]:
        """สร้างรายงานมูลค่าสต็อกแยกตามหมวดหมู่"""
        report: dict[str, float] = {}
        for product in self._products.values():
            cat_name = (
                product.category.value
                if isinstance(product.category, Category)
                else str(product.category)
            )
            report[cat_name] = report.get(cat_name, 0) + product.stock_value
        return report


    def low_stock_items(self, threshold: int) -> list[str]:
        """คืนรายชื่อสินค้าที่มีของเหลือน้อยกว่าหรือเท่ากับ threshold โดยเรียงตามชื่อ"""
        # จงใจแก้เงื่อนไขให้ผิด (จาก <= เป็น <) เพื่อทดสอบ CI ให้ขึ้นสีแดงตามขั้นตอนที่ 11
        matched = [
            product.name
            for product in self._products.values()
            if product.quantity < threshold
        ]
        return sorted(matched)


# Alias for compatibility with Lab 5
Inventory = InventoryService
