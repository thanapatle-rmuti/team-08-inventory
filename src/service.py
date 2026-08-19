"""InventoryService — business logic ของระบบจัดการสต็อก"""

from __future__ import annotations

from typing import Protocol

from models import Product, Category, StockTransaction


# ---------------------------------------------------------------------------
# Notifier Protocol (ใช้ structural subtyping เพื่อไม่ import notifiers โดยตรง)
# ---------------------------------------------------------------------------


class Notifier(Protocol):
    """โปรโตคอลสำหรับช่องทางแจ้งเตือน"""

    def send(self, product: Product, message: str) -> None: ...


# ---------------------------------------------------------------------------
# InventoryService
# ---------------------------------------------------------------------------


class InventoryService:
    """บริการจัดการสต็อกสินค้า — รับ/จ่าย, แจ้งเตือน, รายงาน"""

    def __init__(self, notifiers: list[Notifier] | None = None) -> None:
        """สร้าง InventoryService พร้อมรับ notifier ผ่าน DI"""
        self._products: dict[str, Product] = {}
        self._notifiers: list[Notifier] = notifiers or []
        self._transactions: list[StockTransaction] = []

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
        """บันทึกจ่ายสินค้าออกจากคลัง"""
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

    # -- แจ้งเตือน --

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
