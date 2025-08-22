import time
from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class BaseCheckbox(BaseComponent):
    """
    A class representing a checkbox component on a web page.

    This class provides methods to interact with a checkbox, including checking,
    unchecking, and verifying its state (checked, required, enabled).

    Inherits from:
        BaseComponent: The base class for all components, providing common methods
                       for interacting with elements on the page.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Optional[Locator] = None):
        """
        Initialize the BaseCheckbox instance with a label, page, and optional selector.

        Args:
            label (str): The label text associated with the checkbox.
            page (Page): The Playwright Page object where the checkbox exists.
            selector (Optional[str]): The selector for the checkbox. If not provided,
                                      a default XPath is constructed based on the label.
        """
        # If no selector is provided, construct the default XPath selector based on the label
        if not selector:
            # EXAMPLE
            selector = f'//input[@type="checkbox"]/ancestor::label//span[contains(text(),"{label}")]/ancestor::div[@ref="component"][1]'
        # Initialize the BaseComponent with the located checkbox element and page
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def title(self) -> str:
        """
        Get the title (text) of the checkbox label.

        Returns:
            str: The label/title text associated with the checkbox.
        """
        return self.child_el('//label//span[text()]').text

    @property
    def is_checked(self) -> bool:
        """
        Check if the checkbox is currently checked.

        Returns:
            bool: True if the checkbox is checked, False otherwise.
        """
        # Check for the presence of 'Mui-checked' class in the checkbox element
        return 'Mui-checked' in self.child_el('//span[contains(@class,"MuiCheckbox-root")]').get_attribute('class')

    @property
    def is_required(self) -> bool:
        """
        Check if the checkbox is marked as required.

        Returns:
            bool: True if the checkbox is required, False otherwise.
        """
        # Check for the presence of 'field-required' class in the label element
        return 'field-required' in self.child_el('//label').get_attribute('class')

    @property
    def input_field(self) -> BaseElement:
        """
        Get the input field element of the checkbox.

        Returns:
            BaseElement: The input field element representing the checkbox.
        """
        return self.child_el('//input')

    @property
    def is_enabled(self) -> bool:
        """
        Check if the checkbox is currently enabled.

        Returns:
            bool: True if the checkbox is enabled, False otherwise.
        """
        return self.input_field.is_enabled

    def _wait_until_be_checked(self, checked: bool = True, timeout: float = 5) -> None:
        """
        Wait until the checkbox reaches the expected checked state.

        Args:
            checked (bool): The expected checked state (True for checked, False for unchecked).
            timeout (float): Maximum time to wait in seconds.

        Raises:
            TimeoutError: If the checkbox does not reach the expected state within the timeout.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_checked == checked:
                return
            time.sleep(0.1)
        raise TimeoutError(f"Checkbox '{self.title}' did not reach expected checked state: {checked}")

    def check(self) -> None:
        """
        Check the checkbox if it is not already checked.

        This method forces the click action to ensure the checkbox is checked.
        """
        # If the checkbox is not checked, click to check it
        if not self.is_checked:
            self.input_field.click(force=True)
            self._wait_until_be_checked(checked=True)

    def uncheck(self) -> None:
        """
        Uncheck the checkbox if it is already checked.

        This method forces the click action to ensure the checkbox is unchecked.
        """
        # If the checkbox is checked, click to uncheck it
        if self.is_checked:
            self.input_field.click(force=True)
            self._wait_until_be_checked(checked=False)