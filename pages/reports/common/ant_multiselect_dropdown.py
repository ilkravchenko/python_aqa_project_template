from typing import Optional, Union

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent


class SelectedOption(BaseComponent):
    """Represents a selected option inside the multi-select dropdown."""

    @property
    def name(self) -> str:
        """Get the text of the selected option."""
        return self.child_el('//span[contains(@class, "ant-select-selection-item-content")]').text

    def delete(self) -> None:
        """Remove the selected option by clicking the close button."""
        self.child_el('//span[contains(@class, "anticon-close")]').click()
        for element in self.find_elements('//div[contains(@class,"ant-select-loading")]', wait=False):
            element.raw.wait_for(state="hidden")


class DropdownOption(BaseComponent):
    """Represents an option inside the dropdown list."""

    @property
    def name(self) -> str:
        """Get the text of the dropdown option."""
        return self.child_el('//div[contains(@class, "ant-select-item-option-content")]').text

    @property
    def is_selected(self) -> bool:
        """Check whether the option is selected."""
        return 'ant-select-item-option-selected' in self.element.get_attribute('class')

    def toggle_selection(self) -> None:
        """Click to select/unselect the option."""
        self.element.click()


class AntMultiSelectDropdown(BaseComponent):
    """Handles interactions with an Ant Design Multi-Select dropdown."""

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Locator = None):
        """Initialize the dropdown based on the label."""
        if not selector:
            selector = f'//div[@data-test="ParameterBlock-{label}"]//div[contains(@class, "ant-select-multiple")]'
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def selected_options(self) -> list[SelectedOption]:
        """Get all currently selected options."""
        return self.get_list_of_components('//span[@class="ant-select-selection-item"]',
                                           component=SelectedOption)

    @property
    def selected_values(self) -> list[str]:
        """Get a list of selected values (text)."""
        return [option.name for option in self.selected_options]

    @property
    def is_expanded(self) -> bool:
        """
        Check if the dropdown is currently expanded.

        Returns:
            bool: True if expanded, False otherwise.
        """
        return ('ant-select-open' in self.element.get_attribute('class') and
                self.find_element(self._expanded_dropdown_selector).is_visible)

    def expand(self) -> None:
        """Expand the dropdown if it's not already expanded."""
        if not self.is_expanded:
            self.element.click()
            self.wait_for_dropdown_expansion()

    def collapse(self) -> None:
        """Collapse the dropdown if it's currently expanded."""
        if self.is_expanded:
            self.child_el('//span[@aria-label="search"]').click(force=True)
            self.wait_for_dropdown_collapse()

    @property
    def _expanded_dropdown_selector(self) -> str:
        """Get the XPath of the expanded dropdown list."""
        return "//div[contains(@class, 'ant-select-dropdown') and not(contains(@class, 'hidden'))]"

    def wait_for_dropdown_expansion(self) -> None:
        """
        Wait for the dropdown to be expanded.
        """
        self.find_element(self._expanded_dropdown_selector).wait_until_visible()

    def wait_for_dropdown_collapse(self) -> None:
        """
        Wait for the dropdown to be collapsed.
        """
        self.find_element(self._expanded_dropdown_selector).wait_until_hidden()

    def select_options(self, options_to_select: Union[list[str], str],
                       remove_previous: bool = True) -> 'AntMultiSelectDropdown':
        """Select an option from the dropdown."""
        if isinstance(options_to_select, str):
            options_to_select = [options_to_select]

        if remove_previous:
            for selected_option in self.selected_options:
                selected_option.delete()

        self.page.wait_for_load_state(state='networkidle')
        self.page.wait_for_load_state(state='domcontentloaded')
        self.expand()
        selector = f"{self._expanded_dropdown_selector}//div[contains(@class, ' ant-select-item-option')]"
        options = [DropdownOption(locator=locator.raw, page=self.page) for locator in self.find_elements(selector)]

        for option in options_to_select:
            option_to_select = next((opt for opt in options if opt.name == option), None)
            if option_to_select:
                option_to_select.toggle_selection()
            else:
                raise ValueError(f"Option '{option}' not found in dropdown.")

        self.collapse()
        self.wait_for_page_load()
        for element in self.find_elements('//div[contains(@class,"ant-select-loading")]', wait=False):
            element.raw.wait_for(state="hidden")
        self.page.wait_for_load_state(state='networkidle')  # Ensure all network requests are idle
        self.page.wait_for_load_state(state='domcontentloaded')  # Ensure DOM is fully loaded
        return self

    def unselect_option(self, option_text: str) -> None:
        """Unselect an option that is already selected."""
        option_to_remove = next((opt for opt in self.selected_options if opt.name == option_text), None)
        if option_to_remove:
            option_to_remove.delete()
            self.wait_for_page_load()
        else:
            raise ValueError(f"Option '{option_text}' is not currently selected.")

    def get_options(self) -> list[str]:
        """Retrieve a list of available options in the dropdown."""
        self.expand()
        option_locators = self.get_list_of_components(
            f"{self._expanded_dropdown_selector}//div[contains(@class, 'ant-select-item-option')]",
            component=DropdownOption
        )
        return [option.name for option in option_locators]
