"""Tests for Two Product Types (Physical & Digital) - Lab 5 Step 3.

ชนิดสินค้า | สัญญาที่ test ต้องจับ
จับต้องได้ | สั่งซื้อเกินยอดคงเหลือต้องถูกปฏิเสธ และเมื่อขายสำเร็จยอดคงเหลือต้องลดลงตามจำนวนที่ขาย
ดิจิทัล    | ขายแล้วยอดคงเหลือไม่ลด และเปิดลิงก์ดาวน์โหลดไม่ได้ถ้าคำสั่งซื้อยังไม่ยืนยัน
"""

import pytest

from models import Category, DigitalProduct, PhysicalProduct
from service import Inventory

# ---------------------------------------------------------------------------
# กฎของสินค้าจับต้องได้ (Physical Product)
# ---------------------------------------------------------------------------


def test_physical_product_sell_exceeds_stock_rejected():
    """สินค้าจับต้องได้: สั่งซื้อเกินยอดคงเหลือต้องถูกปฏิเสธ และยอดคงเหลือไม่เปลี่ยน"""
    inv = Inventory()
    book = PhysicalProduct(
        name="คู่มือวิศวกรรมไฟฟ้า",
        category=Category.TOOLS,
        price_per_unit=350.0,
        quantity=5,
    )
    inv.add_product(book)

    # พยายามขายเกินสต็อก (สั่งซื้อ 10 ชิ้น แต่มีแค่ 5)
    with pytest.raises(ValueError, match="สต็อกไม่เพียงพอ"):
        inv.sell("คู่มือวิศวกรรมไฟฟ้า", 10)

    # ยอดคงเหลือต้องคงเดิม
    assert inv.get_product("คู่มือวิศวกรรมไฟฟ้า").quantity == 5


def test_physical_product_sell_success_reduces_stock():
    """สินค้าจับต้องได้: เมื่อขายสำเร็จยอดคงเหลือต้องลดลงตามจำนวนที่ขาย"""
    inv = Inventory()
    wire = PhysicalProduct(
        name="สายไฟ 2.5 sq.mm",
        category=Category.ELECTRICAL,
        price_per_unit=50.0,
        quantity=20,
    )
    inv.add_product(wire)

    inv.sell("สายไฟ 2.5 sq.mm", 8)

    assert inv.get_product("สายไฟ 2.5 sq.mm").quantity == 12


# ---------------------------------------------------------------------------
# กฎของสินค้าดิจิทัล (Digital Product)
# ---------------------------------------------------------------------------


def test_digital_product_sell_stock_does_not_decrease():
    """สินค้าดิจิทัล: ขายแล้วยอดคงเหลือไม่ลด"""
    inv = Inventory()
    ebook = DigitalProduct(
        name="E-Book Python สำหรับงานช่าง",
        category=Category.TOOLS,
        price_per_unit=199.0,
        quantity=1,
        download_url="https://downloads.shop.com/ebook-python.pdf",
    )
    inv.add_product(ebook)

    inv.sell("E-Book Python สำหรับงานช่าง", 1, confirmed=True)

    # ขายแล้วยอดคงเหลือต้องไม่ลด
    assert inv.get_product("E-Book Python สำหรับงานช่าง").quantity == 1


def test_digital_product_download_link_blocked_if_unconfirmed():
    """สินค้าดิจิทัล: เปิดลิงก์ดาวน์โหลดไม่ได้ถ้าคำสั่งซื้อยังไม่ยืนยัน"""
    inv = Inventory()
    software = DigitalProduct(
        name="Circuit Designer Pro",
        category=Category.ELECTRICAL,
        price_per_unit=990.0,
        quantity=1,
        download_url="https://downloads.shop.com/circuit-pro.zip",
    )
    inv.add_product(software)

    order = inv.sell("Circuit Designer Pro", 1, confirmed=False)

    with pytest.raises(PermissionError, match="ยังไม่ยืนยัน"):
        order.get_download_link()


def test_digital_product_download_link_accessible_when_confirmed():
    """สินค้าดิจิทัล: เปิดลิงก์ดาวน์โหลดได้เมื่อคำสั่งซื้อยืนยันแล้ว"""
    inv = Inventory()
    software = DigitalProduct(
        name="Circuit Designer Pro",
        category=Category.ELECTRICAL,
        price_per_unit=990.0,
        quantity=1,
        download_url="https://downloads.shop.com/circuit-pro.zip",
    )
    inv.add_product(software)

    order = inv.sell("Circuit Designer Pro", 1, confirmed=True)

    assert order.get_download_link() == "https://downloads.shop.com/circuit-pro.zip"
