from pages.common.base_element import BaseElement
from pages.common.base_page import BasePage


class BaseProcessForm(BasePage):
    """
    A base class for handling common form actions within a process form page.

    This class provides properties for accessing frequently used buttons in process forms,
    such as cancel, continue, back, and save buttons.
    """

    @property
    def cancel_button(self) -> BaseElement:
        """
        Locate and return the 'Cancel' button element on the form.

        Returns:
            BaseElement: The 'Cancel' button element.
        """
        return self.find_element('//button[contains(text(),"Cancel")] | //button/span[contains(text(),"Cancel")]')

    @property
    def continue_button(self) -> BaseElement:
        """
        Locate and return the 'Continue' button element on the form.

        Returns:
            BaseElement: The 'Continue' button element.
        """
        return self.find_element('//button[contains(text(),"Continue")]')

    @property
    def back_button(self) -> BaseElement:
        """
        Locate and return the 'Back' button element on the form.

        Supports locating the button by text inside either a `span` or directly within `button`.

        Returns:
            BaseElement: The 'Back' button element.
        """
        return self.find_element('//button/span[contains(text(),"Back")] | //button[contains(text(),"Back")]')

    @property
    def save_changes_button(self) -> BaseElement:
        """
        Locate and return the 'Save Changes' button element on the form.

        Returns:
            BaseElement: The 'Save Changes' button element.
        """
        return self.find_element('//button/span[text()="Save changes"]')
