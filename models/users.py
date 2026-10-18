MAX_VACATION_DAYS = 28


class User:
    """Пользователь системы учёта отпусков."""

    def __init__(
        self,
        user_id: int,
        name: str,
        vacation_days_available: int = 28,
        vacation_days_total: int = 28,
    ) -> None:
        """Создать объект пользователя."""
        if not 0 <= vacation_days_total <= MAX_VACATION_DAYS:
            raise ValueError(
                f"Общее количество дней должно быть от 0 до "
                f"{MAX_VACATION_DAYS}."
            )
        self.id = user_id
        self.name = name
        self.vacation_days_total = vacation_days_total
        self.vacation_days_available = vacation_days_available

    @property
    def vacation_days_available(self) -> int:
        return self._vacation_days_available

    @vacation_days_available.setter
    def vacation_days_available(self, days: int) -> None:
        if not 0 <= days <= min(self.vacation_days_total, MAX_VACATION_DAYS):
            raise ValueError(
                f"Доступное количество дней должно быть от 0 до "
                f"{min(self.vacation_days_total, MAX_VACATION_DAYS)}."
            )
        self._vacation_days_available = days

    def reduce_days(self, duration: int) -> bool:
        """Списать дни отпуска. False, если дней недостаточно."""
        if duration <= 0:
            return False
        if self.vacation_days_available - duration < 0:
            return False
        self.vacation_days_available -= duration
        return True

    def restore_days(self, duration: int) -> None:
        """Вернуть дни при отмене заявки."""
        if duration <= 0:
            raise ValueError(
                "Количество возвращаемых дней должно быть больше 0."
            )
        self.vacation_days_available = min(
            self.vacation_days_available + duration,
            self.vacation_days_total,
            MAX_VACATION_DAYS,
        )

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из данных JSON."""
        total_days = min(
            max(data["vacation_days_total"], 0),
            MAX_VACATION_DAYS,
        )
        available_days = min(
            max(data["vacation_days_available"], 0),
            total_days,
        )
        return cls(
            user_id=data["id"],
            name=data["name"],
            vacation_days_available=available_days,
            vacation_days_total=total_days,
        )

    def to_dict(self) -> dict:
        """Преобразовать объект в словарь для JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "vacation_days_available": self.vacation_days_available,
            "vacation_days_total": self.vacation_days_total,
        }

    def __str__(self) -> str:
        """Строковое представление пользователя."""
        return (
            f"{self.name} (id={self.id}), "
            f"доступно {self.vacation_days_available} из"
            f" {self.vacation_days_total} дней"
        )


# ---------- функции работы с коллекцией пользователей ----------

def add_user(users: list[User], name: str, days: int = 28) -> User:
    """Создать пользователя и добавить его в коллекцию."""
    new_id = max((u.id for u in users), default=0) + 1
    user = User(new_id, name, days, days)
    users.append(user)
    return user


def find_user_by_name(users: list[User], query: str) -> list[User]:
    """Найти пользователей по подстроке имени."""
    q = query.lower()
    return [u for u in users if q in u.name.lower()]


def find_user_by_id(users: list[User], user_id: int) -> User | None:
    """Найти пользователя по id (нужно для загрузки бронирований из JSON)."""
    for u in users:
        if u.id == user_id:
            return u
    return None


def show_users(users: list[User]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Пользователей нет.")
        return
    print(f"{'ID':<4}{'Имя':<25}{'Доступно':<10}{'Всего':<10}")
    print("-" * 50)
    for u in users:
        print(
            f"{u.id:<4}{u.name:<25}"
            f"{u.vacation_days_available:<10}{u.vacation_days_total:<10}"
        )
