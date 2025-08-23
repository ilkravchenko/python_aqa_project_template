from pages.common.base_element import BaseElement
from pages.common.base_page import BasePage
from pages.urls import Urls


class ReportsPage(BasePage):

    @property
    def view_reports_link(self) -> BaseElement:
        return self.find_element('//a[@data-xpath="reportsLinkButton"]')

    def open_page(self) -> None:
        self.page.goto(Urls().base_url)
        self.wait_for_page_load(anchor_selector='//h1[text()="Reports"]')
