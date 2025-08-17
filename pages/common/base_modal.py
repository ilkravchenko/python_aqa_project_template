import time
from typing import Optional

from playwright.sync_api import Page

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class BaseModal(BaseComponent):
    """
    A base class for interacting with modals in the UI.

    This class provides common methods and properties to interact with modal components
    such as save, cancel, and close actions. It uses a default selector if none is provided,
    based on the label of the modal.

    Args:
        label (str): The label text of the modal, used to construct a default selector if none is provided.
        page (Page): The Playwright page instance for locating and interacting with elements.
        selector (Optional[str]): Optional custom selector for the modal.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None):
        # If no selector is provided, construct the default XPath selector based on the label
        if not selector:
            selector = f'//YOUR_IDENTIFIER[contains(text(),"{label}")]/YOUR_IDENTIFIER'
        # Initialize the BaseComponent with the located checkbox element and page
        super().__init__(page.locator(selector), page)

    @property
    def save_button(self) -> BaseElement:
        """
        Returns the save button element inside the modal.

        Returns:
            BaseElement: The save button element.
        """
        return self.child_el('//button[@type="submit"]')

    @property
    def cancel_button(self) -> BaseElement:
        """
        Returns the cancel button element inside the modal.

        Returns:
            BaseElement: The cancel button element.
        """
        return self.child_el('//button[@name="data[cancel]"]')

    @property
    def close_icon(self) -> BaseElement:
        """
        Returns the close icon element to close the modal.

        Returns:
            BaseElement: The close icon element.
        """
        return self.child_el('//button[@aria-label="close"]')

    @property
    def title(self) -> BaseElement:
        """
        Returns the title element of the modal.

        Returns:
            BaseElement: The title element of the modal.
        """
        return self.child_el('//title')

    def close(self) -> None:
        """
        Clicks the close icon to close the modal and waits until the modal is no longer visible.
        """
        self.close_icon.click()
        self.wait_for_invisibility()

    def cancel(self) -> None:
        """
        Clicks the cancel button to close the modal and waits until the modal is no longer visible.
        """
        self.cancel_button.click()
        self.wait_for_invisibility()

    def save(self, wait: bool = True) -> None:
        """
        Clicks the save button to submit the modal and optionally waits until the modal is no longer visible.

        Args:
            wait (bool): Whether to wait for the modal to disappear after clicking save. Default is True.
        """
        self.save_button.click()
        if wait:
            self.wait_for_invisibility()
            time.sleep(0.2)
