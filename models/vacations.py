from datetime import date

from .users import User, find_user_by_id


class Vacation:
    """Заявка на отпуск."""

    def __init__(
        self,
        vacation_id: int,
        user: User,
        start_date: str,
        end_date: str,
        duration: int,
        status: str = "pending",
    ) -> None:
        """Создать заявку на отпуск."""
        self.id = vacation_id
        self.user = user
        self.start_date = start_date
        self.end_date = end_date
        self.duration = duration
        self.status = status  # pending | approved | cancelled

    def cancel(self) -> None:
        """Отменить заявку и вернуть дни пользователю."""
        if self.status == "cancelled":
            return
        self.user.restore_days(self.duration)
        self.status = "cancelled"

    @classmethod
    def from_data(cls, data: dict, users: list[User]) -> "Vacation | None":
        """Создать заявку из данных JSON, восстановив связь с User."""
        user = find_user_by_id(users, data["user_id"])
        if user is None:
            return None
        return cls(
            vacation_id=data["id"],
            user=user,
            start_date=data["start_date"],
            end_date=data["end_date"],
            duration=data["duration"],
            status=data["status"],
        )

    def to_dict(self) -> dict:
        """Преобразовать объект в словарь для JSON."""
        return {
            "id": self.id,
            "user_id": self.user.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration": self.duration,
            "status": self.status,
        }

    def __str__(self) -> str:
        """Строковое представление заявки."""
        return (
            f"Заявка №{self.id} ({self.user.name}): "
            f"{self.start_date} — {self.end_date}, "
            f"{self.duration} дн., статус: {self.status}"
        )


# ---------- функции работы с коллекцией заявок ----------

def is_user_available(
    vacations: list[Vacation],
    user: User,
    start: date,
    end: date,
) -> bool:
    """Проверить отсутствие пересекающихся активных заявок."""
    for v in vacations:
        if v.user.id != user.id or v.status == "cancelled":
            continue
        v_start = date.fromisoformat(v.start_date)
        v_end = date.fromisoformat(v.end_date)
        if start <= v_end and end >= v_start:
            return False
    return True


def create_vacation(
    vacations: list[Vacation],
    user: User,
    start: date,
    end: date,
) -> Vacation | None:
    """Создать заявку на отпуск. None, если создать нельзя."""
    duration = (end - start).days + 1
    if duration <= 0:
        print("Ошибка: дата окончания раньше даты начала.")
        return None
    if duration > user.vacation_days_available:
        print(
            f"Ошибка: недостаточно дней. "
            f"Доступно {user.vacation_days_available}, запрошено {duration}."
        )
        return None
    if not is_user_available(vacations, user, start, end):
        print("Ошибка: на эти даты уже есть активная заявка.")
        return None

    user.reduce_days(duration)

    vacation_id = max((v.id for v in vacations), default=0) + 1
    vacation = Vacation(
        vacation_id=vacation_id,
        user=user,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        duration=duration,
        status="pending",
    )
    vacations.append(vacation)
    return vacation


def cancel_vacation(vacations: list[Vacation], vacation_id: int) -> bool:
    """Найти заявку по id и отменить её."""
    for v in vacations:
        if v.id == vacation_id:
            v.cancel()
            return True
    return False


def filter_vacations_by_user(
    vacations: list[Vacation],
    user: User,
) -> list[Vacation]:
    """Отобрать заявки конкретного пользователя."""
    return [v for v in vacations if v.user.id == user.id]


def sort_vacations_by_start(vacations: list[Vacation]) -> list[Vacation]:
    """Отсортировать заявки по дате начала."""
    return sorted(vacations, key=lambda v: v.start_date)


def get_vacation_status(vacation: Vacation) -> str:
    """Текстовый статус заявки."""
    statuses = {
        "pending": "Ожидает согласования",
        "approved": "Согласована",
        "cancelled": "Отменена",
    }
    return statuses.get(vacation.status, "Неизвестный статус")


def show_vacations(
    vacations: list[Vacation],
    users: list[User] | None = None,
) -> None:
    """Вывести список заявок."""
    if not vacations:
        print("Заявок нет.")
        return
    print(f"{'ID':<4}{'Пользователь':<25}{'Начало':<12}"
          f"{'Конец':<12}{'Дней':<6}{'Статус'}")
    print("-" * 90)
    for v in sort_vacations_by_start(vacations):
        print(
            f"{v.id:<4}{v.user.name:<25}{v.start_date:<12}"
            f"{v.end_date:<12}{v.duration:<6}{get_vacation_status(v)}"
        )
