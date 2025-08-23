from playwright.sync_api import Page

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class Sidebar(BaseComponent):
    selector = '//nav[@class="desktop-navbar"]'

    def __init__(self, page: Page, selector: str = selector):
        """
        Initialize the HeaderComponent with the page and its selector.

        Args:
            page (Page): The Playwright Page instance.
            selector (str): The XPath selector for the header. Defaults to a predefined XPath for the header.
        """
        super().__init__(page.locator(selector), page)

    @property
    def home_page_icon(self) -> BaseElement:
        return self.child_el('//div[@role="menuitem"]/a[@href="/reports/./"]')

    @property
    def dashboards_icon(self) -> BaseElement:
        return self.child_el('//li[@role="menuitem"]/a[@href="/reports/dashboards"]')

    @property
    def queries_icon(self) -> BaseElement:
        return self.child_el('//li[@role="menuitem"]/a[@href="/reports/queries"]')

    @property
    def alerts_icon(self) -> BaseElement:
        return self.child_el('//li[@role="menuitem"]/a[@href="/reports/alerts"]')
