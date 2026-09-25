"""Tests for Inventory / InventoryService - Lab 5 TDD."""

import pytest

from models import Category, Product
from service import Inventory

# ---------------------------------------------------------------------------
# ขั้นที่ 2: TDD 6 กรณีสำหรับ low_stock_items(threshold)
# ---------------------------------------------------------------------------


def test_low_stock_items_all_above_threshold():
    """กรณีที่ 1: ของทุกชิ้นมากกว่า threshold -> คืน list ว่าง"""
    inv = Inventory()
    inv.add_product(Product("สินค้า A", Category.TOOLS, 100.0, quantity=15))
    inv.add_product(Product("สินค้า B", Category.TOOLS, 200.0, quantity=20))

    result = inv.low_stock_items(10)
    assert result == []


def test_low_stock_items_exact_threshold():
    """กรณีที่ 2: มีชิ้นที่เท่ากับ threshold พอดี -> ต้องถูกนับรวมด้วย (<= threshold)"""
    inv = Inventory()
    inv.add_product(Product("สินค้า A", Category.TOOLS, 100.0, quantity=10))
    inv.add_product(Product("สินค้า B", Category.TOOLS, 200.0, quantity=15))

    result = inv.low_stock_items(10)
    assert result == ["สินค้า A"]


def test_low_stock_items_multiple_sorted_by_name():
    """กรณีที่ 3: มีหลายชิ้นเข้าเกณฑ์ -> ผลลัพธ์เรียงตามชื่อ ไม่ใช่ตามลำดับที่เพิ่ม"""
    inv = Inventory()
    # เพิ่มแบบไม่เรียงชื่อ: C -> A -> B
    inv.add_product(Product("ฮาร์ดแวร์ C", Category.TOOLS, 100.0, quantity=3))
    inv.add_product(Product("กาว A", Category.TOOLS, 50.0, quantity=2))
    inv.add_product(Product("บันได B", Category.SAFETY, 500.0, quantity=4))
    inv.add_product(Product("ของเกิน D", Category.TOOLS, 100.0, quantity=20))

    result = inv.low_stock_items(5)
    assert result == ["กาว A", "บันได B", "ฮาร์ดแวร์ C"]


def test_low_stock_items_empty_inventory():
    """กรณีที่ 4: คลังว่าง -> คืน list ว่าง ไม่ใช่ error"""
    inv = Inventory()
    result = inv.low_stock_items(10)
    assert result == []


def test_low_stock_items_threshold_zero():
    """กรณีที่ 5: threshold เป็น 0 -> คืนเฉพาะชิ้นที่เหลือ 0"""
    inv = Inventory()
    inv.add_product(Product("ของหมด 1", Category.TOOLS, 100.0, quantity=0))
    inv.add_product(Product("ของมี 2", Category.TOOLS, 100.0, quantity=1))
    inv.add_product(Product("ของหมด 2", Category.SAFETY, 200.0, quantity=0))

    result = inv.low_stock_items(0)
    assert result == ["ของหมด 1", "ของหมด 2"]


def test_low_stock_items_negative_threshold():
    """กรณีที่ 6: threshold ติดลบ -> คืน list ว่าง (ข้อตกลงทีม: สต็อกไม่ติดลบ คืน [])"""
    inv = Inventory()
    inv.add_product(Product("ของหมด", Category.TOOLS, 100.0, quantity=0))
    inv.add_product(Product("ของมี", Category.TOOLS, 100.0, quantity=5))

    result = inv.low_stock_items(-1)
    assert result == []


# ---------------------------------------------------------------------------
# ขั้นที่ 4: Test ชุดของ sell (รวมกรณีปกติของ AI + Edge Cases ที่เขียนเสริม)
# ---------------------------------------------------------------------------


def test_sell_basic_happy_path():
    """กรณีที่ AI มักเขียนให้ (กรณีปกติ): ขายสำเร็จและสต็อกลดลงถูกต้อง"""
    inv = Inventory()
    inv.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, quantity=20))

    result = inv.sell("สายไฟ 2.5 sq.mm", 5)

    assert result.product_name == "สายไฟ 2.5 sq.mm"
    assert result.quantity == 5
    assert inv.get_product("สายไฟ 2.5 sq.mm").quantity == 15


def test_sell_exact_stock_remaining_zero():
    """กลุ่มค่าขอบ: ขายพอดีกับที่เหลือทั้งหมด สต็อกต้องเหลือ 0 พอดี"""
    inv = Inventory()
    inv.add_product(Product("คีมตัด", Category.TOOLS, 300.0, quantity=5))

    inv.sell("คีมตัด", 5)

    assert inv.get_product("คีมตัด").quantity == 0


def test_sell_zero_quantity_raises_value_error():
    """กลุ่มค่าที่ไม่ควรรับ: ขายจำนวน 0 ระบบต้องปฏิเสธด้วย ValueError"""
    inv = Inventory()
    inv.add_product(Product("คีมตัด", Category.TOOLS, 300.0, quantity=5))

    with pytest.raises(ValueError, match="จำนวนต้องมากกว่า 0"):
        inv.sell("คีมตัด", 0)


def test_sell_negative_quantity_raises_value_error():
    """กลุ่มค่าที่ไม่ควรรับ: ขายจำนวนติดลบ ระบบต้องปฏิเสธด้วย ValueError"""
    inv = Inventory()
    inv.add_product(Product("คีมตัด", Category.TOOLS, 300.0, quantity=5))

    with pytest.raises(ValueError, match="จำนวนต้องมากกว่า 0"):
        inv.sell("คีมตัด", -3)


def test_sell_exceeds_stock_raises_value_error():
    """กลุ่มค่าที่ไม่ควรรับ: ขายเกินสต็อกที่มี ระบบต้องปฏิเสธด้วย ValueError"""
    inv = Inventory()
    inv.add_product(Product("คีมตัด", Category.TOOLS, 300.0, quantity=5))

    with pytest.raises(ValueError, match="สต็อกไม่เพียงพอ"):
        inv.sell("คีมตัด", 6)


def test_sell_non_existent_product_raises_key_error():
    """กลุ่มเส้นทาง error: ขายของที่ไม่มีในคลัง ระบบต้องโยน KeyError พร้อมระบุชื่อสินค้า"""
    inv = Inventory()

    with pytest.raises(KeyError, match="ไม่พบสินค้า: สินค้าที่ไม่มีจริง"):
        inv.sell("สินค้าที่ไม่มีจริง", 1)


def test_sell_invalid_type_float_raises_type_error():
    """กลุ่มชนิดข้อมูล: ใส่จำนวนเป็นทศนิยม ระบบต้องปฏิเสธด้วย TypeError"""
    inv = Inventory()
    inv.add_product(Product("สายไฟ", Category.ELECTRICAL, 50.0, quantity=10))

    with pytest.raises(TypeError, match="จำนวนต้องเป็นตัวเลขจำนวนเต็ม"):
        inv.sell("สายไฟ", 2.5)  # type: ignore


def test_sell_invalid_type_string_raises_type_error():
    """กลุ่มชนิดข้อมูล: ใส่จำนวนเป็นข้อความ ระบบต้องปฏิเสธด้วย TypeError"""
    inv = Inventory()
    inv.add_product(Product("สายไฟ", Category.ELECTRICAL, 50.0, quantity=10))

    with pytest.raises(TypeError, match="จำนวนต้องเป็นตัวเลขจำนวนเต็ม"):
        inv.sell("สายไฟ", "ห้า")  # type: ignore
