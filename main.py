from tables_handler import InputConnect
from stat_handler import start
mode = input("Введите данные для печати: ")
if mode == "Вакансии и не чота":
    ic = InputConnect()
    ic.handle_vacancies()
elif mode == "Статистика":
    start()

