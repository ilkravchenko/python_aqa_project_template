import time
from typing import Optional, Literal

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class SelectedOption(BaseComponent):
    """
    A component representing a selected option in a dropdown.

    Provides methods to access the name of the selected option and delete it.
    """

    @property
    def name(self) -> str:
        """
        Retrieve the text of the selected option.

        Returns:
            str: The name of the selected option.
        """
        return self.child_el('//span[@class="MuiChip-label"]').text

    def delete(self) -> None:
        """
        Clicks the delete button to remove the selected option.
        """
        self.child_el('//button').click()


class BaseDropdown(BaseComponent):
    """
    A base class for handling dropdown components.

    This class provides methods to interact with dropdown elements, such as expanding,
    collapsing, selecting options, and retrieving various attributes related to the dropdown.

    Args:
        label (str): The label of the dropdown component.
        page (Page): The Playwright page object.
        selector (Optional[str]): Optional XPath selector to locate the dropdown. Defaults to None.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Optional[Locator] = None):
        """
        Initializes the BaseDropdown component by setting the selector and passing it to the parent class.

        Args:
            label (str): The label of the dropdown to identify it.
            page (Page): The Playwright page object.
            selector (Optional[str]): Optional XPath selector. Defaults to an XPath based on the label if not provided.
        """
        if not selector:
            selector = f'//div[@role="combobox"]/../../label[contains(text(),"{label}")]/..'
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def title(self) -> str:
        """
        Get the title/label of the dropdown.

        Returns:
            str: The dropdown title.
        """
        return self.child_el('//label').text

    @property
    def is_required(self) -> bool:
        """
        Check if the dropdown is a required field.

        Returns:
            bool: True if the dropdown is required, False otherwise.
        """
        return 'field-required' in self.child_el('//label').get_attribute('class')

    @property
    def is_expanded(self) -> bool:
        """
        Check if the dropdown is currently expanded.

        Returns:
            bool: True if expanded, False otherwise.
        """
        loc = self.child_el('//div[@aria-expanded]')
        return loc.get_attribute('aria-expanded') == 'true' if loc.is_visible else None

    @property
    def input_field(self) -> BaseElement:
        """
        Get the input field element associated with the dropdown.

        Returns:
            BaseElement: The input field element.
        """
        return self.child_el('//input')

    @property
    def value(self) -> str:
        """
        Get the current selected value from the dropdown.

        Returns:
            str: The selected value.
        """
        return self.input_field.value

    @property
    def is_enabled(self) -> bool:
        """
        Check if the dropdown is enabled.

        Returns:
            bool: True if the dropdown is enabled, False otherwise.
        """
        return self.input_field.is_enabled

    @property
    def clear_button(self) -> BaseElement:
        """
        Get the clear button element for the dropdown.

        Returns:
            BaseElement: The clear button element.
        """
        return self.child_el('//button[@aria-label="Clear"]')

    @property
    def has_error(self) -> bool:
        """
        Checks if the dropdown field currently has an error state.

        Returns:
            bool: True if the field has an error, False otherwise.
        """
        return 'has-message' in self.element.get_attribute('class')

    @property
    def error_message(self) -> str:
        """
        Returns the error message associated with the input field, if any.

        Returns:
            str: The error message text.
        """
        return self.child_el('//*[@viewBox]/../..//span[contains(@class,"jss")][text()]').text

    def get_options(self, wait: bool = True) -> list[BaseElement]:
        """
        Retrieve the list of available options in the dropdown.

        Returns:
            list[BaseElement]: A list of available options in the dropdown.
        """
        return self.find_elements('//div[@role="presentation"]//li[@role="option"]', wait=wait)

    def get_text_options(self, wait: bool = True) -> list[str]:
        """
        Retrieve the text of all available options in the dropdown.

        Returns:
            list[str]: A list of option texts.
        """
        return [option.text for option in self.get_options(wait=wait)]

    @property
    def selected_options(self) -> list[SelectedOption]:
        """
        Retrieve the list of currently selected options.

        Returns:
            list[SelectedOption]: A list of selected options in the dropdown.
        """
        return self.get_list_of_components('//div[contains(@class,"MuiChip-root")]', SelectedOption)

    def wait_for_options(self) -> None:
        """
        Wait until the options in the dropdown become visible.
        """
        self.child_el('//div[contains(@class,"MuiChip-root")]').raw.nth(0).wait_for(state='visible')

    def expand(self, wait: bool = False, expand_type: Literal['input', 'arrow'] = 'input'):
        """
        Expand the dropdown if it's not already expanded.
        """
        if not self.is_expanded:
            if expand_type == 'arrow':
                self._open_arrow_button.click()
            else:
                self.input_field.click(force=True)
            if wait:
                self.page.wait_for_load_state(state='networkidle')
                self.page.locator('//div[@role="presentation"]//li[@role="option"]').nth(0).wait_for(state='visible')
                self.page.wait_for_load_state(state='domcontentloaded')
            time.sleep(0.2)
        return self

    def collapse(self, collapse_type: Literal['input', 'arrow'] = 'input') -> None:
        """
        Collapse the dropdown if it's currently expanded.
        """
        if self.is_expanded:
            if collapse_type == 'arrow':
                self._close_arrow_button.click()
            else:
                self.input_field.click(force=True)
            self.page.locator('//div[@role="presentation"]//li[@role="option"]').nth(0).wait_for(state='hidden')
            time.sleep(0.1)

    @property
    def _close_arrow_button(self) -> BaseElement:
        """
        Get the close arrow button element for the dropdown.

        Returns:
            BaseElement: The close arrow button element.
        """
        return self.child_el('//button[@aria-label="Close"]')

    @property
    def _open_arrow_button(self) -> BaseElement:
        """
        Get the open arrow button element for the dropdown.

        Returns:
            BaseElement: The open arrow button element.
        """
        return self.child_el('//button[@aria-label="Open"]')

    def select_option(self, option_value: str, search: bool = True, partial: bool = False, wait: bool = False,
                      index: Optional[int] = None) -> None:
        """
        Selects an option from a dropdown based on the provided value.

        Args:
            option_value (str): The value of the option to select.
            search (bool, optional): Whether to search for the option by typing into the input field. Defaults to True.
            partial (bool, optional): Whether to allow partial matches for the option text. Defaults to False.
            wait (bool, optional): Whether to wait for specific network requests during the search. Defaults to False.
            index (Optional[int], optional): The index of the option to select if multiple options match. Defaults to None.

        Raises:
            ValueError: If the search fails or the desired option cannot be located.
        """
        # Step 1: Open the dropdown menu
        self.expand(wait=wait)

        # Step 2: Perform a search if enabled
        if search:
            for _ in range(3):  # Retry mechanism to ensure the input value is correctly filled
                if wait:
                    # Define the network request pattern to wait for
                    request_pattern = '/data-factory/address-detailed-search'
                    with self.page.expect_request_finished(lambda request: request_pattern in request.url):
                        self.input_field.fill(option_value)  # Fill the input field with the search value
                        time.sleep(0.3)  # Allow time for the search request to complete
                else:
                    self.input_field.fill(option_value)  # Fill the input field without waiting for requests

                # Verify that the input field contains the correct value
                if self.input_field.value == option_value:
                    self.page.wait_for_load_state(state='networkidle')  # Ensure all network requests are idle
                    self.page.wait_for_load_state(state='domcontentloaded')  # Ensure DOM is fully loaded
                    break
            else:
                raise ValueError(
                    f"Dropdown search failed: Expected '{option_value}', but got '{self.input_field.value}'")

        # Step 3: Locate and select the desired option
        if partial:
            # Allow partial matching of the option text
            self.find_element(f"//li[@role='option'][contains(., '{option_value}')]").click()
        elif index is not None:
            # Select the option by index if provided
            self.find_element('//li[@role="option"]').raw.nth(index).click()
        else:
            # Require an exact match for the option text
            self.find_element(f'//li[@role="option"][normalize-space()="{option_value}"]').click()

        # Step 4: Wait for the dropdown options to close
        self.find_element('//div[@role="presentation"]//li[@role="option"]').raw.nth(0).wait_for(state='hidden')
        time.sleep(0.1)  # Allow a brief delay for UI stabilization
        assert self.input_field.value or self.selected_options, 'The dropdown value was not selected'
