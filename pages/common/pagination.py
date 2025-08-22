import time
from typing import Literal, Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement
from pages.common.dropdown import BaseDropdown


class PaginationComponent(BaseComponent):
    """
    A class to represent the pagination controls on a table.

    This component interacts with the pagination elements on the table,
    such as navigating to the next/previous pages, setting the number
    of rows per page, and accessing pagination buttons.

    Attributes:
        selector (str): The XPath selector used to locate the pagination toolbar.
    """
    # XPath selector for the pagination toolbar
    selector = '//div[contains(@class,"MuiTablePagination-toolbar")]'

    def __init__(self, page: Page, selector: str = selector, root: Optional[Locator] = None):
        """
        Initialize the PaginationComponent.

        Args:
            page (Page): The Playwright page object.
            selector (str): The selector for the pagination toolbar. Defaults to a common selector for pagination.
        """
        # Initialize the component by locating the selector on the given page
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def rows_number(self) -> str:
        """
        Get the number of rows displayed in the pagination section.

        Returns:
            str: The number of rows as a string.
        """
        # Locate and return the text of the row count displayed in the pagination controls
        return self.child_el('//p[2]/span').text

    @property
    def next_page_button(self) -> BaseElement:
        """
        Get the next page button element.

        Returns:
            BaseElement: The Playwright element representing the next page button.
        """
        # Locate and return the "Next Page" button
        return self.child_el('//button[@aria-label="Next Page"]')

    @property
    def previous_page_button(self) -> BaseElement:
        """
        Get the previous page button element.

        Returns:
            BaseElement: The Playwright element representing the previous page button.
        """
        # Locate and return the "Previous Page" button
        return self.child_el('//button[@aria-label="Previous Page"]')

    @property
    def first_page_button(self) -> BaseElement:
        """
        Get the first page button element.

        Returns:
            BaseElement: The Playwright element representing the first page button.
        """
        # Locate and return the "First Page" button
        return self.child_el('//button[@aria-label="First Page"]')

    @property
    def last_page_button(self) -> BaseElement:
        """
        Get the first page button element.

        Returns:
            BaseElement: The Playwright element representing the first page button.
        """
        # Locate and return the "Last Page" button
        return self.child_el('//button[@aria-label="Last Page"]')

    @property
    def rows_limit_dropdown(self) -> BaseDropdown:
        """
        Get the dropdown element for setting the number of rows per page.

        Returns:
            BaseDropdown: The dropdown element that controls the number of rows per page.
        """
        # XPath selector for the rows per page dropdown
        selector = '//div[contains(@class,"MuiTablePagination-input")]'

        # Return the dropdown component for selecting the rows limit
        return self.child_el(label='Rows on page', selector=selector, component=BaseDropdown)

    def set_limit(self, limit: Literal['10', '25', '50', '100']) -> None:
        """
        Set the limit for the number of rows per page in the pagination dropdown.

        Args:
            limit (Literal['10', '25', '50', '100']): The number of rows to display per page.

        Returns:
            None
        """
        # Select the desired row limit from the dropdown
        self.rows_limit_dropdown.select_option(limit, search=False)

        # Wait for the page to load after selecting the new limit
        self.wait_for_page_load()
        self.page.wait_for_load_state(state='domcontentloaded')
        for _ in range(10):
            if self.rows_limit_dropdown.value == limit:
                break
            time.sleep(0.1)
            self.wait_for_page_load()

        # Adding a small delay to ensure the page updates correctly
        time.sleep(0.1)
