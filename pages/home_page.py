from pages.common.base_element import BaseElement
from pages.common.base_page import BasePage
from pages.urls import Urls


class HomePage(BasePage):
    @property
    def available_processes_link(self) -> BaseElement:
        return self.find_element('//h2//a[@href="process-list"]')

    @property
    def available_processes_count(self) -> int:
        return int(self.find_element('//div[@data-xpath="processDefinitionMenuOption"]//h1').text)

    @property
    def my_processes_link(self) -> BaseElement:
        return self.find_element('//h2//a[@href="process-list"]')

    @property
    def my_processes_count(self) -> int:
        return int(self.find_element('//div[@data-xpath="processActiveMenuOption"]//h1').text)

    @property
    def my_tasks_link(self) -> BaseElement:
        return self.find_element('//h2//a[@href="/user-tasks-list"]')

    @property
    def my_tasks_count(self) -> int:
        return int(self.find_element('//div[@data-xpath="taskMenuOption"]//h1').text)

    @property
    def reports_link(self) -> BaseElement:
        return self.find_element('//h2//a[@href="/reports-list"]')

    def open_page(self) -> None:
        self.page.goto(Urls().base_url)
        self.wait_for_page_load()
