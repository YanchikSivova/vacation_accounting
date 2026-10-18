from datetime import date

from .users import User, find_user_by_id


class Vacation:
    """Тип отпуска."""

    def __init__(
        self,
        vacation_id: int,
        name: str,
        deducts_vacation_days: bool = False,
    ) -> None:
        self.id = vacation_id
        self.name = name
        self.deducts_vacation_days = deducts_vacation_days

    def __str__(self) -> str:
        return self.name


VACATION_TYPES = (
    Vacation(1, "Ежегодный оплачиваемый", deducts_vacation_days=True),
    Vacation(2, "Неоплачиваемый"),
    Vacation(3, "По уходу за ребёнком"),
    Vacation(4, "По болезни"),
)


def find_vacation_by_id(vacation_id: int) -> Vacation | None:
    """Найти тип отпуска по id."""
    return next(
        (
            vacation
            for vacation in VACATION_TYPES
            if vacation.id == vacation_id
        ),
        None,
    )


class VacationRequest:
    """Заявка пользователя на отпуск."""

    def __init__(
        self,
        request_id: int,
        user: User,
        vacation: Vacation,
        start_date: str,
        end_date: str,
        duration: int,
        status: str = "pending",
    ) -> None:
        self.id = request_id
        self.user = user
        self.vacation = vacation
        self.start_date = start_date
        self.end_date = end_date
        self.duration = duration
        self.status = status

    def cancel(self) -> None:
        """Отменить заявку и вернуть списанные дни пользователю."""
        if self.status == "cancelled":
            return
        if self.vacation.deducts_vacation_days:
            self.user.restore_days(self.duration)
        self.status = "cancelled"

    @classmethod
    def from_data(
        cls,
        data: dict,
        users: list[User],
    ) -> "VacationRequest | None":
        """Создать заявку из JSON и восстановить связанные объекты."""
        user = find_user_by_id(users, data["user_id"])
        if user is None:
            return None

        # Старые записи без типа обозначали ежегодный оплачиваемый отпуск.
        vacation_id = data.get("vacation_id", 1)
        vacation = find_vacation_by_id(vacation_id)
        if vacation is None:
            raise ValueError(f"Неизвестный тип отпуска: {vacation_id}")

        return cls(
            request_id=data["id"],
            user=user,
            vacation=vacation,
            start_date=data["start_date"],
            end_date=data["end_date"],
            duration=data["duration"],
            status=data["status"],
        )

    def to_dict(self) -> dict:
        """Преобразовать заявку в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "user_id": self.user.id,
            "vacation_id": self.vacation.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration": self.duration,
            "status": self.status,
        }

    def __str__(self) -> str:
        return (
            f"Заявка №{self.id} ({self.user.name}): {self.vacation.name}, "
            f"{self.start_date} — {self.end_date}, "
            f"{self.duration} дн., статус: {self.status}"
        )


def is_user_available(
    requests: list[VacationRequest],
    user: User,
    start: date,
    end: date,
) -> bool:
    """Проверить отсутствие пересекающихся активных заявок."""
    for request in requests:
        if request.user.id != user.id or request.status == "cancelled":
            continue
        request_start = date.fromisoformat(request.start_date)
        request_end = date.fromisoformat(request.end_date)
        if start <= request_end and end >= request_start:
            return False
    return True


def create_vacation_request(
    requests: list[VacationRequest],
    user: User,
    vacation: Vacation,
    start: date,
    end: date,
) -> VacationRequest | None:
    """Создать заявку на отпуск; вернуть None, если создать её нельзя."""
    duration = (end - start).days + 1
    if duration <= 0:
        print("Ошибка: дата окончания раньше даты начала.")
        return None
    if (
        vacation.deducts_vacation_days
        and duration > user.vacation_days_available
    ):
        print(
            f"Ошибка: недостаточно дней. "
            f"Доступно {user.vacation_days_available}, запрошено {duration}."
        )
        return None
    if not is_user_available(requests, user, start, end):
        print("Ошибка: на эти даты уже есть активная заявка.")
        return None

    if vacation.deducts_vacation_days and not user.reduce_days(duration):
        print(
            f"Ошибка: недостаточно дней. "
            f"Доступно {user.vacation_days_available}, запрошено {duration}."
        )
        return None

    request_id = max((request.id for request in requests), default=0) + 1
    request = VacationRequest(
        request_id=request_id,
        user=user,
        vacation=vacation,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        duration=duration,
    )
    requests.append(request)
    return request


def cancel_vacation_request(
    requests: list[VacationRequest],
    request_id: int,
) -> bool:
    """Найти заявку по id и отменить её."""
    for request in requests:
        if request.id == request_id:
            request.cancel()
            return True
    return False


def filter_requests_by_user(
    requests: list[VacationRequest],
    user: User,
) -> list[VacationRequest]:
    """Отобрать заявки конкретного пользователя."""
    return [request for request in requests if request.user.id == user.id]


def sort_requests_by_start(
    requests: list[VacationRequest],
) -> list[VacationRequest]:
    """Отсортировать заявки по дате начала."""
    return sorted(requests, key=lambda request: request.start_date)


def get_request_status(request: VacationRequest) -> str:
    """Текстовый статус заявки."""
    statuses = {
        "pending": "Ожидает согласования",
        "approved": "Согласована",
        "cancelled": "Отменена",
    }
    return statuses.get(request.status, "Неизвестный статус")


def show_vacation_requests(requests: list[VacationRequest]) -> None:
    """Вывести список заявок."""
    if not requests:
        print("Заявок нет.")
        return
    print(
        f"{'ID':<4}{'Пользователь':<25}{'Тип отпуска':<28}"
        f"{'Начало':<12}{'Конец':<12}{'Дней':<6}{'Статус'}"
    )
    print("-" * 105)
    for request in sort_requests_by_start(requests):
        print(
            f"{request.id:<4}{request.user.name:<25}"
            f"{request.vacation.name:<28}{request.start_date:<12}"
            f"{request.end_date:<12}{request.duration:<6}"
            f"{get_request_status(request)}"
        )
