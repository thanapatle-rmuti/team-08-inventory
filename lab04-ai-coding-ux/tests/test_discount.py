# tests/test_discount.py
import pytest
from discount import apply_discount, bulk_total, average_price, cheapest_n


def test_apply_discount_basic():
    # ลด 10% จาก 100 บาท ควรเหลือ 90 บาท
    assert apply_discount(100.0, 10) == 90.0


def test_apply_discount_zero():
    # ลด 0% ควรได้ราคาเดิม
    assert apply_discount(250.0, 0) == 250.0


def test_bulk_total():
    # (100 + 100 + 100) = 300 ลด 10% ควรเหลือ 270
    assert bulk_total([100.0, 100.0, 100.0], 10) == 270.0


def test_average_price():
    # ค่าเฉลี่ยของ [10, 20, 30] = 20
    assert average_price([10.0, 20.0, 30.0]) == 20.0


def test_average_price_empty():
    # คลังว่างควรได้ 0.0 ไม่ใช่ crash
    assert average_price([]) == 0.0


def test_cheapest_n():
    # ถูกสุด 2 รายการของ [50, 10, 30, 20] = [10, 20]
    assert cheapest_n([50.0, 10.0, 30.0, 20.0], 2) == [10.0, 20.0]
