from pages.common.base_page import BasePage
from pages.reports.common.ant_datepicker import AntDatePickerForm
from pages.reports.common.ant_dropdown import AntDropdown
from pages.reports.common.ant_multiselect_dropdown import AntMultiSelectDropdown
from pages.reports.common.ant_table import AntTable, AntRow
from pages.reports.common.dashboard_filters import DashboardFilters


class InformationMessageRow(AntRow):
    """Represents a row in the Information Messages table."""

    @property
    def index(self) -> str:
        """Return № з.п. (Index)."""
        return self.child_el('//td[1]').text

    @property
    def message_number(self) -> str:
        """(Information Message Number)."""
        return self.child_el('//td[2]/div').text

    @property
    def message_status(self) -> str:
        """(Information Message Status)."""
        return self.child_el('//td[3]/div').text

    @property
    def registration_date(self) -> str:
        """(Registration Date)."""
        return self.child_el('//td[4]').text

    @property
    def property_type(self) -> str:
        """(Property Type)."""
        return self.child_el('//td[5]/div').text


class InformationMessagesTable(AntTable):
    @property
    def rows(self) -> list[InformationMessageRow]:
        return self.get_list_of_components(InformationMessageRow.selector, InformationMessageRow)


class InformationMessagesFilters(DashboardFilters):
    """Represents the filters section in the Information Messages dashboard."""

    @property
    def registration_date_picker(self) -> AntDatePickerForm:
        """Date range picker for (Registration Date)."""
        return AntDatePickerForm("Created_date", self.page)

    @property
    def status_dropdown(self) -> AntDropdown:
        """Dropdown for (Information Message Status)."""
        return AntDropdown("status", self.page)

    @property
    def property_type_dropdown(self) -> AntMultiSelectDropdown:
        """Multi-select dropdown for (Property Type)."""
        return AntMultiSelectDropdown("type_name", self.page)


class InformationMessagesDashboard(BasePage):
    """Dashboard for Information Messages list and filters."""

    @property
    def table(self) -> InformationMessagesTable:
        return InformationMessagesTable(self.page)

    @property
    def filters(self) -> InformationMessagesFilters:
        return InformationMessagesFilters(self.page.locator(InformationMessagesFilters.selector), self.page)
