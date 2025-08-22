from time import sleep
from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_page import BasePage


class ValidationMessageComponent(BaseComponent):
    """
    Component for interacting with validation messages on a page.

    This class provides properties to access the title and icon elements within
    a validation message component, which is located using a specific XPath selector.

    Args:
        page (Page): Playwright Page instance for web interactions.
        selector (str): XPath selector to locate the validation message component.
        locator (Optional[Locator]): Optional specific locator for the component.

    Attributes:
        selector (str): Default XPath selector for the validation message component.
    """

    selector = '//div[@data-xpath="validationMessageTitle"]/../..'

    def __init__(self, page: Page, selector: str = selector, locator: Optional[Locator] = None):
        """
        Initialize the ValidationMessageComponent with either a custom locator or a default selector.

        If a custom locator is provided, it will be used to locate the component;
        otherwise, the default selector will be applied.

        Args:
            page (Page): The Playwright Page instance.
            selector (str): The XPath selector to locate the validation message.
            locator (Optional[Locator]): A specific locator, if available, to initialize the component.
        """
        # Use a provided locator if available; otherwise, use the default selector
        if not locator:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(locator, page)

    @property
    def title(self) -> str:
        """
        Retrieve the text of the validation message title.

        Returns:
            str: The title text of the validation message component.
        """
        return self.child_el('//div[text()]').text

    @property
    def icon(self) -> str:
        """
        Retrieve the text of the icon element within the validation message.

        Returns:
            str: The text or label of the icon (often used for accessibility).
        """
        return self.child_el('//span[@role="img"]').text


class ValidationMessages(BasePage):
    """
    Class for interacting with validation messages on a page.

    This class provides methods to wait for validation messages to appear or disappear,
    retrieve a list of validation message components, and verify the content of validation messages.
    """

    def wait_for_validation_messages(self) -> None:
        """
        Wait for the validation messages to become visible.

        This method waits until the first validation message component is visible on the page.
        """
        self.find_element(ValidationMessageComponent.selector).raw.nth(0).wait_for(state="visible")

    def wait_for_validation_messages_hidden(self) -> None:
        """
        Wait for the validation messages to become hidden.

        This method waits until the first validation message component is hidden on the page.
        """
        self.find_element(ValidationMessageComponent.selector).raw.nth(0).wait_for(state="hidden")

    @property
    def validation_messages_list(self) -> list[ValidationMessageComponent]:
        """
        Retrieve a list of validation message components.

        This property adds a small delay to ensure the validation messages are rendered properly,
        then returns a list of `ValidationMessageComponent` instances.

        Returns:
            list[ValidationMessageComponent]: A list of validation message components.
        """
        sleep(0.2)
        return self.get_list_of_components(selector=ValidationMessageComponent.selector,
                                           component=ValidationMessageComponent)

    def verify_validation_messages(self, title: str, icon: str = '🔥') -> None:
        """
        Verify the content of the validation messages.

        This method waits for the validation messages to appear, then verifies that the first
        validation message has the expected title and icon.

        Args:
            title (str): The expected title of the validation message.
            icon (str): The expected icon of the validation message. Defaults to '🔥'.

        Raises:
            AssertionError: If the title or icon of the validation message does not match the expected values.
        """
        self.wait_for_validation_messages()
        validation_message = self.validation_messages_list[0]  # Verify the first validation message
        assert validation_message.title == title, f'{validation_message.title} instead of {title}'
        assert validation_message.icon == icon, f'{validation_message.icon} instead of {icon}'
        self.page.wait_for_load_state(state='domcontentloaded')
