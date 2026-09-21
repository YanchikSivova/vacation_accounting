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
        self.id = user_id
        self.name = name
        self.vacation_days_available = vacation_days_available
        self.vacation_days_total = vacation_days_total

    def reduce_days(self, duration: int) -> bool:
        """Списать дни отпуска. False, если дней недостаточно."""
        if self.vacation_days_available - duration < 0:
            return False
        self.vacation_days_available -= duration
        return True

    def restore_days(self, duration: int) -> None:
        """Вернуть дни при отмене заявки."""
        self.vacation_days_available += duration

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из данных JSON."""
        return cls(
            user_id=data["id"],
            name=data["name"],
            vacation_days_available=data["vacation_days_available"],
            vacation_days_total=data["vacation_days_total"],
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
