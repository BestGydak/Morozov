import csv
import re

import prettytable

from prettytable import PrettyTable

from datetime import datetime


def format_date(text):
    date = datetime.strptime(text[:10], "%Y-%M-%d")
    return date.strftime("%d.%M.%Y")


def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return False
    return True


def format_number(number):
    return '{:,d}'.format(int(float(number))).replace(',', ' ')


def formatdesc(text):
    newtext = text.replace(" ", " ").replace(" ", " ").replace("&qout", " ")
    newtext = re.sub("<.*?>", '', newtext)
    newtext = re.sub(" +", " ", newtext)
    newtext = newtext.strip()

    return newtext


def rename_to_rus(text):
    rus_dict = {"noExperience": "Нет опыта",
                "between1And3": "От 1 года до 3 лет",
                "between3And6": "От 3 до 6 лет",
                "moreThan6": "Более 6 лет",
                "AZN": "Манаты",
                "BYR": "Белорусские рубли",
                "EUR": "Евро",
                "GEL": "Грузинский лари",
                "KGS": "Киргизский сом",
                "KZT": "Тенге",
                "RUR": "Рубли",
                "UAH": "Гривны",
                "USD": "Доллары",
                "UZS": "Узбекский сум",
                "False": "Нет",
                "True": "Да"}
    if text in rus_dict.keys():
        return rus_dict[text]
    return text


def format_gross(text):
    if text == "False":
        return "С вычетом налогов"

    return "Без вычета налогов"


def print_vacancies(data_vacancies, dic_naming):
    for vacancy in data_vacancies:
        for key in vacancy.keys():
            print(f"{dic_naming[key]}: {rename_to_rus(vacancy[key])}")
        print()


def shorten_description(text):
    if len(text) > 100:
        return text[:100] + "..."
    return text


def skill_parser(text):
    if '\n' in text:
        return text
    return text.replace(", ", "\n").replace(',', '\n')


class DataSet:

    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies_objects = self.csv_reader()

    def csv_reader(self):
        vacancies = []
        error_code = 0
        titles = []
        with open(self.file_name, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            is_first = True
            for line in reader:
                error_code = 1
                if is_first:
                    titles = line
                    is_first = False
                    continue
                error_code = 2
                if len(line) == len(titles) and "" not in line:
                    vacancies.append(line)
        if error_code == 1:
            print("Нет данных")
            exit()
        if error_code == 0:
            print("Пустой файл")
            exit()
        return self.csv_filer(vacancies, titles)

    def csv_filer(self, reader, list_naming):
        vacancies_dicts = []
        for vacancy_data in reader:
            new_vacancy = Vacancy(formatdesc(vacancy_data[list_naming.index('name')]),
                                  formatdesc(vacancy_data[list_naming.index('description')]),
                                  formatdesc(vacancy_data[list_naming.index('key_skills')]).split('\n'),
                                  formatdesc(vacancy_data[list_naming.index('experience_id')]),
                                  formatdesc(vacancy_data[list_naming.index('premium')]),
                                  formatdesc(vacancy_data[list_naming.index('employer_name')]),
                                  formatdesc(vacancy_data[list_naming.index('salary_from')]),
                                  formatdesc(vacancy_data[list_naming.index('salary_to')]),
                                  formatdesc(vacancy_data[list_naming.index('salary_gross')]),
                                  formatdesc(vacancy_data[list_naming.index('salary_currency')]),
                                  formatdesc(vacancy_data[list_naming.index('area_name')]),
                                  vacancy_data[list_naming.index('published_at')])
            vacancies_dicts.append(new_vacancy)
        return vacancies_dicts


class Vacancy:
    def __init__(self, name, description, key_skills, experience_id,
                 premium, employer_name, salary_from, salary_to, salary_gross, salary_currency, area_name,
                 published_at):
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = Salary(salary_from, salary_to, salary_gross, salary_currency)
        self.area_name = area_name
        self.published_at = published_at


class Salary:
    currency_to_rub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }

    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = float(salary_from)
        self.salary_to = float(salary_to)
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def get_value_in_rub_to(self):
        return Salary.currency_to_rub[self.salary_currency] * self.salary_to

    def get_value_in_rub_from(self):
        return Salary.currency_to_rub[self.salary_currency] * self.salary_from


class InputConnect:
    def create_table(self, vacancies, vac_filter, args):
        table = PrettyTable()
        table.align = 'l'
        table.hrules = prettytable.ALL
        table.field_names = ['№', "Название", "Описание", "Навыки", "Опыт работы", "Премиум-вакансия", "Компания",
                             "Оклад", "Название региона", "Дата публикации вакансии"]
        table.max_width = 20
        vacancies_present = False
        index = 0
        for vacancy_pack in enumerate(vacancies):
            vacancy = vacancy_pack[1]
            if not vac_filter(vacancy):
                continue
            vacancies_present = True
            new_row = [index + 1,
                       shorten_description(vacancy.name),
                       shorten_description(vacancy.description),
                       shorten_description("\n".join(vacancy.key_skills)),
                       shorten_description(rename_to_rus(vacancy.experience_id)),
                       shorten_description(rename_to_rus(vacancy.premium)),
                       shorten_description(vacancy.employer_name),
                       f"{format_number(vacancy.salary.salary_from)} - {format_number(vacancy.salary.salary_to)} "
                       f"({rename_to_rus(vacancy.salary.salary_currency)}) ({format_gross(vacancy.salary.salary_gross)})",
                       shorten_description(rename_to_rus(vacancy.area_name)),
                       shorten_description(format_date(vacancy.published_at))]
            table.add_row(new_row)
            index += 1
        if not vacancies_present:
            print('Ничего не найдено')
            exit()
        if len(args) == 0:
            print(table.get_string())
        else:
            if not (args.get("fields") is None):
                args["fields"].insert(0, "№")
            print(table.get_string(**args))

    def create_filter(self, string):
        if len(string) == 0:
            def always_true(vac):
                return True

            return always_true
        if not (":" in string):
            print("Формат ввода некорректен")
            exit()
        string_statement, string_parameter = string.split(": ")

        if string_statement == "Навыки":
            parameters = string_parameter.split(", ")

            def check_statement(vac):
                skills = vac.key_skills
                for req_skill in parameters:
                    if not (req_skill in skills):
                        return False
                return True

            return check_statement

        elif string_statement == "Идентификатор валюты оклада":
            def check_statement(vac):
                return rename_to_rus(vac.salary.salary_currency) == string_parameter

            return check_statement

        elif string_statement == "Оклад":
            value = int(string_parameter)

            def check_statement(vac):
                return float(vac.salary.salary_from) <= value <= float(vac.salary.salary_to)

            return check_statement

        elif string_statement == "Название":
            name = string_parameter

            def check_statement(vac):
                return vac.name == name

            return check_statement

        elif string_statement == "Описание":
            name = string_parameter

            def check_statement(vac):
                return vac.description == name

            return check_statement

        elif string_statement == "Компания":
            name = string_parameter

            def check_statement(vac):
                return vac.employer_name == name

            return check_statement

        elif string_statement == "Дата публикации вакансии":
            data = string_parameter

            def check_statement(vac):
                return format_date(vac.published_at) == data

            return check_statement

        elif string_statement == "Опыт работы":
            experience = string_parameter
            experience_conversion = {
                "noExperience": "Нет опыта",
                "between1And3": "От 1 года до 3 лет",
                "between3And6": "От 3 до 6 лет",
                "moreThan6": "Более 6 лет"
            }

            def check_statement(vac):
                return experience_conversion[vac.experience_id] == experience

            return check_statement

        elif string_statement == "Премиум-вакансия":
            premium = string_parameter

            def check_statement(vac):
                return rename_to_rus(vac.premium) == premium

            return check_statement
        elif string_statement == "Название региона":
            def check_statement(vac):
                return vac.area_name == string_parameter

            return check_statement
        print('Параметр поиска некорректен')
        exit()

    def create_sorting_key(self, inp):
        if inp == "Название":
            def sorting_key(vacancy):
                return vacancy.name

            return sorting_key, True
        if inp == "Описание":
            def sorting_key(vacancy):
                return vacancy.description

            return sorting_key, True
        if inp == "Навыки":
            def sorting_key(vacancy):
                return len(vacancy.key_skills)

            return sorting_key, True
        if inp == "Опыт работы":
            def sorting_key(vacancy):
                if vacancy.experience_id == 'noExperience':
                    return 0
                if vacancy.experience_id == 'between1And3':
                    return 1
                if vacancy.experience_id == 'between3And6':
                    return 2
                if vacancy.experience_id == 'moreThan6':
                    return 3

            return sorting_key, True
        if inp == "Премиум-вакансия":
            def sorting_key(vacancy):
                if rename_to_rus(vacancy.premium) == "Нет":
                    return 0
                return 1

            return sorting_key, True
        if inp == "Компания":
            def sorting_key(vacancy):
                return vacancy.employer_name

            return sorting_key, True
        if inp == "Оклад":
            def sorting_key(vacancy):
                return (vacancy.salary.get_value_in_rub_to() + vacancy.salary.get_value_in_rub_from()) / 2

            return sorting_key, True
        if inp == "Название региона":
            def sorting_key(vacancy):
                return vacancy.area_name

            return sorting_key, True
        if inp == "Дата публикации вакансии":
            def sorting_key(vacancy):
                return datetime.strptime(vacancy.published_at, "%Y-%m-%dT%H:%M:%S%z")

            return sorting_key, True
        return lambda x: x, False

    def handle_vacancies(self):
        file_name = input("Введите название файла: ")
        filter_parameter = input("Введите параметр фильтрации: ")
        sort_parameter = input("Введите параметр сортировки: ")
        is_inverted_str = input("Обратный порядок сортировки (Да / Нет): ")
        ids = list(map(int, input("Введите диапазон вывода: ").split()))
        arguments = dict()
        if len(ids) > 0:
            arguments["start"] = ids[0] - 1
            if len(ids) == 2:
                arguments["end"] = ids[1] - 1
        column_list = input("Введите требуемые столбцы: ").split(", ")
        new_filter = self.create_filter(filter_parameter)
        if len(column_list) > 0 and not (len(column_list) == 1 and column_list[0] == ''):
            arguments["fields"] = column_list
        is_reversed = False
        if is_inverted_str == "Да":
            is_reversed = True
        elif is_inverted_str == "Нет":
            is_reversed = False
        elif is_inverted_str != "":
            print("Порядок сортировки задан некорректно")
            exit()

        sorting_key, is_key_created = self.create_sorting_key(sort_parameter)
        if not is_key_created and sort_parameter != '':
            print("Параметр сортировки некорректен")
            exit()

        data = DataSet(file_name)
        vacancies = data.vacancies_objects
        if is_key_created:
            vacancies.sort(key=sorting_key, reverse=is_reversed)

        return self.create_table(vacancies, new_filter, arguments)

