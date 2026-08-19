"""ระบบแจ้งเตือน: Notifier protocol, concrete notifiers, และ factory"""

from __future__ import annotations

from typing import Protocol

from models import Product


# ---------------------------------------------------------------------------
# Notifier Protocol (interface)
# ---------------------------------------------------------------------------


class Notifier(Protocol):
    """โปรโตคอลสำหรับช่องทางแจ้งเตือนทุกประเภท"""

    def send(self, product: Product, message: str) -> None:
        """ส่งการแจ้งเตือนเกี่ยวกับสินค้าที่สต็อกต่ำ"""
        ...


# ---------------------------------------------------------------------------
# Concrete Notifiers
# ---------------------------------------------------------------------------


class EmailNotifier:
    """แจ้งเตือนผ่าน Email (จำลองด้วย print)"""

    def __init__(self, recipient_email: str) -> None:
        """สร้าง EmailNotifier พร้อมระบุ email ผู้รับ"""
        self._recipient_email = recipient_email

    def send(self, product: Product, message: str) -> None:
        """ส่งการแจ้งเตือนผ่าน Email (print จำลอง)"""
        print(f"[EMAIL] ถึง {self._recipient_email}: {message}")


class SMSNotifier:
    """แจ้งเตือนผ่าน SMS (จำลองด้วย print)"""

    def __init__(self, phone_number: str) -> None:
        """สร้าง SMSNotifier พร้อมระบุเบอร์โทรผู้รับ"""
        self._phone_number = phone_number

    def send(self, product: Product, message: str) -> None:
        """ส่งการแจ้งเตือนผ่าน SMS (print จำลอง)"""
        print(f"[SMS] ถึง {self._phone_number}: {message}")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class NotifierFactory:
    """Factory สำหรับสร้าง Notifier ตามช่องทางที่ระบุ"""

    @staticmethod
    def create(channel: str, **kwargs: str) -> Notifier:
        """สร้าง Notifier จากชื่อช่องทาง ('email' หรือ 'sms')"""
        if channel == "email":
            return EmailNotifier(
                recipient_email=kwargs.get("recipient_email", "manager@shop.com")
            )
        elif channel == "sms":
            return SMSNotifier(
                phone_number=kwargs.get("phone_number", "0812345678")
            )
        else:
            raise ValueError(f"ไม่รู้จักช่องทาง: {channel}")
