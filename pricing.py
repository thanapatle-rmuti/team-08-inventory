# pricing.py -- โมดูลคำนวณราคาและส่วนลด (Refactored Clean Code - Lab 5: ขั้นที่ 8)
"""โมดูลคำนวณราคา ส่วนลด และภาษีมูลค่าเพิ่มสำหรับระบบสต็อกสินค้า

ได้รับการจัดระเบียบใหม่ (Refactored) เพื่อแก้ไข Code Smells ทั้ง 7 ข้อ:
1. กำหนดค่าคงที่ชัดเจน (No Magic Numbers)
2. แยกฟังก์ชันย่อยตามหลัก Single Responsibility Principle (SRP)
3. ปรับปรุงชื่อตัวแปรให้อ่านเข้าใจง่าย สื่อความหมาย
4. แก้ไขการเปรียบเทียบตามมาตรฐาน PEP 8 (ใช้ is not None)
5. รักษาพฤติกรรมเดิม 100% (Backward Compatible Contract)
"""

from __future__ import annotations

import datetime

# ---------------------------------------------------------------------------
# ค่าคงที่ทางธุรกิจ (Business Rule Constants)
# ---------------------------------------------------------------------------
DEFAULT_TAX_RATE: float = 0.07
BULK_THRESHOLD_HIGH: int = 100
BULK_DISCOUNT_HIGH: float = 0.90   # ลด 10%
BULK_THRESHOLD_MID: int = 50
BULK_DISCOUNT_MID: float = 0.95    # ลด 5%

MEMBER_DISCOUNT_RATE: float = 0.95 # สมาชิกลด 5%
POINTS_SPENDING_DIVISOR: int = 100 # 1 แต้มต่อทุก 100 บาท

# ฐานข้อมูลจำลองและบันทึกประวัติ (ยังคงรักษา Interface เดิม)
TAX: float = DEFAULT_TAX_RATE
member_points: dict[str, int] = {}
LOG: list[tuple[str | None, float]] = []


# ---------------------------------------------------------------------------
# ฟังก์ชันย่อยแยกตามความรับผิดชอบ (SRP Helper Functions)
# ---------------------------------------------------------------------------
def calculate_items_subtotal(items: list[tuple[str, int, float]]) -> float:
    """คำนวณราคารวมของสินค้า พร้อมคิดส่วนลดซื้อเหมาตามจำนวนชิ้น"""
    subtotal = 0.0
    for _name, quantity, unit_price in items:
        if quantity <= 0:
            continue
        line_total = quantity * unit_price
        if quantity >= BULK_THRESHOLD_HIGH:
            line_total *= BULK_DISCOUNT_HIGH
        elif quantity >= BULK_THRESHOLD_MID:
            line_total *= BULK_DISCOUNT_MID
        subtotal += line_total
    return subtotal


def apply_member_discount(
    amount: float,
    member: str | None,
    points_repo: dict[str, int],
) -> float:
    """คิดส่วนลดสมาชิกและบันทึกคะแนนสะสม"""
    if member is None:
        return amount
    if member not in points_repo:
        points_repo[member] = 0
    discounted = amount * MEMBER_DISCOUNT_RATE
    points_repo[member] += int(discounted / POINTS_SPENDING_DIVISOR)
    return discounted


def apply_coupon_discount(
    amount: float,
    coupon: str | None,
    today: datetime.date | None = None,
) -> float:
    """คำนวณส่วนลดจากรหัสคูปองโปรโมชัน"""
    if coupon is None:
        return amount
    if coupon == "SAVE50":
        return amount - 50.0
    if coupon == "HALF":
        return amount * 0.5
    if coupon == "NEWYEAR":
        check_date = datetime.date.today() if today is None else today
        if check_date.month == 1:
            return amount * 0.8
    return amount


def finalize_tax_and_rounding(amount: float, tax_rate: float = DEFAULT_TAX_RATE) -> float:
    """จำกัดยอดไม่ให้ติดลบ รวมภาษีมูลค่าเพิ่ม และปัดเศษทศนิยม 2 ตำแหน่ง"""
    net_amount = max(0.0, amount)
    total_with_tax = net_amount + (net_amount * tax_rate)
    return round(total_with_tax, 2)


# ---------------------------------------------------------------------------
# ฟังก์ชันหลัก (Main Orchestrator)
# ---------------------------------------------------------------------------
def calc(
    items: list[tuple[str, int, float]],
    member: str | None = None,
    coupon: str | None = None,
    today: datetime.date | None = None,
) -> float:
    """ฟังก์ชันหลักสำหรับคำนวณราคาสุทธิ (รักษาพฤติกรรมเดิม 100%)"""
    subtotal = calculate_items_subtotal(items)
    after_member = apply_member_discount(subtotal, member, member_points)
    after_coupon = apply_coupon_discount(after_member, coupon, today)
    final_total = finalize_tax_and_rounding(after_coupon, TAX)
    
    LOG.append((member, final_total))
    return final_total
