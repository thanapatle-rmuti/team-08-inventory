# pricing_legacy.py
# โมดูลคำนวณราคาและส่วนลดของระบบ Inventory
# เขียนเร่งรีบ ไม่มี test ไม่มีใครกล้าแตะ

import datetime

TAX = 0.07
member_points = {}
LOG = []


def calc(items, member=None, coupon=None, today=None):
    # items = list ของ tuple (ชื่อ, จำนวน, ราคาต่อหน่วย)
    # member = ชื่อสมาชิก (ถ้ามี)
    # coupon = รหัสคูปอง (ถ้ามี)
    # today = วันที่ (ถ้าไม่ใส่ใช้วันนี้)
    t = 0
    for i in items:
        # คำนวณราคารวมก่อนส่วนลด
        if i[1] <= 0:
            continue
        sub = i[1] * i[2]
        # ลดราคาสินค้าซื้อเยอะ
        if i[1] >= 100:
            sub = sub * 0.9
        elif i[1] >= 50:
            sub = sub * 0.95
        t = t + sub
    # ส่วนลดสมาชิก
    if member != None:
        if member not in member_points:
            member_points[member] = 0
        # สมาชิกลด 5%
        t = t * 0.95
        # สะสมแต้ม 1 แต้มต่อ 100 บาท
        member_points[member] = member_points[member] + int(t / 100)
    # คูปอง
    if coupon != None:
        if coupon == "SAVE50":
            t = t - 50
        elif coupon == "HALF":
            t = t * 0.5
        elif coupon == "NEWYEAR":
            # ใช้ได้เฉพาะเดือนมกราคม
            if today == None:
                today = datetime.date.today()
            if today.month == 1:
                t = t * 0.8
    if t < 0:
        t = 0
    # บวกภาษี
    t = t + t * TAX
    # ปัดเศษ
    t = round(t, 2)
    LOG.append((member, t))
    return t
