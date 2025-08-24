import os
import random
from datetime import datetime, timedelta
from typing import Literal


def generate_random_number_string(length: int) -> str:
    """
    Generate a random numeric string of the specified length.

    Args:
        length (int): The number of digits in the generated string.

    Returns:
        str: A randomly generated string of numbers with the given length.
    """
    if length <= 0:
        raise ValueError("Length must be a positive integer.")

    # Generate a string of random digits
    return ''.join(random.choice('0123456789') for _ in range(length))


def generate_legal_name() -> str:
    """
    Generate a random legal entity name.

    Returns:
        str: A randomly generated legal entity name.
    """
    name_key = 'Авто-тест' if os.getenv('IS_SUPPORT', 'false') == 'false' else 'Сапорт'
    return f'ТОВ "{name_key} {generate_random_number_string(8)}"'


def generate_ukrainian_name(name_type: Literal['last', 'first', 'second']) -> str:
    """
    Generate a random Ukrainian name based on the specified type.

    Args:
        name_type (Literal['last', 'first', 'second']): The type of name to generate.
            - 'first': Generates a first name.
            - 'second': Generates a middle name.
            - 'last': Generates a last name.

    Returns:
        str: A randomly generated Ukrainian name.
    """
    names = {
        'first': [
            "Андрій", "Богдан", "Володимир", "Дмитро", "Євген",
            "Іван", "Максим", "Олександр", "Сергій", "Тарас",
            "Павло", "Юрій", "Михайло", "Віталій", "Олег",
            "Захар", "Ростислав", "Арсен", "Артем", "Лев",
            "Святослав", "Роман", "Любомир", "Василь", "Микола",
            "Остап", "Григорій", "Назар", "Степан",
            "Ярослав", "Петро", "Антін", "Семен", "Вадим",
            "Кирило", "Тимофій", "Матвій", "Родіон", "Марко",
            "Леонід", "Єлисей", "Данило", "Гліб", "Ігор",
            "Всеволод", "Свирид", "Мирон", "Пилип", "Ілля",
            "Данило", "Артемій", "Тихон", "Денис", "Зіновій",
            "Юліан", "Василько", "Ярема", "Валентин", "Ігор"
        ],
        'last': [
            "Шевченко", "Іваненко", "Коваленко", "Тарасенко", "Петренко",
            "Данилюк", "Зінченко", "Литвин", "Савченко", "Мельник",
            "Гнатюк", "Ковальчук", "Романюк", "Бондаренко", "Федорчук",
            "Білоус", "Гаврилюк", "Лисенко", "Деркач", "Дорошенко",
            "Клименко", "Сидоренко", "Онищенко", "Мартиненко", "Остапчук",
            "Гуменюк", "Паламарчук", "Семенюк", "Вовк", "Рябоконь",
            "Дзюба", "Захарчук", "Лисиченко", "Чорний", "Цибулько",
            "Тимощук", "Юрчук", "Крамаренко", "Литвиненко", "Яковенко",
            "Зубенко", "Піддубний", "Король", "Тимошенко", "Кулик",
            "Хоменко", "Кисіль", "Лебідь", "Ткачук", "Дорош",
            "Дмитрук", "Москаленко", "Луценко", "Ніколайчук", "Зеленко",
            "Козаченко", "Логвиненко", "Божко", "Кравчук", "Павлюк",
            "Михайленко", "Степаненко", "Грицай", "Олійник", "Проценко",
            "Палій", "Скороход", "Тищенко", "Чередник", "Козак",
            "Богачук", "Герасименко", "Назаренко", "Яровий", "Чуб",
            "Тригуб", "Романенко", "Шпак", "Гречко", "Щербатий",
            "Демченко", "Заболотний", "Кириленко", "Левченко", "Мовчан",
            "Панченко", "Слободян", "Якименко", "Іщенко", "Шевчук"
        ]
    }

    if name_type == 'first':
        name_key = 'Авто' if os.getenv('IS_SUPPORT', 'false') == 'false' else 'Сапорт'
        return f'{name_key}-{random.choice(names["first"])}'
    elif name_type == 'second':
        return f'{random.choice(names["first"])}ич'
    else:
        name_key = 'тест' if os.getenv('IS_SUPPORT', 'false') == 'false' else 'сапорт'
        return f'{random.choice(names["last"])}-{name_key}'


def generate_random_email() -> str:
    """
    Generate a random email address.

    Returns:
        str: A randomly generated email address.
    """
    email_key = 'aqa' if os.getenv('IS_SUPPORT', 'false') == 'false' else 'support'
    return f"{email_key}_test_{generate_random_number_string(3)}@test.com"


def generate_random_phone_number() -> str:
    """
    Generate a random phone number in the format (0XX) XXX-XXXX.

    Returns:
        str: A randomly generated phone number.
    """
    return f"(0{generate_random_number_string(2)}) {generate_random_number_string(3)}-{generate_random_number_string(4)}"


def generate_birthday() -> str:
    """
    Generate a random birthday ensuring the person is at least 18 years old.

    Returns:
        str: A birthday in the format YYYY-MM-DD.
    """
    # Calculate the latest possible birthday for 18 years old
    max_date = datetime.now() - timedelta(days=18 * 365.25)
    # Calculate the earliest reasonable birthday (e.g., 100 years ago)
    min_date = max_date - timedelta(days=82 * 365.25)  # Assuming max age of 100
    # Generate a random date between min_date and max_date
    random_date = min_date + timedelta(days=random.randint(0, int((max_date - min_date).days)))
    # Return the date in the required format
    return random_date.strftime('%Y-%m-%d')


# Function to generate a random time
def generate_random_time() -> str:
    """
    Generate a random time in the format 'HH:MM'.

    Returns:
        str: A string representing the random time in 'HH:MM' format.
    """
    # Generate random hours (00 to 23) and minutes (00 to 59)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)

    # Format the hours and minutes as two digits each (e.g., 09:05, 15:30)
    return f"{hours:02}:{minutes:02}"
