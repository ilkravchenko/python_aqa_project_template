from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class ApplyChangesButton(BaseComponent):
    """
    Class representing the apply changes button on the dashboard.

    This class provides methods to interact with the apply changes button,
    such as clicking the button, waiting until it is hidden, and retrieving its text and applied filters count.
    """

    def __init__(self, selector: str, page: Page, root: Locator = None):
        """
        Initialize the ApplyChangesButton.

        Args:
            selector (str): The selector for the apply changes button.
            page (Page): The Playwright page object.
            root (Locator, optional): The root locator. Defaults to None.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(root.locator(selector), page)

    def click(self) -> None:
        """
        Click the apply changes button.
        """
        self.element.click()

    def hide_tooltip(self) -> None:
        """
        Hide the tooltip of the apply changes button.

        When changes are made to filters, a tooltip appears above the apply changes button
        which can potentially overlap other filter elements. This method moves the mouse
        away to hide that tooltip.
        """
        self.element.hover()
        self.page.mouse.move(0, 0)

    def wait_until_hidden(self) -> None:
        """
        Wait until the apply changes button is hidden.
        """
        self.child_el('//ancestor::div[1][@data-show="true"]').wait_until_hidden()

    @property
    def text(self) -> str:
        """
        Retrieve the text of the apply changes button.

        Returns:
            str: The text of the apply changes button.
        """
        return self.child_el('//span[text()]').text

    @property
    def applied_filters(self) -> int:
        """
        Retrieve the count of applied filters.

        Returns:
            int: The count of applied filters.
        """
        locator = self.child_el('//p[@class="ant-scroll-number-only-unit current"]')
        return int(locator.text) if locator.is_visible else 0


class DashboardFilters(BaseComponent):
    """
    Class for interacting with dashboard filters on the report platform.

    This class provides properties and methods to interact with the dashboard filters,
    such as applying filters and waiting for the filters to be applied.
    """
    selector = '//div[@data-test="DashboardParameters"]'

    @property
    def apply_changes_button(self) -> ApplyChangesButton:
        """
        Retrieve the apply changes button element.

        Returns:
            ApplyChangesButton: The button element to apply changes.
        """
        return self.child_el('//div[@data-test="ParameterApplyButton"]//button', component=ApplyChangesButton)

    @property
    def update_results_button(self) -> BaseElement:
        """
        Retrieve the update results button element.

        Returns:
            BaseElement: The button element to update results.
        """
        return self.find_element('//button/span[text()="Update"]/..')

    def update_table(self) -> None:
        """
        Click the update results button to refresh the table.
        """
        self.update_results_button.click()
        self.wait_until_refresh()

    def wait_until_refresh(self) -> None:
        """
        Wait until the refresh icon is hidden, indicating that the refresh is complete.
        """
        self.page.wait_for_load_state(state='networkidle', timeout=60000)  # Ensure all network requests are idle
        self.page.wait_for_load_state(state='domcontentloaded')  # Ensure DOM is fully loaded
        self.update_results_button.raw.locator('//i[contains(@class,"zmdi-hc-spin")]').wait_for(state="hidden",
                                                                                                timeout=60000)
        self.page.wait_for_load_state(state='networkidle')  # Ensure all network requests are idle
        self.page.wait_for_load_state(state='domcontentloaded')  # Ensure DOM is fully loaded

    def apply_filters(self) -> None:
        """
        Apply the selected filters and wait until the changes are applied and the refresh is complete.
        """
        self.wait_for_filters()
        self.apply_changes_button.click()
        self.apply_changes_button.wait_until_hidden()
        self.wait_until_refresh()

    def wait_for_filters(self) -> None:
        """
        Wait until the filter loading indicators are hidden, indicating that the filters are loaded.
        """
        for element in self.find_elements('//div[contains(@class,"ant-select-loading")]', wait=False):
            element.raw.wait_for(state="hidden")
        self.page.wait_for_load_state(state='networkidle')  # Ensure all network requests are idle
        self.page.wait_for_load_state(state='domcontentloaded')  # Ensure DOM is fully loaded
