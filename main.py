from datetime import date
from datetime import datetime

# Пользователь
name = 'Сивова Яна'
vacation_days_available = 28

# Даты отпуска
start_date, end_date = date.today(), date.today()

# Статус заявки
pplication_status = ''

# Регистрация пользователя


def create_user(name, days_available=28):
    return name, days_available

# Уменьшение количества дней доступных для отпуска


def reduce_vacation_days_available(vacation_duration):
    global vacation_days_available
    if vacation_days_available - vacation_duration < 0:
        return False
    else:
        vacation_days_available -= vacation_duration
        return True


# Создание заявки
def create_vacation_application(inner_start_date, inner_end_date):
    global application_status, start_date, end_date
    duration = (inner_end_date - inner_start_date).days
    if duration <= 0:
        return False, 'Ошибка! Миинимальная длина отпуска 1 день.'
    if duration > vacation_days_available:
        return False, f'Ошибка! Доступное количество дней {vacation_days_available}'

    ok = reduce_vacation_days_available(duration)
    if not (ok):
        return False, 'Ошибка!'
    start_date = inner_start_date
    end_date = inner_end_date
    application_status = 'pending'
    return True, 'Заявка создана!'

# Проверка статуса заявки


def check_application_status():
    return application_status


print("=== Сервис учета отпусков ===")
print()

# Тест функции регистрация пользователя
print('Регистрация пользователя в системе')
input_name = input("Введите имя пользователя: ")
input_vacation_days_available = int(
    input("Введите количество доступных дней для отпуска: "))
user_name, vacation_days_available = create_user(
    input_name, input_vacation_days_available)
print(
    f'Зарегистрирован пользователь {user_name}. Доступных дней для отпуска {vacation_days_available}')
print()

# Тест функции создания заявки на отпуск
print('Создание заявки на отпуск')
input_start_date = input(
    "Введите дату начала планируемого отпуска (dd.mm.yyyy): ")
input_end_date = input(
    "Введите дату окончания планируемого отпуска (dd.mm.yyyy): ")
start = datetime.strptime(input_start_date, "%d.%m.%Y").date()
end = datetime.strptime(input_end_date, "%d.%m.%Y").date()
ok, message = create_vacation_application(start, end)
print(message)
print()

# Тест функции проверки статуса заявки
print('Проверка статуса заявки')
print(f'Статус заявки: {check_application_status()}')
