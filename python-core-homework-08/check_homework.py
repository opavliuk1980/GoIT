"""
==============================================================================
Цей файл є тестом домашнього завдання.
Будь ласка, НЕ вносьте зміни до цього файлу без попереднього узгодження з ментором.
==============================================================================
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from main import get_birthdays_per_week

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"


class CustomTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write(f"{GREEN} {test.shortDescription()} {RESET}\n")

    def addFailure(self, test, err):
        self.failures.append((test, str(err[1])))
        self._mirrorOutput = True
        self.stream.write(f"{RED} {str(err[1])} {RESET}\n")

    def printErrors(self):
        if self.errors:
            print(
                f"{RED}Ваш код викликає помилки при виконанні тесту. Перевірте чи ви виконали імпорт 'from datetime import date'{RESET}"
            )
            self.printErrorList("ERROR:", self.errors)
        self.stream.write(f"\nВсього пройдено {self.testsRun} тестів.\n")
        failed, errored = len(self.failures), len(self.errors)
        if failed:
            self.stream.write(f"{RED}Провалених тестів: {failed} {RESET}\n")
        if errored:
            self.stream.write(
                f"{RED} Помилок при виконанні тестів: {errored} {RESET}\n"
            )

    def getDescription(self, test):
        return ""


class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult


class TestGetBirthdaysPerWeek(unittest.TestCase):
    def setUp(self):
        self.today = datetime(2023, 12, 26)

    @patch("main.date")
    def test_all_past_birthdays_this_year(self, date_mock):
        """
        1. Успішно пройдено тест коли всі дні народження користувачів вже минули у цьому році
        """
        date_mock.today.return_value = self.today.date()
        users = [
            {"name": "John", "birthday": (self.today - timedelta(days=10)).date()},
            {"name": "Doe", "birthday": (self.today - timedelta(days=20)).date()},
        ]
        result = get_birthdays_per_week(users)
        expected = {}
        assert (
            result == expected
        ), """1. Провалено тест коли всі дні народження користувачів вже минули у цьому році. Функція повинна повертати пустий словник"""

    @patch("main.date")
    def test_empty_users(self, date_mock):
        """
        2. Успішно пройдено тест коли у функцію передали пустий список користувачів
        """
        date_mock.today.return_value = self.today.date()
        users = []
        result = get_birthdays_per_week(users)
        expected = {}
        assert (
            result == expected
        ), """2. Провалено тест коли у функцію передали пустий список користувачів. Функція повинна повертати пустий словник"""

    @patch("main.date")
    def test_weekend_birthdays(self, date_mock):
        """
        5. Успішно пройдено тест коли функція повернула правильний список днів народження користувачів, причому деякі припадають на вихідні
        """
        date_mock.today.return_value = self.today.date()
        users = [
            {
                "name": "John",
                "birthday": (self.today + timedelta(days=5)).date(),
            },
            {
                "name": "Doe",
                "birthday": (self.today + timedelta(days=6)).date(),
            },
            {"name": "Alice", "birthday": (self.today + timedelta(days=3)).date()},
        ]
        result = get_birthdays_per_week(users)
        expected = {"Monday": ["John", "Doe"], "Friday": ["Alice"]}
        assert (
            result == expected
        ), "5. Провалено тест коли дні народження деяких користувачів випадають на вихідні. Функція повернула не правильний словник"

    @patch("main.date")
    def test_past_birthdays_next_week(self, date_mock):
        """
        4. Успішно пройдено тест коли функція повернула правильний список днів народження користувачів, де деякі дні народження вже минули в цьому році, але вони будуть на наступному тижні
        """
        date_mock.today.return_value = self.today.date()
        users = [
            {
                "name": "John",
                "birthday": (self.today + timedelta(days=-5)).date(),
            },
            {
                "name": "Doe",
                "birthday": (self.today + timedelta(days=-6)).date(),
            },
            {
                "name": "Alice",
                "birthday": (datetime(2021, 1, 1)).date(),
            },
        ]
        result = get_birthdays_per_week(users)
        expected = {
            "Monday": ["Alice"],
        }
        assert (
            result == expected
        ), """4. Провалено тест бо функція повернула не правильний список днів народження користувачів, де деякі вже минули в цьому році, але вони будуть на наступному тижні"""

    @patch("main.date")
    def test_future_birthdays(self, date_mock):
        """
        3. Успішно пройдено тест коли функція повернула правильний список днів народження користувачів які не припадають на вихідні
        """

        date_mock.today.return_value = self.today.date()
        users = [
            {
                "name": "John",
                "birthday": (self.today + timedelta(days=1)).date(),
            },
            {
                "name": "Doe",
                "birthday": (self.today + timedelta(days=3)).date(),
            },
            {"name": "Alice", "birthday": (self.today + timedelta(days=-3)).date()},
        ]
        result = get_birthdays_per_week(users)
        expected = {"Wednesday": ["John"], "Friday": ["Doe"]}
        assert (
            result == expected
        ), """3. Провалено тест бо функція повернула не правильний список днів народження користувачів які є у майбутньому та вони не припадають на вихідні"""


if __name__ == "__main__":
    runner = CustomTestRunner(verbosity=0)
    unittest.main(testRunner=runner)