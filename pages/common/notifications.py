import time
from time import sleep
from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement
from pages.common.base_page import BasePage


class NotificationComponent(BaseComponent):
    """
    A component representing an individual notification on the page.
    It provides methods to interact with and retrieve data from the notification component.
    """

    # XPath selector to locate the notification component
    selector = '//div[@data-testid="timed-notification"]'

    def __init__(self, page: Page, selector: str = selector, locator: Optional[Locator] = None):
        """
        Initializes the NotificationComponent with the provided selector or locator.

        Args:
            page (Page): Playwright page object.
            selector (str): The XPath selector to locate the notification (default is NotificationComponent.selector).
            locator (Optional[Locator]): Optional Locator object to locate the notification element.
        """
        if not locator:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(locator, page)

    @property
    def title(self) -> str:
        """
        Returns the title of the notification.

        Returns:
            str: The title text of the notification.
        """
        return self.child_el('//div/div[text()][1]').text

    @property
    def body_text(self) -> str:
        """
        Returns the body text of the notification.

        Returns:
            str: The body content of the notification.
        """
        return self.child_el('//div/div[text()][2]').raw.inner_text().split('\n')[0]

    @property
    def icon(self) -> str:
        """
        Returns the name of the icon used in the notification.

        Returns:
            str: The icon name in the notification.
        """
        return self.child_el('//span[@role="img"]').text

    @property
    def secondary_button(self) -> BaseElement:
        return self.child_el('//button[contains(@class,"MuiButton-outlinedSecondary")]')

    def close(self) -> None:
        """
        Closes the notification by clicking the close button and waits for the notification to disappear.
        """
        self.child_el('//button[contains(@class,"MuiIconButton-edgeStart")]').click()
        # Adding a small sleep to handle potential animation delay after closing
        sleep(0.2)
        self.wait_for_invisibility()


class Notifications(BasePage):
    """
    A class representing a collection of notifications on the page.
    It provides methods to handle multiple notifications, including waiting, closing, and verifying them.
    """

    def wait_for_notifications(self) -> None:
        """
        Waits until at least one notification is visible on the page.
        """
        self.find_element(NotificationComponent.selector).raw.nth(0).wait_for(state="visible")

    def wait_for_notifications_hidden(self) -> None:
        """
        Waits until all notifications are hidden or none are visible.
        """
        self.find_element(NotificationComponent.selector).raw.nth(0).wait_for(state="hidden")

    @property
    def notifications_list(self) -> list[NotificationComponent]:
        """
        Returns a list of currently visible notification components.

        Returns:
            list[NotificationComponent]: A list of NotificationComponent objects representing the visible notifications.
        """
        # Adding a small delay to ensure the notifications are rendered properly
        sleep(0.2)
        return self.get_list_of_components(selector=NotificationComponent.selector, component=NotificationComponent)

    def close_notifications(self) -> None:
        """
        Closes all visible notifications in reverse order to ensure correct handling of DOM elements.
        """
        # Reverse the list to close notifications in the reverse order to avoid locator issues
        notifications = self.notifications_list[::-1]
        count = len(notifications)
        for notification in notifications:
            notification.close()
            notification.wait_for_invisibility()
            while count == len(self.notifications_list):
                # Wait for the notification to be removed from the list
                time.sleep(0.2)
            count -= 1

    def verify_notifications(self, text: str, title: str = 'Welcome!', icon: str = '✅') -> None:
        """
        Verifies the title, body text, and icon of the first visible notification, and then closes all notifications.

        Args:
            text (str): The expected body text of the notification.
            title (str, optional): The expected title of the notification (default is 'Вітаємо!').
            icon (str, optional): The expected icon of the notification (default is '✅').

        Raises:
            AssertionError: If any of the title, body text, or icon do not match the expected values.
        """
        self.wait_for_page_load()
        self.wait_for_notifications()
        notification = self.notifications_list[0]  # Verify the first notification
        assert notification.title == title, f'{notification.title} instead of {title}'
        assert notification.icon == icon, f'{notification.icon} instead of {icon}'
        assert notification.body_text.replace(' ', ' ') == text, f'{notification.body_text} instead of {text}'
        self.close_notifications()
