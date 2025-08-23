from pages.common.checkbox import BaseCheckbox
from pages.common.dropdown import BaseDropdown
from pages.common.input import BaseInput
from pages.common.process_form import BaseProcessForm
from pages.common.radio_button import BaseRadiobutton


class SearchInfoMessageForm(BaseProcessForm):
    """
    Look for Info message
    """

    @property
    def search_by_radiobutton(self) -> BaseRadiobutton:
        return BaseRadiobutton('Search by', self.page, selector='(//label[contains(text(),"Search by")]/..)[1]')

    @property
    def address_search_radiobutton(self) -> BaseRadiobutton:
        return BaseRadiobutton('Address search', self.page)

    @property
    def number_search_radiobutton(self) -> BaseRadiobutton:
        return BaseRadiobutton('Number of Info message', self.page)

    @property
    def information_message_dropdown(self) -> BaseDropdown:
        return BaseDropdown('Choose Info message', self.page)

    @property
    def region_dropdown(self) -> BaseDropdown:
        return BaseDropdown("Region", self.page)

    @property
    def district_dropdown(self) -> BaseDropdown:
        return BaseDropdown("District", self.page)

    @property
    def outside_settlement_checkbox(self) -> BaseCheckbox:
        return BaseCheckbox("Outside settlement", self.page)

    @property
    def building_number_input(self) -> BaseInput:
        return BaseInput("Building number", self.page)

