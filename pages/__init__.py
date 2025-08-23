from functools import cached_property

from playwright.sync_api import Page

from pages.available_processes.info_message.search_form import SearchInfoMessageForm
from pages.available_processes.info_message.update_info_message_form import UpdateInfoMessageForm
# Common Pages
from pages.common.header import HeaderComponent
from pages.common.notifications import Notifications
from pages.common.validation_message_component import ValidationMessages
# Top-level Pages
from pages.home_page import HomePage
from pages.login_page import LoginPage, AuthPage
from pages.messages import MessagesPage
from pages.reports_page import ReportsPage


class AvailableProcessesAdminInfoMessage:

    def __init__(self, page: Page):
        self.page = page

    @cached_property
    def search_info_message_form(self) -> SearchInfoMessageForm:
        return SearchInfoMessageForm(self.page)

    @cached_property
    def update_info_message_form(self) -> UpdateInfoMessageForm:
        return UpdateInfoMessageForm(self.page)





class Pages:
    """
    Provides access to all pages and components, grouped by logical sections.
    """

    def __init__(self, page: Page):
        self.page = page

    # Top-level pages
    @cached_property
    def login_page(self) -> LoginPage:
        return LoginPage(self.page)

    @cached_property
    def auth_page(self) -> AuthPage:
        return AuthPage(self.page)

    @cached_property
    def home_page(self) -> HomePage:
        return HomePage(self.page)

    @cached_property
    def reports_page(self) -> ReportsPage:
        return ReportsPage(self.page)

    @cached_property
    def messages_page(self) -> MessagesPage:
        return MessagesPage(self.page)

    # Other pages
    @cached_property
    def available_processes_admin_info_message(self) -> AvailableProcessesAdminInfoMessage:
        return AvailableProcessesAdminInfoMessage(self.page)

    # Common components
    @cached_property
    def header(self) -> HeaderComponent:
        return HeaderComponent(self.page)

    @cached_property
    def notifications(self) -> Notifications:
        return Notifications(self.page)

    @cached_property
    def validation_messages(self) -> ValidationMessages:
        return ValidationMessages(self.page)
