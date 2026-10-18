from models import VACATION_TYPES, User, VacationRequest
from models.users import (
    add_user,
    find_user_by_name,
    find_user_by_id,
    show_users
)
from models.vacations import (
    create_vacation_request,
    cancel_vacation_request,
    filter_requests_by_user,
    show_vacation_requests,
)
from storage import (
    load_users,
    save_users,
    load_vacation_requests,
    save_vacation_requests,
)
from utils import input_int, input_date, input_str

USERS_FILE = "data/users.json"
REQUESTS_FILE = "data/vacations.json"


def create_new_vacation(
    users: list[User],
    requests: list[VacationRequest],
) -> None:
    """Сценарий создания заявки на отпуск."""
    show_users(users)
    user_id = input_int("ID пользователя: ")
    user = find_user_by_id(users, user_id)
    if user is None:
        print("Ошибка: пользователь не найден.")
        return

    print("Типы отпуска:")
    for vacation in VACATION_TYPES:
        print(f"{vacation.id}. {vacation.name}")
    vacation_id = input_int("ID типа отпуска: ")
    vacation = next(
        (item for item in VACATION_TYPES if item.id == vacation_id),
        None,
    )
    if vacation is None:
        print("Ошибка: тип отпуска не найден.")
        return

    start = input_date("Дата начала (dd.mm.yyyy): ")
    end = input_date("Дата окончания (dd.mm.yyyy): ")

    request = create_vacation_request(requests, user, vacation, start, end)
    if request is None:
        return
    print(f"Заявка №{request.id} создана (ожидает согласования).")


def menu() -> None:
    """Основной цикл меню."""
    users = load_users(USERS_FILE)
    requests = load_vacation_requests(REQUESTS_FILE, users)

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
            while True:
                days = input_int("Доступных дней (от 0 до 28): ")
                if 0 <= days <= 28:
                    break
                print(
                    "Ошибка: количество доступных дней должно быть "
                    "от 0 до 28."
                )
            user = add_user(users, name, days)
            print(f"Создан пользователь {user.name} (id={user.id}).")
            save_users(USERS_FILE, users)

        elif choice == "3":
            query = input_str("Подстрока имени: ")
            found = find_user_by_name(users, query)
            if found:
                for u in found:
                    print(u)
            else:
                print("Ничего не найдено.")

        elif choice == "4":
            create_new_vacation(users, requests)
            save_users(USERS_FILE, users)
            save_vacation_requests(REQUESTS_FILE, requests)

        elif choice == "5":
            show_vacation_requests(requests)
            request_id = input_int("ID заявки для отмены: ")
            if cancel_vacation_request(requests, request_id):
                print(f"Заявка №{request_id} отменена.")
                save_users(USERS_FILE, users)
                save_vacation_requests(REQUESTS_FILE, requests)
            else:
                print(f"Заявка №{request_id} не найдена.")

        elif choice == "6":
            show_vacation_requests(requests)

        elif choice == "7":
            user_id = input_int("ID пользователя: ")
            user = find_user_by_id(users, user_id)
            if user is None:
                print("Пользователь не найден.")
                continue
            user_requests = filter_requests_by_user(requests, user)
            show_vacation_requests(user_requests)

        elif choice == "0":
            save_users(USERS_FILE, users)
            save_vacation_requests(REQUESTS_FILE, requests)
            print("Данные сохранены. До свидания!")
            break

        else:
            print("Неизвестная команда.")


def main() -> None:
    """Точка входа."""
    menu()


if __name__ == "__main__":
    main()
