from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent


class BaseFieldsetComponent(BaseComponent):
    """
    Represents a collapsible fieldset component on a web page, used to encapsulate related
    form elements or information, typically styled with Material UI (MUI) in a React environment.

    This class provides methods to interact with the fieldset, including expanding or collapsing it,
    and to retrieve its title.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None):
        """
        Initialize the BaseFieldsetComponent.

        Args:
            label (str): The label text to identify the fieldset component.
            page (Page): The Playwright Page object to interact with.
            selector (Optional[str]): An optional XPath selector for locating the fieldset.
                                      If not provided, a default selector based on the label is used.
        """
        if not selector:
            # Default selector targeting the fieldset ancestor of a legend with the specified label text
            if '"' in label:
                selector = f"//legend[contains(text(),'{label}')]/ancestor::fieldset[1]"
            else:
                selector = f'//legend[contains(text(),"{label}")]/ancestor::fieldset[1]'
        super().__init__(page.locator(selector), page)

    @property
    def title(self) -> str:
        """
        Retrieve the title text of the fieldset from its legend element.

        Returns:
            str: The title text of the fieldset.
        """
        return self.child_el('//legend').text.strip()

    @property
    def _arrow(self) -> Locator:
        """
        Locate the arrow icon within the legend, which controls the expand/collapse functionality.

        Returns:
            Locator: The locator for the arrow image element within the legend.
        """
        return self.child_el('//legend/img').raw.nth(0)

    @property
    def is_expanded(self) -> bool:
        """
        Check if the fieldset is currently expanded.

        Returns:
            bool: True if the fieldset is expanded; False otherwise.
        """
        # Determine expanded state based on the class attribute of the legend element
        return 'non-collapsed' in self.child_el('//legend').raw.nth(0).get_attribute('class')

    def collapse(self) -> None:
        """
        Collapse the fieldset if it is currently expanded.
        """
        if self.is_expanded:
            self._arrow.click()

    def expand(self, force: bool = False) -> None:
        """
        Expand the fieldset if it is currently collapsed.
        """
        if not self.is_expanded or force:
            self._arrow.click()
