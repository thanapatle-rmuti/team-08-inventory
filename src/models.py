"""โมเดลข้อมูลสำหรับระบบจัดการสต็อกสินค้า"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class PhysicalProduct(Product):
    """สินค้าจับต้องได้: การขายจะตัดสต็อก และต้องปฏิเสธหากสั่งซื้อเกินสต็อก"""

    pass


@dataclass
class DigitalProduct(Product):
    """สินค้าดิจิทัล: การขายไม่ลดสต็อก และมีลิงก์สำหรับดาวน์โหลด"""

    download_url: str = ""


@dataclass
class OrderResult:
    """ผลลัพธ์คำสั่งซื้อสินค้า"""

    product_name: str
    quantity: int
    confirmed: bool = False
    download_url: str | None = None

    def get_download_link(self) -> str:
        """ขอรับลิงก์ดาวน์โหลด (เฉพาะสินค้าดิจิทัลและคำสั่งซื้อยืนยันแล้วเท่านั้น)"""
        if not self.confirmed:
            raise PermissionError("เปิดลิงก์ดาวน์โหลดไม่ได้ถ้าคำสั่งซื้อยังไม่ยืนยัน")
        if not self.download_url:
            raise ValueError("สินค้านี้ไม่มีลิงก์ดาวน์โหลด")
        return self.download_url
