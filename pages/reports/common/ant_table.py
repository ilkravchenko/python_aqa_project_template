import time
from datetime import datetime
from typing import Literal, Union, Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement
from pages.common.dropdown import BaseDropdown
from pages.reports.common.ant_dropdown import AntDropdown


class AntPaginationComponent(BaseComponent):
    """
    A class to represent the pagination controls in an Ant Design table.

    This component interacts with Ant Design's pagination elements, such as:
    - Navigating between pages (next, previous, specific page numbers)
    - Setting the number of rows per page

    Attributes:
        selector (str): The CSS selector used to locate the pagination toolbar.
    """
    selector = '//div[@class="paginator-container"]'

    def __init__(self, page: Page, selector: str = selector, root: Optional[Locator] = None):
        """
        Initialize the PaginationComponent.

        Args:
            page (Page): The Playwright page object.
            selector (str): The selector for the pagination toolbar.
        """
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def current_page(self) -> str:
        """
        Get the current active page number.

        Returns:
            str: The current page number.
        """
        return self.child_el('//li[contains(@class, "ant-pagination-item-active")]/a').text

    @property
    def total_pages(self) -> int:
        """
        Get the total number of pages in the pagination.

        Returns:
            int: Total number of pages.
        """
        pages = self.child_elements('//li[contains(@class, "ant-pagination-item")]/a')
        return len(pages)

    @property
    def next_page_button(self) -> BaseElement:
        """
        Get the next page button element.

        Returns:
            Locator: The Playwright element representing the next page button.
        """
        return self.child_el('//li[contains(@class, "ant-pagination-next")]/button')

    @property
    def previous_page_button(self) -> BaseElement:
        """
        Get the previous page button element.

        Returns:
            Locator: The Playwright element representing the previous page button.
        """
        return self.child_el('//li[contains(@class, "ant-pagination-prev")]/button')

    @property
    def first_page_button(self) -> BaseElement:
        """
        Get the first page button element.

        Returns:
            Locator: The Playwright element representing the first page button.
        """
        return self.child_el('//li[contains(@class, "ant-pagination-item-1")]/a')

    @property
    def last_page_button(self) -> BaseElement:
        """
        Get the last page button element.

        Returns:
            Locator: The Playwright element representing the last page button.
        """
        return self.child_elements('//li[contains(@class, "ant-pagination-item")]/a')[-1]

    @property
    def rows_limit_dropdown(self) -> AntDropdown:
        """
        Get the dropdown element for setting the number of rows per page.

        Returns:
            BaseDropdown: The dropdown element that controls the number of rows per page.
        """
        return self.child_el(selector='//div[contains(@class, "ant-pagination-options-size-changer")]',
                             component=AntDropdown, label='pagination')

    def go_to_page(self, page_number: int) -> None:
        """
        Navigate to a specific page.

        Args:
            page_number (int): The page number to go to.
        """
        page_locator = f'//li[contains(@class, "ant-pagination-item-{page_number}")]/a'
        self.child_el(page_locator).click()
        self.wait_for_page_load()

    def go_to_next_page(self) -> None:
        """
        Click the next page button to navigate forward.
        """
        if not self.next_page_button.get_attribute("aria-disabled"):
            self.next_page_button.click()
            self.wait_for_page_load()

    def go_to_previous_page(self) -> None:
        """
        Click the previous page button to navigate backward.
        """
        if not self.previous_page_button.get_attribute("aria-disabled"):
            self.previous_page_button.click()
            self.wait_for_page_load()

    def set_limit(self, limit: Literal['10', '20', '50', '100']) -> None:
        """
        Set the number of rows per page.

        Args:
            limit (Literal['10', '20', '50', '100']): The number of rows per page.
        """
        self.rows_limit_dropdown.select_option(f'{limit} / page')

        # Wait for the page to load after changing the row limit
        self.wait_for_page_load()
        self.page.wait_for_load_state(state='domcontentloaded')

        for _ in range(10):
            if self.rows_limit_dropdown.selected_value == f'{limit} / page':
                break
            time.sleep(0.1)
            self.wait_for_page_load()

        time.sleep(0.1)


class AntColumn(BaseComponent):
    """
    Represents a column in an Ant Design table.
    """

    def __init__(self, page: Page, locator: Locator, index: int):
        super().__init__(locator, page)
        self.index = index + 1

    @property
    def title(self) -> str:
        """
        Get the title of the column.
        :return: str
        """
        return self.element.text

    @property
    def is_sortable(self) -> bool:
        """
        Check if the column has sorting functionality.

        Returns:
            bool: True if sortable, False otherwise.
        """
        return "ant-table-column-has-sorters" in self.element.get_attribute("class")

    @property
    def sorted_by(self) -> Optional[str]:
        """
        Get the sorting order of the current column.

        Returns:
            Optional[str]: 'asc' if sorted ascending, 'desc' if sorted descending, None if not sorted.
        """
        if not self.is_sortable:
            return None

        up_arrow = self.child_el('//span[contains(@class, "ant-table-column-sorter-up")]')
        down_arrow = self.child_el('//span[contains(@class, "ant-table-column-sorter-down")]')

        if "active" in down_arrow.get_attribute("class"):
            return "desc"
        elif "active" in up_arrow.get_attribute("class"):
            return "asc"
        return None

    def sort(self, sort_way: Literal["asc", "desc"], wait: bool = True) -> None:
        """
        Sort the table by clicking the appropriate sorting arrow.

        Args:
            sort_way (Literal["asc", "desc"]): The desired sorting order.
            wait (bool, optional): Whether to wait for sorting to take effect. Defaults to True.
        """
        if not self.is_sortable:
            raise ValueError("This column is not sortable.")

        for _ in range(3):
            current_sort = self.sorted_by

            if current_sort == sort_way:
                break  # Correct sorting applied
            else:
                self.element.click()
                self.wait_for_page_load()

                if wait:
                    self.child_el('//ancestor::table//tr[1]/td').raw.nth(0).wait_for(state="visible")

    @property
    def values(self) -> list[str]:
        """
        Get a list of values in the current column.
        :return: List[str]
        """
        loc = f'//ancestor::table//tbody//td[{self.index}]'
        return [element.text for element in self.child_elements(loc) if element.text]

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
                return float('inf')  # Positive infinity as a fallback

        return sorted(self.values, key=extract_integer, reverse=reverse)

    def get_sorted_column_with_dates(self, reverse: bool = False, date_format: str = '%d %b %Y') -> list[str]:
        """
        Sorts a list of date strings in the format "10 May 2024" based on date values.
        """

        def parse_date(date_str: str) -> datetime:
            """
            Parses a date string in the given format into a datetime object.
            """
            return datetime.strptime(date_str.replace("Sept", "Sep", 1), date_format)

        has_email = '\n' in self.values[0]

        if has_email:
            date_email_pairs = [(row.split('\n')[0], row.split('\n')[1] if '\n' in row else '') for row in self.values]
            sorted_date_email_pairs = sorted(date_email_pairs, key=lambda pair: parse_date(pair[0]), reverse=reverse)
            sorted_rows = [f"{pair[0]}\n{pair[1]}" if pair[1] else pair[0] for pair in sorted_date_email_pairs]
        else:
            sorted_rows = sorted(self.values, key=parse_date, reverse=reverse)

        return sorted_rows


class AntRow(BaseComponent):
    """
    Represents a row in an Ant Design table.
    """
    selector = '//tbody//tr'

    @property
    def row_key(self) -> str:
        """
        Get the unique attribute of the table row.
        :return: str
        """
        return self.element.get_attribute('data-row-key')


class AntTable(BaseComponent):
    """
    Represents an Ant Design table.
    """
    selector = '//div[contains(@class, "ant-table-content")]/table'

    def __init__(self, page: Page, selector: Optional[str] = selector):
        super().__init__(page.locator(selector), page)

    @property
    def columns(self) -> list[AntColumn]:
        """
        Get a list of table columns (objects).
        :return: List[AntColumn]
        """
        self.wait_for_loader()
        return self.get_list_of_components('//thead//th', AntColumn, index=True)

    @property
    def rows(self) -> list[AntRow]:
        """
        Get a list of table rows (objects).
        :return: List[AntRow]
        """
        self.wait_for_loader()
        return self.get_list_of_components('//tbody//tr', AntRow)

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
        """
        Wait for the first cell of the table to be visible.
        """
        self.child_el('//tbody//td').raw.nth(0).wait_for(state='visible')
