from pages.common.checkbox import BaseCheckbox
from pages.common.datepicker import BaseDatePickerForm
from pages.common.dropdown import BaseDropdown
from pages.common.input import BaseInput
from pages.common.process_form import BaseProcessForm
from pages.common.upload_form import BaseUploadReadForm


class UpdateInfoMessageForm(BaseProcessForm):
    """
    Update Info Message.
    """

    @property
    def information_message_number(self) -> str:
        return BaseInput('Info message number', self.page).value

    @property
    def registration_date(self) -> str:
        return BaseDatePickerForm('Registration date', self.page).value

    @property
    def information_message_status(self) -> str:
        return BaseDropdown('Status', self.page).value

    @property
    def non_resident_flag(self) -> bool:
        return BaseCheckbox('Non resident', self.page).is_checked

    @property
    def phone_number(self) -> str:
        return BaseInput('Phone', self.page).value

    @property
    def email_address(self) -> str:
        return BaseInput('Email', self.page).value

    @property
    def region(self) -> str:
        return BaseInput('Region', self.page).value

    @property
    def city(self) -> str:
        return BaseInput('City', self.page).value

    @property
    def house_number(self) -> str:
        return BaseInput('House', self.page).value

    @property
    def uploaded_documents_viewer(self) -> BaseUploadReadForm:
        return BaseUploadReadForm('See Uploaded documents', self.page)
