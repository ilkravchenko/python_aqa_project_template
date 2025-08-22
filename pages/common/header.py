from playwright.sync_api import Page

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class UserInfo(BaseComponent):
    """
    A component representing user information in the header.

    It provides properties and methods to interact with the user info dropdown,
    such as expanding/collapsing the dropdown, retrieving the user's name, logging out,
    or opening the user's profile.
    """

    @property
    def user_name(self) -> str:
        """
        Get the user's name displayed in the header.

        Returns:
            str: The user's name.
        """
        return self.child_el('//p').text

    @property
    def _dropdown(self) -> BaseElement:
        """
        Get the dropdown element containing the logout button and other user actions.

        Returns:
            BaseElement: The dropdown element that contains user actions like logout.
        """
        return self.find_element('//li[@data-xpath="logoutButton"]/..')

    @property
    def is_expanded(self) -> bool:
        """
        Check if the dropdown is currently expanded (visible).

        Returns:
            bool: True if the dropdown is visible, False otherwise.
        """
        return self._dropdown.is_visible

    def expand(self) -> None:
        """
        Expand the user info dropdown if it is not already expanded.
        """
        if not self.is_expanded:
            self.child_el('//button').click()

    def collapse(self) -> None:
        """
        Collapse the user info dropdown if it is expanded.
        """
        if self.is_expanded:
            self.child_el('//button').click()

    def logout(self) -> None:
        """
        Expand the dropdown (if not already expanded) and click the logout button
        to log the user out.
        """
        self.expand()
        self.find_element('//li[@data-xpath="logoutButton"]').click()

    def open_profile(self) -> None:
        """
        Expand the dropdown (if not already expanded) and click the profile button
        to open the user's profile page.
        """
        self.expand()
        self.find_element('//li[text()="Профіль"]').click()


class HeaderComponent(BaseComponent):
    """
    A component representing the header section of the page.

    It provides properties and methods to interact with the header elements,
    such as the logo, navigation links, and user information dropdown.
    """

    selector = '//div[@data-xpath="header"]'

    def __init__(self, page: Page, selector: str = selector):
        """
        Initialize the HeaderComponent with the page and its selector.

        Args:
            page (Page): The Playwright Page instance.
            selector (str): The XPath selector for the header. Defaults to a predefined XPath for the header.
        """
        super().__init__(page.locator(selector), page)

    @property
    def logo(self) -> BaseElement:
        """
        Get the logo element in the header.

        Returns:
            BaseElement: The element representing the logo, linking to the home page.
        """
        return self.child_el('//div[contains(@class,"MuiToolbar-root")]/a[@href="/logo"]')

    @property
    def links(self) -> list[BaseElement]:
        """
        Get all navigation links in the header.

        Returns:
            list[BaseElement]: A list of BaseElement objects representing the header's navigation links.
        """
        return self.child_elements('//div[@data-xpath="headerLinks"]/a')

    @property
    def user_info(self) -> UserInfo:
        """
        Get the UserInfo component that interacts with the user dropdown in the header.

        Returns:
            UserInfo: The UserInfo component instance.
        """
        return UserInfo(self.page.locator('//div[@data-xpath="headerUserInfo"]'), self.page)

    def open_link_by_text(self, link_text: str) -> None:
        """
        Open a link in the header by matching its visible text.

        Args:
            link_text (str): The visible text of the link to open.

        Raises:
            ValueError: If no link with the given text is found.
        """
        needed_link = [link for link in self.links if link.text == link_text]
        if not needed_link:
            raise ValueError(f'No link with name - {link_text}')
        needed_link[0].click()
