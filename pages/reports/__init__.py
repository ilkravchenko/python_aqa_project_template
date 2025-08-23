from functools import cached_property

from playwright.sync_api import Page

from pages.reports.reports_page import DashboardPage
from pages.reports.sidebar import Sidebar
from pages.reports.dashboards.info_messages import InformationMessagesDashboard


class ReportsPages:
    """
    Provides access to all pages and components, grouped by logical sections.
    """

    def __init__(self, page: Page):
        self.page = page

    @cached_property
    def sidebar(self) -> Sidebar:
        return Sidebar(self.page)

    @cached_property
    def dashboard_page(self) -> DashboardPage:
        return DashboardPage(self.page)

    @cached_property
    def information_messages_dashboard(self) -> InformationMessagesDashboard:
        return InformationMessagesDashboard(self.page)
