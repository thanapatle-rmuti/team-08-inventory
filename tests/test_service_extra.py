"""Additional tests for InventoryService: Observer notification, receive, and stock_value_report."""

from models import Category, Product
from notifiers import NotifierFactory
from service import Inventory


def test_notifier_low_stock_notification(capsys):
    """ทดสอบ Observer Pattern: แจ้งเตือนเมื่อสต็อกสินค้าต่ำกว่า threshold"""
    inv = Inventory()
    email_notifier = NotifierFactory.create("email", recipient_email="boss@shop.com")
    sms_notifier = NotifierFactory.create("sms", phone_number="0899999999")
    inv.register_notifier(email_notifier)
    inv.register_notifier(sms_notifier)

    product = Product("สายไฟ", Category.ELECTRICAL, 50.0, quantity=10, threshold=8)
    inv.add_product(product)

    # ขาย 3 ชิ้น เหลือ 7 (ต่ำกว่า threshold 8)
    inv.sell("สายไฟ", 3)

    captured = capsys.readouterr().out
    assert "[EMAIL] ถึง boss@shop.com: สต็อกต่ำ: สายไฟ เหลือ 7 (threshold = 8)" in captured
    assert "[SMS] ถึง 0899999999: สต็อกต่ำ: สายไฟ เหลือ 7 (threshold = 8)" in captured

    # ทดสอบ unregister_notifier
    inv.unregister_notifier(sms_notifier)
    inv.sell("สายไฟ", 1)
    captured2 = capsys.readouterr().out
    assert "[EMAIL]" in captured2
    assert "[SMS]" not in captured2


def test_receive_stock():
    """ทดสอบการรับสินค้าเข้าคลัง (receive)"""
    inv = Inventory()
    product = Product("คีมตัด", Category.TOOLS, 300.0, quantity=5)
    inv.add_product(product)

    inv.receive("คีมตัด", 10)
    assert inv.get_product("คีมตัด").quantity == 15


def test_stock_value_report():
    """ทดสอบการสร้างรายงานมูลค่าสต็อกแยกตามหมวดหมู่"""
    inv = Inventory()
    inv.add_product(Product("สายไฟ", Category.ELECTRICAL, 50.0, quantity=10))  # 500
    inv.add_product(Product("คีมตัด", Category.TOOLS, 300.0, quantity=2))       # 600

    report = inv.stock_value_report()
    assert report["Electrical"] == 500.0
    assert report["Tools"] == 600.0
