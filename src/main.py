import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from models import Product, Category
from notifiers import NotifierFactory
from service import InventoryService


def test_us01_receive():
    """AC: รับสินค้าเข้าคลัง — สต็อก 20 + รับ 30 = 50"""
    svc = InventoryService()
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 20, 15))
    svc.receive("สายไฟ 2.5 sq.mm", 30)
    p = svc.get_product("สายไฟ 2.5 sq.mm")
    assert p.quantity == 50, f"FAIL: expected 50, got {p.quantity}"
    print("✅ US-01 รับเข้า: PASS")


def test_us01_issue_success():
    """AC: จ่ายสำเร็จ — สต็อก 20 - 10 = 10"""
    svc = InventoryService()
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 20, 15))
    svc.issue("สายไฟ 2.5 sq.mm", 10)
    p = svc.get_product("สายไฟ 2.5 sq.mm")
    assert p.quantity == 10, f"FAIL: expected 10, got {p.quantity}"
    print("✅ US-01 จ่ายออก: PASS")


def test_us01_issue_insufficient():
    """AC: จ่ายเกินสต็อก — ปฏิเสธ สต็อกไม่เปลี่ยน"""
    svc = InventoryService()
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 5, 15))
    try:
        svc.issue("สายไฟ 2.5 sq.mm", 10)
        print("❌ US-01 จ่ายเกิน: FAIL — ไม่ raise error")
    except ValueError as e:
        p = svc.get_product("สายไฟ 2.5 sq.mm")
        assert p.quantity == 5, f"FAIL: stock changed to {p.quantity}"
        assert "สต็อกไม่เพียงพอ" in str(e)
        print("✅ US-01 จ่ายเกิน: PASS")


def test_us01_zero_quantity():
    """AC: บันทึกจำนวน 0 — ปฏิเสธ"""
    svc = InventoryService()
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 20, 15))
    try:
        svc.receive("สายไฟ 2.5 sq.mm", 0)
        print("❌ US-01 จำนวน 0: FAIL — ไม่ raise error")
    except ValueError as e:
        assert "จำนวนต้องมากกว่า 0" in str(e)
        print("✅ US-01 จำนวน 0: PASS")


def test_us02_below_threshold():
    """AC: จ่ายจนต่ำกว่า threshold — ต้องแจ้งเตือน"""
    print("\n--- US-02: จ่ายจนต่ำกว่า threshold ---")
    notifiers = [
        NotifierFactory.create("email", recipient_email="manager@shop.com"),
        NotifierFactory.create("sms", phone_number="0899999999"),
    ]
    svc = InventoryService(notifiers=notifiers)
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 20, 15))
    svc.issue("สายไฟ 2.5 sq.mm", 8)
    p = svc.get_product("สายไฟ 2.5 sq.mm")
    assert p.quantity == 12, f"FAIL: expected 12, got {p.quantity}"
    print("✅ US-02 ต่ำกว่า threshold: PASS (ดู [EMAIL]/[SMS] ด้านบน)")


def test_us02_above_threshold():
    """AC: จ่ายแต่ยังสูงกว่า threshold — ไม่แจ้ง"""
    print("\n--- US-02: ยังสูงกว่า threshold (ต้องไม่มี [EMAIL]/[SMS]) ---")
    notifiers = [
        NotifierFactory.create("email", recipient_email="manager@shop.com"),
    ]
    svc = InventoryService(notifiers=notifiers)
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 50, 15))
    svc.issue("สายไฟ 2.5 sq.mm", 10)
    p = svc.get_product("สายไฟ 2.5 sq.mm")
    assert p.quantity == 40, f"FAIL: expected 40, got {p.quantity}"
    print("✅ US-02 สูงกว่า threshold: PASS")


def test_us02_equal_threshold():
    """AC: สต็อกเท่ากับ threshold พอดี — ไม่แจ้ง"""
    print("\n--- US-02: เท่ากับ threshold (ต้องไม่มี [EMAIL]/[SMS]) ---")
    notifiers = [
        NotifierFactory.create("email", recipient_email="manager@shop.com"),
    ]
    svc = InventoryService(notifiers=notifiers)
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 20, 15))
    svc.issue("สายไฟ 2.5 sq.mm", 5)
    p = svc.get_product("สายไฟ 2.5 sq.mm")
    assert p.quantity == 15, f"FAIL: expected 15, got {p.quantity}"
    print("✅ US-02 เท่ากับ threshold: PASS")


def test_us03_report():
    """AC: รายงานมูลค่าแยกหมวด"""
    print("\n--- US-03: รายงานมูลค่าสต็อก ---")
    svc = InventoryService()
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 100, 15))
    svc.add_product(Product("คีมตัด", Category.TOOLS, 300.0, 10, 5))
    report = svc.stock_value_report()
    assert report["Electrical"] == 5000, f"FAIL: Electrical = {report.get('Electrical')}"
    assert report["Tools"] == 3000, f"FAIL: Tools = {report.get('Tools')}"
    print(f"  Electrical = {report['Electrical']} บาท")
    print(f"  Tools = {report['Tools']} บาท")
    print(f"  รวม = {sum(report.values())} บาท")
    print("✅ US-03 รายงาน: PASS")


def test_us04_set_threshold():
    """AC: ตั้งค่า threshold"""
    svc = InventoryService()
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 20, 15))
    p = svc.get_product("สายไฟ 2.5 sq.mm")
    p.set_threshold(20)
    assert p.threshold == 20, f"FAIL: expected 20, got {p.threshold}"
    print("✅ US-04 ตั้ง threshold: PASS")


def test_us04_negative_threshold():
    """AC: ตั้ง threshold ค่าลบ — ปฏิเสธ"""
    svc = InventoryService()
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 20, 15))
    p = svc.get_product("สายไฟ 2.5 sq.mm")
    try:
        p.set_threshold(-5)
        print("❌ US-04 threshold ลบ: FAIL — ไม่ raise error")
    except ValueError as e:
        assert p.threshold == 15
        print("✅ US-04 threshold ลบ: PASS")


def test_us05_multi_channel():
    """AC: แจ้งเตือนหลายช่องทาง"""
    print("\n--- US-05: หลายช่องทาง ---")
    notifiers = [
        NotifierFactory.create("email", recipient_email="manager@shop.com"),
        NotifierFactory.create("sms", phone_number="0899999999"),
    ]
    svc = InventoryService(notifiers=notifiers)
    svc.add_product(Product("สายไฟ 2.5 sq.mm", Category.ELECTRICAL, 50.0, 20, 15))
    svc.issue("สายไฟ 2.5 sq.mm", 8)
    print("✅ US-05 หลายช่องทาง: PASS (ดู [EMAIL]+[SMS] ด้านบน)")


if __name__ == "__main__":
    test_us01_receive()
    test_us01_issue_success()
    test_us01_issue_insufficient()
    test_us01_zero_quantity()
    test_us02_below_threshold()
    test_us02_above_threshold()
    test_us02_equal_threshold()
    test_us03_report()
    test_us04_set_threshold()
    test_us04_negative_threshold()
    test_us05_multi_channel()
    print("\n🎉 ทดสอบ AC ทั้งหมดเสร็จสิ้น")
