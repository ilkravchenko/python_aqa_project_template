import time
from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class BaseInput(BaseComponent):
    """
    Represents a base input field component that provides common functionality for text inputs.

    This class is designed to locate input elements based on their associated labels and
    provides properties and methods to interact with these input fields (e.g., filling in data, checking
    if the field is enabled, checking for error messages, etc.).
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Optional[Locator] = None,
                 strict: bool = False):
        """
        Initializes the BaseInput object.

        Args:
            label (str): The label text associated with the input field.
            page (Page): The Playwright page instance for browser interactions.
            selector (Optional[str]): The selector for the input field. If not provided, a default selector is constructed based on the label.
            root (Optional[Locator]): The root locator to search within. If not provided, the entire page is searched.
            strict (bool): If True, the selector will be strict. Defaults to False.
        """
        if not selector:
            # Default selector is created using the label if none is provided
            if strict:
                selector = f'//div[not(ancestor::div[@style="display: none;"])][contains(@class,"MuiTextField-root")]/../../label[normalize-space()="{label}"]/..'
            else:
                selector = f'//div[not(ancestor::div[@style="display: none;"])][contains(@class,"MuiTextField-root")]/../../label[contains(text(),"{label}")]/..'
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def title(self) -> str:
        """
        Returns the title (label text) of the input field.

        Returns:
            str: The label text of the input field.
        """
        return self.child_el('//label').text

    @property
    def error_message(self) -> str:
        """
        Returns the error message associated with the input field, if any.

        Returns:
            str: The error message text.
        """
        return self.child_el('//*[@viewBox]/../..//span[contains(@class,"jss")][text()]').text

    @property
    def is_required(self) -> bool:
        """
        Checks whether the input field is marked as required.

        Returns:
            bool: True if the field is required, False otherwise.
        """
        return 'field-required' in self.child_el('//label').get_attribute('class')

    @property
    def input_field(self) -> BaseElement:
        """
        Locates and returns the input field element.

        Returns:
            BaseElement: The input field element.
        """
        return self.child_el('//input')

    @property
    def is_enabled(self) -> bool:
        """
        Checks whether the input field is enabled.

        Returns:
            bool: True if the input field is enabled, False otherwise.
        """
        return self.input_field.is_enabled

    @property
    def has_error(self) -> bool:
        """
        Checks if the input field currently has an error state.

        Returns:
            bool: True if the field has an error, False otherwise.
        """
        return 'has-error' in self.element.get_attribute('class')

    def wait_for_error(self, timeout: int = 3) -> None:
        """
        Waits for an error to disappear from the input field by polling the has_error property.

        Args:
            timeout (int): Maximum time to wait in milliseconds. Defaults to 10 seconds.
        """
        poll_interval = 0.1  # 100ms poll interval

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if not self.has_error:
                    return
            except Exception:
                # If element is not attached or has other issues, we consider it has no error
                return
            self.page.wait_for_timeout(int(poll_interval * 1000))

        raise TimeoutError(f"Timed out waiting for error to disappear on field '{self.title}'")

    @property
    def value(self) -> str:
        """
        Retrieves the current value of the input field.

        Returns:
            str: The value of the input field.
        """
        return self.input_field.value

    @property
    def tooltip_icon(self) -> BaseElement:
        return self.child_el('//i')

    @property
    def tooltip(self) -> BaseElement:
        return self.child_el('//div[@class="tooltip"]')

    def fill(self, text: str) -> None:
        """
        Fills the input field with the provided text, replacing the existing value.

        Args:
            text (str): The text to be filled in the input field.
        """
        self.input_field.fill(text)

    def type(self, text: str) -> None:
        """
        Types the given text into the input field. Simulates typing character by character.

        Args:
            text (str): The text to be typed into the input field.
        """
        self.input_field.type(text)

    def clear(self):
        """
        Clears the input field.
        """
        self.input_field.clear()
        return self


class BaseTextarea(BaseInput):
    """
    Represents a textarea component, inheriting functionality from BaseInput.
    Overrides the `input_field` property to locate a `textarea` element instead of an `input` element.
    """

    @property
    def input_field(self) -> BaseElement:
        """
        Locates and returns the textarea field element.

        Returns:
            BaseElement: The textarea field element.
        """
        return self.child_el('//textarea')


class SearchInput(BaseInput):
    """
    Represents a search input field component, inheriting from BaseInput.
    This class is used for search input fields specifically, and constructs a custom selector.

    Args:
        label (str): The label associated with the search input field.
        page (Page): The Playwright page instance for browser interactions.
        selector (Optional[str]): Custom selector to locate the search input field. If not provided, a default selector is constructed based on the label.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None):
        """
        Initializes the SearchInput object with a custom or default selector.

        Args:
            label (str): The label text associated with the search input field.
            page (Page): The Playwright page instance for browser interactions.
            selector (Optional[str]): The custom selector for the search input field. If not provided, a default selector is generated.
        """
        if not selector:
            # Default selector specific to search fields
            selector = f'//div[contains(@id,"search-field")]/../../label[contains(text(),"{label}")]/..'
        super().__init__(label=label, selector=selector, page=page)

    @property
    def input_field(self) -> BaseElement:
        """
        Locates and returns the input field element specific to search inputs.

        Returns:
            BaseElement: The input field element for search input.
        """
        return self.child_el('//input[contains(@style,"display: block")]')
