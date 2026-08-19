"""โมเดลข้อมูลสำหรับระบบจัดการสต็อกสินค้า"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Category(Enum):
    """หมวดหมู่สินค้าในร้านอุปกรณ์วิศวกรรม"""

    ELECTRICAL = "Electrical"
    TOOLS = "Tools"
    SAFETY = "Safety"
    PLUMBING = "Plumbing"


@dataclass
class Product:
    """ข้อมูลสินค้าในคลัง"""

    name: str
    category: Category
    price_per_unit: float
    quantity: int = 0
    threshold: int = 10

    def set_threshold(self, value: int) -> None:
        """ตั้งค่า threshold สำหรับแจ้งเตือนสต็อกต่ำ"""
        if value < 0:
            raise ValueError("threshold ต้องไม่ต่ำกว่า 0")
        self.threshold = value

    @property
    def stock_value(self) -> float:
        """คำนวณมูลค่าสต็อกของสินค้านี้ (จำนวน × ราคาต่อหน่วย)"""
        return self.quantity * self.price_per_unit

    def is_below_threshold(self) -> bool:
        """ตรวจว่าสต็อกต่ำกว่า threshold หรือไม่ (strictly less than)"""
        return self.quantity < self.threshold


@dataclass
class StockTransaction:
    """บันทึกรายการรับ/จ่ายสินค้า"""

    product_name: str
    transaction_type: str  # "receive" หรือ "issue"
    quantity: int
    resulting_stock: int
