from time import sleep
from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement
from pages.common.base_page import BasePage
from pages.urls import Urls


class MessagesPagination(BaseComponent):
    selector = '//div[contains(@class,"MuiTablePagination-root")]'

    def __init__(self, page: Page, selector: str = selector, locator: Optional[Locator] = None):
        if not locator:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(locator, page)

    @property
    def pagination_info(self) -> str:
        return self.find_element('//p[contains(@class,"MuiTablePagination-caption")]').text

    @property
    def first_page_button(self) -> BaseElement:
        return self.child_el('//button[@data-xpath="tableFirstPage"]')

    @property
    def previous_page_button(self) -> BaseElement:
        return self.child_el('//button[@data-xpath="tablePrevPage"]')

    @property
    def next_page_button(self) -> BaseElement:
        return self.child_el('//button[@data-xpath="tableNextPage"]')

    def go_to_first_page(self) -> None:
        self.first_page_button.click()
        self.wait_for_page_load()

    def go_to_previous_page(self) -> None:
        self.previous_page_button.click()
        self.wait_for_page_load()

    def go_to_next_page(self) -> None:
        self.next_page_button.click()
        self.wait_for_page_load()

    @property
    def current_range(self) -> tuple[int, int]:
        """Returns the current range of displayed messages as (start, end)"""
        info_text = self.pagination_info
        numbers = [int(num) for num in info_text.split() if num.isdigit()]
        if len(numbers) >= 2:
            return numbers[0], numbers[1]
        return 0, 0


class MessageComponent(BaseComponent):
    selector = '//div[contains(@class,"MuiTablePagination-root")]/../div[starts-with(@class,"jss")]'

    def __init__(self, page: Page, selector: str = selector, locator: Optional[Locator] = None):
        if not locator:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(locator, page)

    @property
    def datetime(self) -> str:
        return self.child_el('//p[contains(@class,"jss74")]').text

    @property
    def is_new(self) -> bool:
        new_label = self.child_el('//p[contains(@class,"jss75")]')
        return new_label.is_visible and "New message" in new_label.text

    @property
    def title(self) -> str:
        return self.child_el('//h3[contains(@class,"jss66")]').text

    @property
    def text(self) -> str:
        return self.child_el('//p[contains(@class,"jss70")]').text

    @property
    def is_expanded(self) -> bool:
        return self.child_el('//p[text()="Hide"]').is_visible

    def expand(self) -> None:
        if not self.is_expanded:
            self.child_el('//a[contains(@class,"jss91")]').click()
            self.wait_for_page_load()

    def collapse(self) -> None:
        if self.is_expanded:
            self.child_el('//a[contains(@class,"jss91")]').click()
            self.wait_for_page_load()


class MessagesPage(BasePage):
    """
    Welcome!
    Here we will receive messages.
    """

    def open_page(self) -> None:
        self.page.goto(Urls().messages_url)
        self.wait_for_page_load(anchor_selector='//p[text()="Here we will receive messages."]')

    def wait_for_messages(self) -> None:
        """
        Waits until at least one Message is visible on the page.
        """
        self.find_element(MessageComponent.selector).raw.nth(0).wait_for(state="visible")

    @property
    def messages_list(self) -> list[MessageComponent]:
        """
        Returns a list of currently visible Message components.

        Returns:
            list[MessageComponent]: A list of MessageComponent objects representing the visible Messages.
        """
        # Adding a small delay to ensure the Messages are rendered properly
        sleep(0.2)
        return self.get_list_of_components(selector=MessageComponent.selector, component=MessageComponent)

    @property
    def pagination(self) -> MessagesPagination:
        """
        Returns the pagination component of the messages page.
        """
        return MessagesPagination(self.page)

    def get_messages_by_time_range(self, from_datetime: str, to_datetime: str) -> list[MessageComponent]:
        """
        Returns messages that fall within the specified datetime range.
        Optimized to stop pagination once we encounter messages older than the from_datetime.

        Args:
            from_datetime: Start datetime in format 'DD.MM.YYYY HH:MM'
            to_datetime: End datetime in format 'DD.MM.YYYY HH:MM'

        Returns:
            list[MessageComponent]: Messages within the specified time range
        """
        from datetime import datetime

        # Convert input strings to datetime objects
        from_dt = datetime.strptime(from_datetime, '%d.%m.%Y %H:%M')
        to_dt = datetime.strptime(to_datetime, '%d.%m.%Y %H:%M')

        filtered_messages = []

        # Make sure we have messages loaded
        self.wait_for_messages()

        # Process pages until we find messages older than from_datetime
        while True:
            # Get all visible messages on current page
            messages = self.messages_list

            # Skip empty pages
            if not messages:
                break

            # Filter messages by datetime
            for message in messages:
                try:
                    message_dt = datetime.strptime(message.datetime, '%d.%m.%Y %H:%M')
                    if from_dt <= message_dt <= to_dt:
                        filtered_messages.append(message)
                except ValueError:
                    # Skip messages with invalid datetime format
                    continue

            # Check if the oldest (last) message on this page is already older than our from_date
            # If so, we don't need to check more pages
            if messages:
                try:
                    oldest_message_dt = datetime.strptime(messages[-1].datetime, '%d.%m.%Y %H:%M')
                    if oldest_message_dt < from_dt:
                        break
                except ValueError:
                    # If we can't parse the date, continue to next page to be safe
                    pass

            # Check if we can go to next page
            if self.pagination.next_page_button.is_visible:
                self.pagination.go_to_next_page()
            else:
                break

        return filtered_messages
