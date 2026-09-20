from users import create_user, find_user_by_name
from vacations import (
    create_vacation,
    cancel_vacation,
    get_vacation_status,
    filter_vacations_by_user,
    sort_vacations_by_start,
)
from storage import load_users, save_users, load_vacations, save_vacations
from utils import input_int, input_date, input_str

USERS_FILE = "data/users.json"
VACATIONS_FILE = "data/vacations.json"


def show_users(users: dict[int, dict]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Пользователей нет.")
        return
    print(f"{'ID':<4}{'Имя':<25}{'Доступно':<10}{'Всего':<10}")
    print("-" * 50)
    for u in users.values():
        print(
            f"{u['id']:<4}{u['name']:<25}"
            f"{u['vacation_days_available']:<10}{u['vacation_days_total']:<10}"
        )


def show_vacations(vacations: list[dict], users: dict[int, dict]) -> None:
    """Вывести список заявок."""
    if not vacations:
        print("Заявок нет.")
        return
    print(
        f"{'ID':<4}{'Пользователь':<25}{'Начало':<12}"
        f"{'Конец':<12}{'Дней':<6}{'Статус'}"
    )
    print("-" * 80)
    for v in sort_vacations_by_start(vacations):
        user = users.get(v["user_id"])
        user_name = user["name"] if user else f"id={v['user_id']}"
        print(
            f"{v['id']:<4}{user_name:<25}{v['start_date']:<12}"
            f"{v['end_date']:<12}{v['duration']:<6}{get_vacation_status(v)}"
        )


def menu() -> None:
    """Основной цикл меню."""
    users = load_users(USERS_FILE)
    vacations = load_vacations(VACATIONS_FILE)

    while True:
        print("\n=== Система учёта отпусков ===")
        print("1. Показать пользователей")
        print("2. Зарегистрировать пользователя")
        print("3. Найти пользователя по имени")
        print("4. Создать заявку на отпуск")
        print("5. Отменить заявку")
        print("6. Показать все заявки")
        print("7. Показать заявки пользователя")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_users(users)

        elif choice == "2":
            name = input_str("Имя пользователя: ")
            days = input_int("Доступных дней (по умолчанию 28): ")
            user = create_user(users, name, days)
            print(f"Создан пользователь {user['name']} (id={user['id']}).")
            save_users(USERS_FILE, users)

        elif choice == "3":
            query = input_str("Подстрока имени: ")
            found = find_user_by_name(users, query)
            if found:
                for u in found:
                    print(
                        f"id={u['id']}, {u['name']},"
                        f" доступно {u['vacation_days_available']}")
            else:
                print("Ничего не найдено.")

        elif choice == "4":
            show_users(users)
            user_id = input_int("ID пользователя: ")
            start = input_date("Дата начала (dd.mm.yyyy): ")
            end = input_date("Дата окончания (dd.mm.yyyy): ")
            ok, message = create_vacation(
                vacations, users, user_id, start, end)
            print(message)
            if ok:
                save_users(USERS_FILE, users)
                save_vacations(VACATIONS_FILE, vacations)

        elif choice == "5":
            show_vacations(vacations, users)
            vacation_id = input_int("ID заявки для отмены: ")
            ok, message = cancel_vacation(vacations, users, vacation_id)
            print(message)
            if ok:
                save_users(USERS_FILE, users)
                save_vacations(VACATIONS_FILE, vacations)

        elif choice == "6":
            show_vacations(vacations, users)

        elif choice == "7":
            user_id = input_int("ID пользователя: ")
            user_vacations = filter_vacations_by_user(vacations, user_id)
            show_vacations(user_vacations, users)

        elif choice == "0":
            save_users(USERS_FILE, users)
            save_vacations(VACATIONS_FILE, vacations)
            print("Данные сохранены. До свидания!")
            break

        else:
            print("Неизвестная команда.")


def main() -> None:
    """Точка входа в приложение."""
    menu()


if __name__ == "__main__":
    main()
