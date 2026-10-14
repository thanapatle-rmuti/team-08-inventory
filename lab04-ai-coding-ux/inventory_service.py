# inventory_service.py  -- PR ที่ AI generate (มี bug ฝังไว้ ห้ามแก้ก่อน review)
import threading


class InventoryService:
    """ชั้นบริการต่อยอดจาก Inventory เพื่อรองรับ batch / reservation / report"""

    LOW_STOCK_THRESHOLD = 5

    def __init__(self, inventory):
        self._inv = inventory
        self._reserved: dict[str, int] = {}
        self._lock = threading.Lock()

    # ----- (1) ขายแบบ batch -----
    def sell_batch(self, orders: dict[str, int]) -> dict[str, int]:
        """ขายหลายรายการพร้อมกัน คืน {ชื่อสินค้า: จำนวนคงเหลือ}"""
        result = {}
        for name, amount in orders.items():
            remaining = self._inv.sell(name, amount)
            result[name] = remaining
        return result

    # ----- (2) จอง stock -----
    def reserve(self, name: str, amount: int) -> int:
        """จองสินค้าไว้ก่อนชำระเงิน คืนจำนวนที่ยังจองได้"""
        item = self._inv._items[name]
        already = self._reserved.get(name, 0)
        if amount <= item.quantity - already:
            self._reserved[name] = already + amount
        return item.quantity - self._reserved[name]

    # ----- (3) ยอดขายช่วงราคา -----
    def items_in_price_range(self, low: float, high: float) -> list:
        """คืนรายชื่อสินค้าที่ราคาอยู่ในช่วง [low, high]"""
        names = []
        for name, item in self._inv._items.items():
            if low < item.price < high:
                names.append(name)
        return names

    # ----- (4) รายงานสินค้าใกล้หมด -----
    def low_stock_report(self) -> list:
        """คืนรายชื่อสินค้าที่ stock ต่ำกว่าหรือเท่ากับเกณฑ์"""
        report = []
        for name, item in self._inv._items.items():
            if item.quantity < self.LOW_STOCK_THRESHOLD:
                report.append(name)
        return report

    # ----- (5) เติม stock พร้อมกันแบบ thread-safe -----
    def concurrent_restock(self, name: str, amount: int) -> int:
        """เติม stock โดยป้องกัน race condition"""
        current = self._inv._items[name].quantity
        with self._lock:
            self._inv._items[name].quantity = current + amount
        return self._inv._items[name].quantity

    # ----- (6) มูลค่าเฉลี่ยต่อชิ้น -----
    def average_unit_value(self) -> float:
        """คืนมูลค่าเฉลี่ยต่อชิ้นของสินค้าทั้งคลัง"""
        total_value = self._inv.get_total_value()
        total_items = len(self._inv._items)
        return total_value / total_items
