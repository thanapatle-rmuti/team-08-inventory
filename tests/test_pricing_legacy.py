# tests/test_pricing_legacy.py
"""Characterization Tests สำหรับโมดูล pricing_legacy.py (Lab 5: ขั้นที่ 7)

ชุดการทดสอบนี้ทำหน้าที่เป็น Safety Net เพื่อบันทึกพฤติกรรมจริงของโค้ดเดิม
ทุกค่าในการ Assert ได้รับการยืนยันจากการรันจริง (Verified Baseline)
"""

import datetime

import pytest

import pricing_legacy


@pytest.fixture(autouse=True)
def reset_legacy_globals():
    """ล้างสถานะ Global Mutable State ก่อนและหลังรันแต่ละ Test"""
    pricing_legacy.LOG.clear()
    pricing_legacy.member_points.clear()
    yield
    pricing_legacy.LOG.clear()
    pricing_legacy.member_points.clear()


# ---------------------------------------------------------------------------
# 1. กลุ่มราคาปกติ (Normal Price)
# ---------------------------------------------------------------------------
def test_calc_normal_price():
    """ราคาปกติ: ซื้อ 2 เล่ม เล่มละ 50 บาท (100 บาท + VAT 7% = 107.00 บาท)"""
    items = [("สมุด", 2, 50.0)]
    result = pricing_legacy.calc(items)
    assert result == 107.0
    assert pricing_legacy.LOG == [(None, 107.0)]


# ---------------------------------------------------------------------------
# 2. กลุ่มซื้อจำนวนมาก (Bulk Discounts)
# ---------------------------------------------------------------------------
def test_calc_bulk_tier_50():
    """ซื้อ 50 ชิ้นพอดี: ได้ลด 5% (50 * 10 * 0.95 = 475 + VAT 7% = 508.25)"""
    items = [("สมุด", 50, 10.0)]
    assert pricing_legacy.calc(items) == 508.25


def test_calc_bulk_tier_100():
    """ซื้อ 100 ชิ้นพอดี: ได้ลด 10% (100 * 10 * 0.90 = 900 + VAT 7% = 963.0)"""
    items = [("สมุด", 100, 10.0)]
    assert pricing_legacy.calc(items) == 963.0


# ---------------------------------------------------------------------------
# 3. กลุ่มจำนวนเป็นศูนย์ (Zero Quantity)
# ---------------------------------------------------------------------------
def test_calc_zero_quantity():
    """สินค้าที่มีจำนวน <= 0 จะถูกข้าม ยอดรวมเป็น 0.0"""
    items = [("สมุด", 0, 50.0)]
    assert pricing_legacy.calc(items) == 0.0
    assert pricing_legacy.LOG == [(None, 0.0)]


# ---------------------------------------------------------------------------
# 4. กลุ่มสมาชิก (Member Discount & Loyalty Points)
# ---------------------------------------------------------------------------
def test_calc_member_discount_and_points():
    """สมาชิกได้ลด 5% และได้แต้ม 1 แต้มต่อทุก 100 บาทก่อนภาษี"""
    items = [("สมุด", 20, 10.0)]  # 200 * 0.95 = 190 บาท
    result = pricing_legacy.calc(items, member="somchai")
    assert result == 203.3  # 190 + VAT 7% = 203.3
    assert pricing_legacy.member_points["somchai"] == 1  # int(190 / 100) = 1
    assert pricing_legacy.LOG == [("somchai", 203.3)]


# ---------------------------------------------------------------------------
# 5. กลุ่มคูปอง (Coupons: SAVE50, HALF, NEWYEAR)
# ---------------------------------------------------------------------------
def test_calc_coupon_save50():
    """คูปอง SAVE50: หัก 50 บาท (100 - 50 = 50 + VAT 7% = 53.5)"""
    items = [("ปากกา", 10, 10.0)]
    assert pricing_legacy.calc(items, coupon="SAVE50") == 53.5


def test_calc_coupon_half():
    """คูปอง HALF: ลด 50% (100 * 0.5 = 50 + VAT 7% = 53.5)"""
    items = [("ปากกา", 10, 10.0)]
    assert pricing_legacy.calc(items, coupon="HALF") == 53.5


def test_calc_coupon_newyear_in_january():
    """คูปอง NEWYEAR ใช้ในเดือนมกราคม: ได้ลด 20% (100 * 0.8 = 80 + VAT 7% = 85.6)"""
    items = [("ปากกา", 10, 10.0)]
    january_date = datetime.date(2026, 1, 15)
    assert pricing_legacy.calc(items, coupon="NEWYEAR", today=january_date) == 85.6


def test_calc_coupon_newyear_outside_january():
    """คูปอง NEWYEAR นอกเดือนมกราคม: ไม่ได้ลด (100 + VAT 7% = 107.0)"""
    items = [("ปากกา", 10, 10.0)]
    may_date = datetime.date(2026, 5, 20)
    assert pricing_legacy.calc(items, coupon="NEWYEAR", today=may_date) == 107.0


# ---------------------------------------------------------------------------
# 6. กลุ่มยอดติดลบ (Negative / Clamp to Zero)
# ---------------------------------------------------------------------------
def test_calc_discount_exceeds_price_clamped_to_zero():
    """ส่วนลดมากกว่าราคาสินค้า (30 - 50 = -20) จะถูกจำกัดไม่ให้ติดลบ (เหลือ 0.0)"""
    items = [("ยางลบ", 1, 30.0)]
    result = pricing_legacy.calc(items, coupon="SAVE50")
    assert result == 0.0


# ---------------------------------------------------------------------------
# 7. กลุ่มการบันทึกสถานะ (Global State & Audit Log)
# ---------------------------------------------------------------------------
def test_calc_accumulate_state_multiple_calls():
    """ทดสอบการสะสมค่าข้ามการเรียกฟังก์ชัน (Audit Log และคะแนนสะสม)"""
    pricing_legacy.calc([("สมุด", 20, 10.0)], member="alice")
    pricing_legacy.calc([("สมุด", 30, 10.0)], member="alice")
    
    # รอบแรกได้ 1 แต้ม, รอบสอง 300 * 0.95 = 285 ได้ 2 แต้ม -> รวม 3 แต้ม
    assert pricing_legacy.member_points["alice"] == 3
    assert len(pricing_legacy.LOG) == 2
