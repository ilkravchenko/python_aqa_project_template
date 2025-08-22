from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement
from pages.common.base_page import BasePage
from pages.urls import Urls


class LoginPage(BasePage):

    @property
    def login_button(self) -> BaseElement:
        return self.find_element('//button[@data-xpath="loginButton"]')

    def open_page(self) -> None:
        self.page.goto(Urls().login_url)
        self.wait_for_page_load('//button[@data-xpath="loginButton"]')


class AuthPage(BasePage):

    @property
    def _iframe(self):
        return self.page.frame_locator('//iframe[@id="sign-widget"]')

    @property
    def version(self) -> str:
        return self.find_element(self._iframe.locator('//div[@id="bottomBlock"]/label[2]')).text

    @property
    def signature_button(self) -> BaseElement:
        return self.find_element((self._iframe.locator('//div[@class="MenuItem"]/span[text()="Sign"]')))
