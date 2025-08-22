from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement
from utils.date_helper import MONTHS_UKR


class DayCell(BaseComponent):
    """
    Represents a single day cell in the date picker. Provides properties to interact with the cell.

    Attributes:
        selector (str): XPath selector to locate day cells that are not outside the current month.
    """

    selector = '//div[contains(@class,"react-datepicker__day--") and not(contains(@class,"outside"))]'

    def __init__(self, page: Page, selector: str = selector, locator: Optional[Locator] = None):
        """
        Initialize the DayCell component.

        Args:
            page (Page): Playwright's Page object for browser interaction.
            selector (str): XPath selector to locate day cells.
        """
        if not locator:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(locator, page)

    @property
    def day(self) -> str:
        """
        Retrieve the day number (text) from the cell.

        Returns:
            str: Day number as a string.
        """
        return self.element.text

    @property
    def title(self) -> str:
        """
        Retrieve the aria-label attribute, used to identify the day's title.

        Returns:
            str: Title of the day (formatted as date string).
        """
        return self.element.get_attribute('aria-label').split(', ')[-1]

    @property
    def is_enabled(self) -> bool:
        """
        Check if the day cell is enabled (clickable).

        Returns:
            bool: True if the cell is enabled, False otherwise.
        """
        return self.element.get_attribute('aria-disabled') == 'false'

    @property
    def is_selected(self) -> bool:
        """
        Check if the day cell is selected.

        Returns:
            bool: True if the cell is selected, False otherwise.
        """
        return '--selected' in self.element.get_attribute('class')

    @property
    def is_today(self) -> bool:
        """
        Check if the day cell represents the current day.

        Returns:
            bool: True if the cell represents today, False otherwise.
        """
        return '--today' in self.element.get_attribute('class')

    def select(self) -> None:
        """
        Click on the day cell to select it.
        """
        self.element.click()


class Datepicker(BaseComponent):
    """
    Represents a date picker component and provides methods to interact with it, such as selecting days, months, and years.

    Attributes:
        selector (str): XPath selector to locate the date picker component.
    """

    selector = '//div[@class="react-datepicker-popper"]'

    def __init__(self, page: Page, selector: str = selector, locator: Optional[Locator] = None):
        """
        Initialize the Datepicker component.

        Args:
            page (Page): Playwright's Page object for browser interaction.
            selector (str): XPath selector to locate the date picker.
            locator (Optional[Locator]): Optionally pass an existing locator for the date picker.
        """
        if not locator:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(locator, page)

    @property
    def current_month(self) -> str:
        """
        Get the name of the currently displayed month.

        Returns:
            str: Current month as a string.
        """
        return self.child_el('//span[@class="react-datepicker__current-month"]').text.strip()

    @property
    def current_year(self) -> str:
        """
        Get the currently displayed year.

        Returns:
            str: Current year as a string.
        """
        return self.child_el('//button[@class="react-datepicker__year-btn"]').text.strip()

    @property
    def previous_month_button(self) -> BaseElement:
        """
        Get the button for navigating to the previous month.

        Returns:
            BaseElement: The previous month button element.
        """
        return self.child_el('//button[@aria-label="Previous Month"]')

    @property
    def next_month_button(self) -> BaseElement:
        """
        Get the button for navigating to the next month.

        Returns:
            BaseElement: The next month button element.
        """
        return self.child_el('//button[@aria-label="Next Month"]')

    @property
    def day_cells(self) -> list[DayCell]:
        """
        Get all the day cells in the current month.

        Returns:
            list[DayCell]: A list of DayCell components.
        """
        return self.get_list_of_components(DayCell.selector, DayCell)

    def select_year(self, year: int, max_attempts: int = 10) -> None:
        """
        Select a specific year in the date picker. Handles years outside the visible range
        by clicking the previous/next year navigation buttons as needed.

        Args:
            year (int): The target year to select.
            max_attempts (int): Maximum number of navigation attempts to prevent infinite loops.
        """
        # First check if the year is already selected
        current_year_btn = self.child_el('//button[@class="react-datepicker__year-btn"]')
        if current_year_btn.text.strip() == str(year):
            return  # Year is already selected, nothing to do

        # Open year selection
        current_year_btn.click()

        # Wait for the year picker to be visible
        self.child_el('//div[@class="react-datepicker__year--container"]').wait_until_visible()

        # Check if the target year is already visible
        year_element = self.child_el(f'//div[@class="react-datepicker__year-text" and text()="{year}"]')
        if year_element.is_visible:
            year_element.click()
            # Wait for year selector to close
            self.child_el('//div[@class="react-datepicker__year--container"]').wait_until_hidden()
            return

        # Try to navigate to the year
        attempts = 0
        while attempts < max_attempts:
            # Get current year range
            year_header = self.child_el('//div[@class="react-datepicker__header react-datepicker-year-header"]')
            current_year_range = year_header.text
            years = current_year_range.split(' - ')
            start_year, end_year = int(years[0]), int(years[1])

            # Check if target year is now in range
            if start_year <= year <= end_year:
                # Year is in range, select it
                year_element = self.child_el(f'//div[@class="react-datepicker__year-text" and text()="{year}"]')
                year_element.click()
                # Wait for year selector to close
                self.child_el('//div[@class="react-datepicker__year--container"]').wait_until_hidden()
                return

            # Determine navigation direction
            if year < start_year:
                # Navigate backward
                prev_btn = self.child_el('//button[@aria-label="Previous Year"]')
                prev_btn.click()
            elif year > end_year:
                # Navigate forward
                next_btn = self.child_el('//button[@aria-label="Next Year"]')
                next_btn.click()

            attempts += 1

        # If we get here, we couldn't find the year after max attempts
        raise ValueError(f"Could not find year {year} in the date picker after {max_attempts} navigation attempts. "
                         f"Current visible range is {start_year} - {end_year}.")

    def select_month_and_year(self, month: int, year: int) -> None:
        """
        Select a specific month and year in the date picker by first selecting the year, then the month.

        Args:
            month (int): The target month to select (1-12).
            year (int): The target year to select.
        """
        # First select the year
        self.select_year(year)

        # Now select the month
        current_month_num = MONTHS_UKR.index(self.current_month.capitalize()) + 1

        if month > current_month_num:
            # Click "Next Month" the required number of times
            for _ in range(month - current_month_num):
                self.next_month_button.click()
        elif month < current_month_num:
            # Click "Previous Month" the required number of times
            for _ in range(current_month_num - month):
                self.previous_month_button.click()

    def select_day(self, day: int) -> None:
        """
        Select a specific day in the date picker.

        Args:
            day (int): The day to select.
        """
        selector = f'{DayCell.selector}[text()="{day}"]'
        day_cell = DayCell(self.page, selector=selector)
        assert day_cell.is_enabled, f'Day {day_cell.title} is not available'
        day_cell.select()

    def select_date(self, day: int, month: int, year: int) -> None:
        """
        Select a specific date (day, month, and year) in the date picker.

        Args:
            day (int): The day to select.
            month (int): The month to select.
            year (int): The year to select.
        """
        self.select_month_and_year(month, year)
        self.select_day(day)
        self.element.wait_until_hidden()


class BaseDatePickerForm(BaseComponent):
    """
    Represents the base form component for a date picker form with label and input field interaction.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Optional[Locator] = None):
        """
        Initialize the BaseDatePickerForm component.

        Args:
            label (str): The label text to locate the date picker form.
            page (Page): Playwright's Page object for browser interaction.
            selector (Optional[str]): XPath selector to locate the form component (default is auto-generated based on the label).
        """
        if not selector:
            selector = f'//div[contains(@class,"mdtuddm-datetime")]/label[contains(text(),"{label}")]/..'
        # Initialize the BaseComponent with the located checkbox element and page
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def title(self) -> str:
        """
        Get the title (label) of the date picker form.

        Returns:
            str: The label of the date picker form.
        """
        return self.child_el('//label').text

    @property
    def is_required(self) -> bool:
        """
        Check if the date picker form field is required.

        Returns:
            bool: True if the field is required, False otherwise.
        """
        return 'field-required' in self.child_el('//label').get_attribute('class')

    @property
    def input_field(self) -> BaseElement:
        """
        Get the input field element of the date picker form.

        Returns:
            BaseElement: The input field element.
        """
        return self.child_el('//input')

    @property
    def value(self) -> str:
        """
        Get the current value in the input field.

        Returns:
            str: The value of the input field.
        """
        return self.input_field.value

    @property
    def is_enabled(self) -> bool:
        """
        Check if the input field is enabled.

        Returns:
            bool: True if the input field is enabled, False otherwise.
        """
        return self.input_field.is_enabled

    @property
    def is_expanded(self) -> bool:
        """
        Check if the date picker is expanded (visible).

        Returns:
            bool: True if the date picker is expanded, False otherwise.
        """
        return self.child_el('//div[contains(@class,"Mui-focused")]').is_visible

    @property
    def datepicker(self) -> Datepicker:
        """
        Get the Datepicker component of the form.

        Returns:
            Datepicker: The Datepicker component instance.
        """
        return Datepicker(self.page)

    def expand(self) -> None:
        """
        Expand the date picker form if it is not already expanded.
        """
        for _ in range(3):
            if not self.is_expanded:
                self.element.click()
            else:
                break
        self.datepicker.wait_for_visibility()

    def select_date(self, day: int, month: int, year: int) -> None:
        """
        Select a specific date in the date picker form.

        Args:
            day (int): The day to select.
            month (int): The month to select.
            year (int): The year to select.
        """
        self.expand()
        self.datepicker.select_date(day, month, year)
        self.datepicker.wait_for_invisibility()

    def select_today(self) -> None:
        self.expand()
        [day for day in self.datepicker.day_cells if day.is_today][0].select()
        self.datepicker.wait_for_invisibility()
