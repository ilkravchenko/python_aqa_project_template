import time
from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement
from pages.common.base_page import BasePage
from pages.common.input import BaseInput
from pages.reports.common.ant_table import AntTable, AntRow, AntPaginationComponent
from pages.urls import ReportUrls


class DashboardMenuItem(BaseComponent):
    def __init__(self, label: str, page: Page, root: Optional[Locator] = None, selector: Optional[str] = None):
        if not selector:
            selector = f'//li/a[text()="{label}"]/..'
        super().__init__(root.locator(selector), page)

    @property
    def name(self) -> str:
        return self.child_el('//a').text

    @property
    def is_selected(self) -> bool:
        return 'ant-menu-item-selected' in self.element.get_attribute('class')

    def select(self) -> None:
        if not self.is_selected:
            self.child_el('//a').click()
            time.sleep(0.2)


class DashboardMenu(BaseComponent):
    @property
    def all_dashboards(self) -> DashboardMenuItem:
        return self.child_el(label="All information panels", component=DashboardMenuItem)

    @property
    def my_dashboards(self) -> DashboardMenuItem:
        return self.child_el(label="My information pannels", component=DashboardMenuItem)

    @property
    def favorite_dashboards(self) -> DashboardMenuItem:
        return self.child_el(label="Favorite", component=DashboardMenuItem)


class DashboardRow(AntRow):
    @property
    def name(self) -> str:
        return self.child_el('//td[2]').text

    @property
    def link(self) -> BaseElement:
        return self.child_el('//td[2]//a')

    @property
    def created_by(self) -> str:
        return self.child_el('//td[2]').text

    @property
    def created_at(self) -> str:
        return self.child_el('//td[3]').text

    @property
    def is_favorite(self) -> bool:
        return self.child_el('//td[1]/button').get_attribute('aria-label') == 'Remove from favorites'

    def add_to_favorite(self) -> None:
        if not self.is_favorite:
            self.child_el('//td[1]/button').click()
            time.sleep(0.2)

    def remove_from_favorite(self) -> None:
        if self.is_favorite:
            self.child_el('//td[1]/button').click()
            time.sleep(0.2)


class DashboardsTable(AntTable):
    @property
    def rows(self) -> list[DashboardRow]:
        return self.get_list_of_components(AntRow.selector, DashboardRow)

    @property
    def pagination(self) -> AntPaginationComponent:
        return AntPaginationComponent(self.page)


class DashboardPage(BasePage):
    """
    Reports
    """

    @property
    def table(self) -> DashboardsTable:
        return DashboardsTable(self.page)

    @property
    def menu(self) -> DashboardMenu:
        return DashboardMenu(self.page.locator('//div[@class="m-b-10 tags-list tiled"]'), self.page)

    @property
    def search_input(self) -> BaseInput:
        return BaseInput('Looking for information panels...', self.page,
                         selector='//input[@placeholder="Looking for information panels..."]/..')

    def open_page(self) -> None:
        """
        Open the dashboards page.

        This method navigates to the dashboards URL and waits for the page to load completely.

        Returns:
            None
        """
        self.page.goto(ReportUrls().dashboards_url)
        self.wait_for_page_load(anchor_selector='//div[@data-test="DashboardLayoutContent"]')

    def open_dashboard(self, name: str) -> None:
        """
        Open a specific dashboard by name.

        This method searches for a dashboard by its name, clicks on the corresponding link,
        and waits for the page to load completely.

        Args:
            name (str): The name of the dashboard to open.

        Returns:
            None
        """
        self.search_input.fill(name)
        self.wait_for_page_load()
        self.find_element(f'//a[@class="table-main-title"][text()="{name}"]').wait_until_visible(timeout=30000).click()
        time.sleep(0.2)
        self.page.wait_for_load_state(state='networkidle', timeout=60000)  # Ensure all network requests are idle
        self.page.wait_for_load_state(state='domcontentloaded', timeout=60000)
