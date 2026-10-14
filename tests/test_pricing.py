# tests/test_pricing.py
"""Characterization Tests สำหรับโมดูลที่ Refactor แล้ว (pricing.py) - Lab 5 ขั้นที่ 8

พิสูจน์ว่าพฤติกรรมเดิมทุกกรณี 100% ยังคงทำงานถูกต้องเหมือนเดิมทุกประการ
"""

import datetime

import pytest

import pricing


@pytest.fixture(autouse=True)
def reset_globals():
    """ล้างสถานะ Global Mutable State ก่อนและหลังรันแต่ละ Test"""
    pricing.LOG.clear()
    pricing.member_points.clear()
    yield
    pricing.LOG.clear()
    pricing.member_points.clear()


def test_refactored_calc_normal_price():
    items = [("สมุด", 2, 50.0)]
    result = pricing.calc(items)
    assert result == 107.0
    assert pricing.LOG == [(None, 107.0)]


def test_refactored_calc_bulk_tier_50():
    items = [("สมุด", 50, 10.0)]
    assert pricing.calc(items) == 508.25


def test_refactored_calc_bulk_tier_100():
    items = [("สมุด", 100, 10.0)]
    assert pricing.calc(items) == 963.0


def test_refactored_calc_zero_quantity():
    items = [("สมุด", 0, 50.0)]
    assert pricing.calc(items) == 0.0
    assert pricing.LOG == [(None, 0.0)]


def test_refactored_calc_member_discount_and_points():
    items = [("สมุด", 20, 10.0)]
    result = pricing.calc(items, member="somchai")
    assert result == 203.3
    assert pricing.member_points["somchai"] == 1
    assert pricing.LOG == [("somchai", 203.3)]


def test_refactored_calc_coupon_save50():
    items = [("ปากกา", 10, 10.0)]
    assert pricing.calc(items, coupon="SAVE50") == 53.5


def test_refactored_calc_coupon_half():
    items = [("ปากกา", 10, 10.0)]
    assert pricing.calc(items, coupon="HALF") == 53.5


def test_refactored_calc_coupon_newyear_in_january():
    items = [("ปากกา", 10, 10.0)]
    january_date = datetime.date(2026, 1, 15)
    assert pricing.calc(items, coupon="NEWYEAR", today=january_date) == 85.6


def test_refactored_calc_coupon_newyear_outside_january():
    items = [("ปากกา", 10, 10.0)]
    may_date = datetime.date(2026, 5, 20)
    assert pricing.calc(items, coupon="NEWYEAR", today=may_date) == 107.0


def test_refactored_calc_discount_exceeds_price_clamped_to_zero():
    items = [("ยางลบ", 1, 30.0)]
    result = pricing.calc(items, coupon="SAVE50")
    assert result == 0.0


def test_refactored_calc_accumulate_state_multiple_calls():
    pricing.calc([("สมุด", 20, 10.0)], member="alice")
    pricing.calc([("สมุด", 30, 10.0)], member="alice")
    assert pricing.member_points["alice"] == 3
    assert len(pricing.LOG) == 2
