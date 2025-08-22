from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class RadioOption(BaseComponent):
    """
    Represents a single radio button option in a radio group.

    Provides properties and methods to interact with the radio button.
    """

    @property
    def title(self) -> str:
        """
        Get the label or title of the radio button option.

        Returns:
            str: The text of the radio button's label.
        """
        return self.element.text

    @property
    def is_checked(self) -> bool:
        """
        Check if the radio button is currently selected (checked).

        Returns:
            bool: True if the radio button is checked, False otherwise.
        """
        return self.input_field.raw.is_checked() or self.child_el('//span[contains(@class,"Mui-checked")]').is_visible

    @property
    def is_required(self) -> bool:
        """
        Check if the radio button is marked as required.

        Returns:
            bool: True if the radio button is required, False otherwise.
        """
        return 'field-required' in self.element.get_attribute('class')

    @property
    def input_field(self) -> BaseElement:
        """
        Get the input element associated with the radio button.

        Returns:
            BaseElement: The input element of the radio button.
        """
        return self.child_el('//input')

    @property
    def is_enabled(self) -> bool:
        """
        Check if the radio button is enabled (i.e., can be interacted with).

        Returns:
            bool: True if the radio button is enabled, False otherwise.
        """
        return self.input_field.is_enabled

    def check(self) -> None:
        """
        Check (select) the radio button if it is not already checked.
        """
        if not self.is_checked:
            self.input_field.click(force=True)

    def uncheck(self) -> None:
        """
        Uncheck (deselect) the radio button if it is checked.
        """
        if self.is_checked:
            self.input_field.click(force=True)


class BaseRadiobutton(BaseComponent):
    """
    Represents a group of radio buttons.

    Provides methods to select radio buttons by name or index and
    manages a collection of `RadioOption` objects.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Optional[Locator] = None):
        """
        Initialize the radio button group.

        Args:
            label (str): The label of the radio button group.
            page (Page): The Playwright page object used for interaction.
            selector (Optional[str]): An optional custom selector for the radio button group.
                                       If not provided, a default XPath selector based on the label is used.
        """
        if not selector:
            selector = f'//label[contains(text(),"{label}")]/ancestor::div[contains(@class,"formio-component-radioLatest")]'
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def options(self) -> list[RadioOption]:
        """
        Get the list of radio button options in the group.

        Returns:
            list[RadioOption]: A list of `RadioOption` objects representing each radio button option.
        """
        return self.get_list_of_components('//div[@role="radiogroup"]/label', RadioOption)

    @property
    def selected_option(self) -> str:
        selected = [radio.title for radio in self.options if radio.is_checked]
        return selected[0] if selected else None

    def select_by_name(self, name: str) -> None:
        """
        Select a radio button option by its name (label).

        Args:
            name (str): The name (label) of the radio button to select.

        Raises:
            AssertionError: If no radio button with the given name is found.
        """
        self.wait_for_visibility()
        needed_option = [option for option in self.options if option.title == name]
        assert needed_option, f'No radio button with name "{name}"'
        needed_option[0].check()

    def select_by_index(self, index: int) -> None:
        """
        Select a radio button option by its index.

        Args:
            index (int): The index of the radio button to select.
                         Indexing starts from 0 (the first option).
        """
        self.options[index].check()
