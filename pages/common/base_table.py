from datetime import datetime
from typing import Literal, Union, Optional

from playwright.sync_api import Page

from pages.common.base_component import BaseComponent


class Column(BaseComponent):
    @property
    def title(self) -> str:
        """
        Get the title of the column.
        :return: str
        """
        return self.child_el('//p').text

    @property
    def sorted_by(self) -> str:
        """
        Get the way in which the current column has been sorted. None if not sorted
        :return: str
        """
        return self.element.get_attribute('aria-sort')

    def sort(self, sort_way: Literal['asc', 'desc'], wait: bool = True) -> None:
        """
        Sort the table by the current column.
        """
        for _ in range(3):
            if self.sorted_by == sort_way:
                break
            else:
                self.child_el('//span').click()
                self.wait_for_page_load()
                if wait:
                    self.child_el('//ancestor::table//tbody/tr/td').raw.nth(0).wait_for(state="visible")

    @property
    def values(self) -> list[str]:
        """
        Get a list of values in the current column.
        :return: List[str]
        """
        data_key = self.element.get_attribute('data-xpath').removeprefix('tableHeadCell-').removeprefix(
            'tableTailCell-')
        loc = f'//ancestor::table//tbody/tr/td[@id="{data_key}"]'
        return [element.text for element in self.child_elements(loc)]

    def get_sorted_column_with_integers(self, reverse: bool = False) -> list[str]:
        """
        Sorts a list of strings containing integers at the beginning based on the integer values (ex. "30 days").
        """

        def extract_integer(value: str) -> Union[int, float]:
            """
            Extracts the integer value from a string.
            """
            try:
                first_part = value.split()[0]
                return int(first_part)
            except ValueError:
                # float('inf') represents positive infinity in Python, a value that's larger than any finite number.
                return float('inf')

        return sorted(self.values, key=extract_integer, reverse=reverse)

    def get_sorted_column_with_dates(self, reverse: bool = False, date_format: str = '%d %b %Y') -> list[str]:
        """
         Sorts a list of date strings in the format "10 May 2024" based on date values.

         Example:
             dates = ['10 May 2024', '15 April 2023', '5 June 2025']
             sorted_dates = get_sorted_dates(dates)
             # sorted_dates will be ['15 April 2023', '10 May 2024', '5 June 2025']
         """

        def parse_date(date_str: str) -> datetime:
            """
            Parses a date string in the "10 May 2024" format into a datetime object.
            """
            return datetime.strptime(date_str.replace("Sept", "Sep", 1), date_format)

        # Check if the first element contains a newline character
        has_email = '\n' in self.values[0]

        if has_email:
            # Split each row into date and email parts (if email part exists)
            date_email_pairs = [(row.split('\n')[0], row.split('\n')[1] if '\n' in row else '') for row in self.values]

            # Sort based on the date part while ignoring the email part
            sorted_date_email_pairs = sorted(date_email_pairs, key=lambda pair: parse_date(pair[0]), reverse=reverse)

            # Join the sorted pairs back into rows
            sorted_rows = [f"{pair[0]}\n{pair[1]}" if pair[1] else pair[0] for pair in sorted_date_email_pairs]
        else:
            # If there are no email addresses, sort directly based on the date part
            sorted_rows = sorted(self.values, key=parse_date, reverse=reverse)

        return sorted_rows


class BaseRow(BaseComponent):
    selector = '//tr[not(contains(@class,"-head"))]'

    @property
    def row_key(self) -> str:
        """
        Get the unique attribute of the table row.
        :return: str
        """
        return self.element.get_attribute('data-xpath')


class BaseTable(BaseComponent):
    def __init__(self, label: str, page: Page, selector: Optional[str] = None):
        if not selector:
            selector = f'//span[contains(text(),"{label}")]/..//table'
        super().__init__(page.locator(selector), page)

    @property
    def columns(self) -> list[Column]:
        """
        Get a list of table columns (objects).
        :return: List[Column]
        """
        self.wait_for_loader()
        return self.get_list_of_components('//th', Column)

    @property
    def rows(self) -> list[BaseRow]:
        """
        Get a list of table rows (objects).
        :return: List[BaseRow]
        """
        self.wait_for_loader()
        return self.get_list_of_components(BaseRow.selector, BaseRow)

    @staticmethod
    def compare_lists(actual_list: list, expected_list: list) -> None:
        """
        Compare two lists and raise an assertion error if they are not equal.
        :param actual_list: list
        :param expected_list: list
        """
        if actual_list and expected_list:
            assert actual_list == expected_list, f'actual list = {actual_list}, expected list = {expected_list}'
        else:
            raise ValueError('Comparing lists are empty')

    def wait_for_table(self) -> None:
        self.child_el('//tbody/tr/td').raw.nth(0).wait_for(state='visible')
