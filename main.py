from models import User, Vacation
from models.users import (
    add_user,
    find_user_by_name,
    find_user_by_id,
    show_users
)
from models.vacations import (
    create_vacation,
    cancel_vacation,
    filter_vacations_by_user,
    show_vacations,
)
from storage import (
    load_users,
    save_users,
    load_vacations,
    save_vacations,
)
from utils import input_int, input_date, input_str

USERS_FILE = "data/users.json"
VACATIONS_FILE = "data/vacations.json"


def create_new_vacation(
    users: list[User],
    vacations: list[Vacation],
) -> None:
    """Сценарий создания заявки на отпуск."""
    show_users(users)
    user_id = input_int("ID пользователя: ")
    user = find_user_by_id(users, user_id)
    if user is None:
        print("Ошибка: пользователь не найден.")
        return

    start = input_date("Дата начала (dd.mm.yyyy): ")
    end = input_date("Дата окончания (dd.mm.yyyy): ")

    vacation = create_vacation(vacations, user, start, end)
    if vacation is None:
        return
    print(f"Заявка №{vacation.id} создана (ожидает согласования).")


def menu() -> None:
    """Основной цикл меню."""
    users = load_users(USERS_FILE)
    vacations = load_vacations(VACATIONS_FILE, users)

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
            create_new_vacation(users, vacations)
            save_users(USERS_FILE, users)
            save_vacations(VACATIONS_FILE, vacations)

        elif choice == "5":
            show_vacations(vacations)
            vacation_id = input_int("ID заявки для отмены: ")
            if cancel_vacation(vacations, vacation_id):
                print(f"Заявка №{vacation_id} отменена.")
                save_users(USERS_FILE, users)
                save_vacations(VACATIONS_FILE, vacations)
            else:
                print(f"Заявка №{vacation_id} не найдена.")

        elif choice == "6":
            show_vacations(vacations)

        elif choice == "7":
            user_id = input_int("ID пользователя: ")
            user = find_user_by_id(users, user_id)
            if user is None:
                print("Пользователь не найден.")
                continue
            user_vacations = filter_vacations_by_user(vacations, user)
            show_vacations(user_vacations)

        elif choice == "0":
            save_users(USERS_FILE, users)
            save_vacations(VACATIONS_FILE, vacations)
            print("Данные сохранены. До свидания!")
            break

        else:
            print("Неизвестная команда.")


def main() -> None:
    """Точка входа."""
    menu()


if __name__ == "__main__":
    main()
