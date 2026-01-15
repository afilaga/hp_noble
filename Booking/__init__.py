from datetime import datetime, time, timedelta
from enum import Enum
from typing import Optional, List, Dict
import uuid


class TableStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"


class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SEATED = "seated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Customer:
    def __init__(self, name: str, phone: str, email: Optional[str] = None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.phone = phone
        self.email = email
        self.visits_count = 0
        self.notes = []

    def add_visit(self):
        self.visits_count += 1

    def add_note(self, note: str):
        self.notes.append(note)


class Table:
    def __init__(self, number: int, capacity: int, location: str = "main"):
        self.id = str(uuid.uuid4())[:8]
        self.number = number
        self.capacity = capacity
        self.location = location
        self.status = TableStatus.AVAILABLE
        self.current_reservation_id: Optional[str] = None
        self.features: List[str] = []
        self.min_reservation_time = 30
        self.max_reservation_time = 120

    def is_available(self) -> bool:
        return self.status == TableStatus.AVAILABLE

    def reserve(self, reservation_id: str):
        self.status = TableStatus.RESERVED
        self.current_reservation_id = reservation_id

    def release(self):
        self.status = TableStatus.AVAILABLE
        self.current_reservation_id = None

    def seat_guests(self):
        self.status = TableStatus.OCCUPIED

    def add_feature(self, feature: str):
        if feature not in self.features:
            self.features.append(feature)


class Reservation:
    def __init__(
        self,
        customer: Customer,
        table: Table,
        start_time: datetime,
        party_size: int,
        duration_minutes: int = 90,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.customer = customer
        self.table = table
        self.start_time = start_time
        self.end_time = start_time + timedelta(minutes=duration_minutes)
        self.party_size = party_size
        self.duration_minutes = duration_minutes
        self.status = ReservationStatus.PENDING
        self.special_requests: List[str] = []
        self.created_at = datetime.now()
        self.confirmed_at: Optional[datetime] = None
        self.seated_at: Optional[datetime] = None
        self.cancelled_at: Optional[datetime] = None
        self.cancellation_reason: Optional[str] = None

        customer.add_visit()
        table.reserve(self.id)

    def confirm(self):
        if self.status == ReservationStatus.PENDING:
            self.status = ReservationStatus.CONFIRMED
            self.confirmed_at = datetime.now()

    def seat(self):
        if self.status in [ReservationStatus.CONFIRMED, ReservationStatus.PENDING]:
            self.status = ReservationStatus.SEATED
            self.seated_at = datetime.now()
            self.table.seat_guests()

    def complete(self):
        self.status = ReservationStatus.COMPLETED
        self.table.release()

    def cancel(self, reason: str = ""):
        self.status = ReservationStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.cancellation_reason = reason
        self.table.release()

    def mark_no_show(self):
        self.status = ReservationStatus.NO_SHOW
        self.table.release()

    def add_special_request(self, request: str):
        self.special_requests.append(request)

    def is_active(self) -> bool:
        return self.status in [
            ReservationStatus.PENDING,
            ReservationStatus.CONFIRMED,
            ReservationStatus.SEATED,
        ]

    def is_upcoming(self) -> bool:
        return self.start_time > datetime.now() and self.is_active()

    def is_overdue(self) -> bool:
        return (
            datetime.now() > self.end_time and self.status == ReservationStatus.SEATED
        )


class TableRepository:
    def __init__(self):
        self._tables: Dict[str, Table] = {}

    def add(self, table: Table):
        self._tables[table.id] = table

    def get(self, table_id: str) -> Optional[Table]:
        return self._tables.get(table_id)

    def get_by_number(self, table_number: int) -> Optional[Table]:
        for table in self._tables.values():
            if table.number == table_number:
                return table
        return None

    def get_available_by_capacity(
        self, min_capacity: int, start_time: datetime, end_time: datetime
    ) -> List[Table]:
        available_tables = []
        for table in self._tables.values():
            if table.capacity >= min_capacity and table.is_available():
                if self._is_time_slot_available(table, start_time, end_time):
                    available_tables.append(table)
        return sorted(available_tables, key=lambda t: t.capacity)

    def _is_time_slot_available(
        self, table: Table, start_time: datetime, end_time: datetime
    ) -> bool:
        return True

    def get_all(self) -> List[Table]:
        return list(self._tables.values())


class ReservationRepository:
    def __init__(self):
        self._reservations: Dict[str, Reservation] = {}

    def add(self, reservation: Reservation):
        self._reservations[reservation.id] = reservation

    def get(self, reservation_id: str) -> Optional[Reservation]:
        return self._reservations.get(reservation_id)

    def get_by_table(
        self, table: Table, date: Optional[datetime] = None
    ) -> List[Reservation]:
        reservations = []
        for res in self._reservations.values():
            if res.table.id == table.id:
                if date is None or res.start_time.date() == date.date():
                    reservations.append(res)
        return sorted(reservations, key=lambda r: r.start_time)

    def get_by_customer(self, customer: Customer) -> List[Reservation]:
        return sorted(
            [r for r in self._reservations.values() if r.customer.id == customer.id],
            key=lambda r: r.start_time,
            reverse=True,
        )

    def get_upcoming(self, limit: int = 10) -> List[Reservation]:
        now = datetime.now()
        upcoming = [r for r in self._reservations.values() if r.is_upcoming()]
        return sorted(upcoming, key=lambda r: r.start_time)[:limit]

    def get_active(self) -> List[Reservation]:
        return [r for r in self._reservations.values() if r.is_active()]


class RestaurantBookingService:
    def __init__(self):
        self.table_repository = TableRepository()
        self.reservation_repository = ReservationRepository()

    def add_table(self, number: int, capacity: int, location: str = "main") -> Table:
        table = Table(number, capacity, location)
        self.table_repository.add(table)
        return table

    def check_availability(
        self, party_size: int, start_time: datetime, end_time: datetime
    ) -> List[Table]:
        return self.table_repository.get_available_by_capacity(
            party_size, start_time, end_time
        )

    def create_reservation(
        self,
        customer: Customer,
        table: Table,
        start_time: datetime,
        party_size: int,
        duration_minutes: int = 90,
        special_requests: Optional[List[str]] = None,
    ) -> Reservation:
        if not table.is_available():
            raise ValueError(f"Table {table.number} is not available")

        if party_size > table.capacity:
            raise ValueError(
                f"Party size {party_size} exceeds table capacity {table.capacity}"
            )

        reservation = Reservation(
            customer=customer,
            table=table,
            start_time=start_time,
            party_size=party_size,
            duration_minutes=duration_minutes,
        )

        if special_requests:
            for request in special_requests:
                reservation.add_special_request(request)

        self.reservation_repository.add(reservation)
        return reservation

    def confirm_reservation(self, reservation_id: str) -> bool:
        reservation = self.reservation_repository.get(reservation_id)
        if reservation:
            reservation.confirm()
            return True
        return False

    def seat_guests(self, reservation_id: str) -> bool:
        reservation = self.reservation_repository.get(reservation_id)
        if reservation:
            reservation.seat()
            return True
        return False

    def complete_reservation(self, reservation_id: str) -> bool:
        reservation = self.reservation_repository.get(reservation_id)
        if reservation:
            reservation.complete()
            return True
        return False

    def cancel_reservation(self, reservation_id: str, reason: str = "") -> bool:
        reservation = self.reservation_repository.get(reservation_id)
        if reservation:
            reservation.cancel(reason)
            return True
        return False

    def mark_no_show(self, reservation_id: str) -> bool:
        reservation = self.reservation_repository.get(reservation_id)
        if reservation:
            reservation.mark_no_show()
            return True
        return False

    def get_todays_reservations(self) -> List[Reservation]:
        today = datetime.now().date()
        return sorted(
            [
                r
                for r in self.reservation_repository.get_active()
                if r.start_time.date() == today
            ],
            key=lambda r: r.start_time,
        )

    def get_upcoming_reservations(self, limit: int = 10) -> List[Reservation]:
        return self.reservation_repository.get_upcoming(limit)

    def find_best_table(
        self, party_size: int, start_time: datetime, duration_minutes: int = 90
    ) -> Optional[Table]:
        end_time = start_time + timedelta(minutes=duration_minutes)
        available = self.check_availability(party_size, start_time, end_time)
        if available:
            for table in available:
                if table.capacity == party_size:
                    return table
            return available[0]
        return None

    def get_reservation_stats(self) -> Dict:
        reservations = list(self.reservation_repository._reservations.values())
        if not reservations:
            return {
                "total": 0,
                "completed": 0,
                "cancelled": 0,
                "no_show": 0,
                "completion_rate": 0.0,
            }

        completed = sum(
            1 for r in reservations if r.status == ReservationStatus.COMPLETED
        )
        cancelled = sum(
            1 for r in reservations if r.status == ReservationStatus.CANCELLED
        )
        no_show = sum(1 for r in reservations if r.status == ReservationStatus.NO_SHOW)

        return {
            "total": len(reservations),
            "completed": completed,
            "cancelled": cancelled,
            "no_show": no_show,
            "completion_rate": round(completed / len(reservations) * 100, 2),
        }


def demo():
    service = RestaurantBookingService()

    service.add_table(1, 2, "window")
    service.add_table(2, 4, "main")
    service.add_table(3, 6, "main")
    service.add_table(4, 8, "private")
    service.add_table(5, 2, "bar")

    customer1 = Customer("Иван Петров", "+7 999 123-45-67", "ivan@email.com")
    customer2 = Customer("Мария Сидорова", "+7 999 987-65-43")

    tomorrow_18 = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    tomorrow_18 += timedelta(days=1)

    best_table = service.find_best_table(4, tomorrow_18)
    if best_table:
        reservation = service.create_reservation(
            customer=customer1,
            table=best_table,
            start_time=tomorrow_18,
            party_size=4,
            special_requests=["Праздничный торт", "Цветы на стол"],
        )
        print(f"Создано бронирование: {reservation.id}")
        print(f"Столик: #{best_table.number} ({best_table.location})")
        print(f"Время: {reservation.start_time}")

    tomorrow_19 = tomorrow_18 + timedelta(hours=1)
    best_table2 = service.find_best_table(2, tomorrow_19)
    if best_table2:
        reservation2 = service.create_reservation(
            customer=customer2, table=best_table2, start_time=tomorrow_19, party_size=2
        )

    service.confirm_reservation(reservation.id)

    upcoming = service.get_upcoming_reservations()
    print(f"\nПредстоящие бронирования: {len(upcoming)}")

    stats = service.get_reservation_stats()
    print(f"Статистика: {stats}")


if __name__ == "__main__":
    demo()
