import time
from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class AntDropdown(BaseComponent):
    """
    A class to interact with Ant Design's Select dropdown component.

    Supports expanding, collapsing, selecting an option, and retrieving selected values.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Locator = None):
        """
        Initialize the AntDropdown component using the label.

        Args:
            label (str): The label text associated with the dropdown.
            page (Page): The Playwright page object.
            root (Locator, optional): Optional root element for scoping.
        """
        if not selector:
            selector = f'//div[@data-test="ParameterBlock-{label}"]//div[contains(@class, "ant-select ")]'
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def search_input(self) -> BaseElement:
        return self.child_el('//input')

    @property
    def selected_value(self) -> str:
        """
        Get the currently selected value from the dropdown.

        Returns:
            str: The text of the selected value.
        """
        return self.child_el('//*[contains(@class, "ant-select-selection-item")]').text

    def expand(self) -> None:
        """
        Expand the dropdown if it's not already expanded.
        """
        self.wait_for_dropdown_loading()
        if not self.is_expanded:
            self.element.click()
            self.wait_for_dropdown_expansion()

    def collapse(self) -> None:
        """
        Collapse the dropdown if it's currently expanded.
        """
        if self.is_expanded:
            self.element.click()
            self.wait_for_dropdown_collapse()
        self.wait_for_dropdown_loading()

    def wait_for_dropdown_loading(self) -> None:
        self.wait_for_page_load()
        for element in self.find_elements('//div[contains(@class,"ant-select-loading")]', wait=False):
            element.raw.wait_for(state="hidden")
        self.page.wait_for_load_state(state='networkidle')  # Ensure all network requests are idle
        self.page.wait_for_load_state(state='domcontentloaded')  # Ensure DOM is fully loaded

    @property
    def _expanded_dropdown_selector(self) -> str:
        """
        Get the selector for the expanded dropdown.

        Returns:
            str: The XPath selector for the expanded dropdown.
        """
        return "//div[contains(@class, 'dropdown-placement') and not(contains(@class, 'hidden'))]"

    @property
    def is_expanded(self) -> bool:
        """
        Check if the dropdown is currently expanded.

        Returns:
            bool: True if expanded, False otherwise.
        """
        return ('ant-select-open' in self.element.get_attribute('class') and
                self.find_element(self._expanded_dropdown_selector).is_visible)

    def wait_for_dropdown_expansion(self) -> None:
        """
        Wait for the dropdown to be expanded.
        """
        self.find_element(self._expanded_dropdown_selector).wait_until_visible()
        time.sleep(0.2)
        selector = f'{self._expanded_dropdown_selector}//div[contains(@class, "ant-select-item-option-content")]'
        self.find_element(selector).raw.nth(1).wait_for(state="visible")

    def wait_for_dropdown_collapse(self) -> None:
        """
        Wait for the dropdown to be collapsed.
        """
        self.find_element(self._expanded_dropdown_selector).wait_until_hidden()

    def select_option(self, option_text: str, partial: bool = False, search: bool = True) -> None:
        """
        Select an option from the dropdown, ensuring selection is within an expanded dropdown.

        Supports both:
        - `ant-dropdown-menu-item` (used in Ant Design dropdown menus)
        - `ant-select-item-option` (used in Ant Design select dropdowns)

        Args:
            option_text (str): The text of the option to select.
            partial (bool): Whether to match the text partially or fully.
            search (bool): Whether to search for the option text in the dropdown.
        """

        self.expand()  # Ensure the dropdown is expanded

        if search:
            self.search_input.fill(option_text)
            time.sleep(0.1)

        # Define selectors for different dropdown types
        dropdown_selector = ('//div[(contains(@class, "ant-dropdown") or contains(@class, "ant-select-dropdown")) '
                             'and not(contains(@class, "hidden")) and not(contains(@class, "dynamic-button"))]')
        option_selector_menu = f'{dropdown_selector}//li[contains(@class, "ant-dropdown-menu-item")]'
        option_selector_select = f'{dropdown_selector}//div[contains(@class, "ant-select-item-option-content")]'

        # Generate locators based on partial or full match
        if partial:
            option_locator_menu = f'{option_selector_menu}[contains(text(), "{option_text}")]'
            option_locator_select = f'{option_selector_select}[contains(text(), "{option_text}")]'
        else:
            option_locator_menu = f'{option_selector_menu}[text()="{option_text}"]'
            option_locator_select = f'{option_selector_select}[text()="{option_text}"]'

        # Try selecting from both possible dropdown types
        if self.find_element(option_locator_menu).is_visible:
            option_element = self.find_element(option_locator_menu)
        elif self.find_element(option_locator_select).is_visible:
            option_element = self.find_element(option_locator_select)
        else:
            raise ValueError(f"Option '{option_text}' not found in the expanded dropdown.")

        option_element.click()
        self.wait_for_dropdown_loading()
        self.find_element(dropdown_selector).wait_until_hidden()

    def get_options(self) -> list[str]:
        """
        Retrieve a list of available options in the dropdown.

        Returns:
            list[str]: A list of option texts.
        """
        self.expand()
        option_locators = self.find_elements('//div[contains(@class, "ant-select-item-option-content")]')
        return [option.text.strip() for option in option_locators]
