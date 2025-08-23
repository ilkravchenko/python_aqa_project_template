import calendar
from typing import Optional, Literal

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class AntDayCell(BaseComponent):
    """Represents a single day cell in the Ant Design DatePicker."""

    selector = '//td[contains(@class, "ant-picker-cell-in-view")]'

    def __init__(self, page: Page, selector: str = selector, root: Locator = None):
        super().__init__(root.locator(selector), page)

    @property
    def day(self) -> str:
        return self.element.text

    @property
    def title(self) -> str:
        return self.element.get_attribute("title")

    @property
    def is_enabled(self) -> bool:
        return "ant-picker-cell-disabled" not in self.element.get_attribute("class")

    @property
    def is_selected(self) -> bool:
        return "ant-picker-cell-selected" in self.element.get_attribute("class")

    @property
    def is_today(self) -> bool:
        return "ant-picker-cell-today" in self.element.get_attribute("class")

    def select(self) -> None:
        self.element.click()


class AntDatePicker(BaseComponent):
    """Represents the Ant Design Date Picker component, handling selection of date, time, and quick options."""

    selector = '//div[contains(@class,"ant-picker-dropdown") and not(contains(@class,"hidden"))]'

    def __init__(self, page: Page, selector: str = selector, locator: Optional[Locator] = None):
        super().__init__(locator or page.locator(selector), page)

    @property
    def current_month(self) -> str:
        return self.child_el('//button[contains(@class,"ant-picker-month-btn")]').text

    @property
    def current_year(self) -> str:
        return self.child_el('//button[contains(@class,"ant-picker-year-btn")]').text

    @property
    def previous_month_button(self) -> BaseElement:
        return self.child_el('//button[contains(@class,"ant-picker-header-prev-btn")]')

    @property
    def next_month_button(self) -> BaseElement:
        return self.child_el('//button[contains(@class,"ant-picker-header-next-btn")]')

    @property
    def ok_button(self) -> BaseElement:
        return self.child_el('//button/span[text()="Ok"]/..')

    @property
    def day_cells(self) -> list[AntDayCell]:
        return self.get_list_of_components(AntDayCell.selector, AntDayCell)

    def select_year(self, year: int) -> None:
        """Selects a specific year in the date picker."""
        self.child_el('//button[contains(@class,"ant-picker-year-btn")]').click()
        year_selector = f'//td[@title="{year}"]'
        self.child_el(year_selector).click()

    def select_month(self, month: int) -> None:
        """Selects a specific month in the date picker."""
        self.child_el('//button[contains(@class,"ant-picker-month-btn")]').click()
        month_name = calendar.month_abbr[month]
        month_selector = f'//td/div[text()="{month_name}"]'
        self.child_el(month_selector).click()

    def select_day(self, day: int, month: int, year: int) -> None:
        """Selects a specific day in the date picker."""
        day_selector = f'{AntDayCell.selector}[@title="{year}-{month:02d}-{day:02d}"]'
        day_cell = self.child_el(selector=day_selector, component=AntDayCell)
        assert day_cell.is_enabled, f'Day {day} is not selectable'
        day_cell.select()

    def select_time(self, hour: int, minute: int) -> None:
        """Selects a specific time in the time panel."""

        hour_selector = f'//ul[@class="ant-picker-time-panel-column"][1]//div[text()="{hour:02d}"]'
        minute_selector = f'//ul[@class="ant-picker-time-panel-column"][2]//div[text()="{minute:02d}"]'

        self.child_el(hour_selector).click()
        self.child_el(minute_selector).click()

    def select_date_time(self, day: int, month: int, year: int, hour: int, minute: int) -> None:
        """Selects a specific date and time in the picker."""
        self.select_year(year)
        self.select_month(month)
        self.select_day(day, month, year)
        self.select_time(hour, minute)
        self.ok_button.click()


class AntDatePickerForm(BaseComponent):
    """Represents a date picker form component with label and input field interaction."""

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Optional[Locator] = None):
        if not selector:
            selector = f'//div[contains(@class,"parameter-block")]/div[@data-test="ParameterName-{label}"]/..'
        super().__init__(root.locator(selector), page) if root else super().__init__(page.locator(selector), page)

    @property
    def title(self) -> str:
        return self.child_el('//label').text

    @property
    def input_field(self) -> BaseElement:
        return self.child_el('//input')

    @property
    def value(self) -> str:
        return self.input_field.value

    @property
    def is_enabled(self) -> bool:
        return self.input_field.is_enabled

    @property
    def is_expanded(self) -> bool:
        return self.child_el('//div[contains(@class,"ant-picker-focused")]').is_visible

    @property
    def datepicker(self) -> AntDatePicker:
        return AntDatePicker(self.page)

    @property
    def quick_select_button(self) -> BaseElement:
        return self.child_el('//span[@aria-label="thunderbolt"]/..')

    def expand(self) -> None:
        """Expands the date picker form if it's not already expanded."""
        for _ in range(3):
            if not self.is_expanded:
                self.element.click()
            else:
                break
        self.datepicker.wait_for_visibility()

    def clear(self) -> None:
        """Clears the input field by clicking the clear button."""
        self.input_field.hover()
        self.child_el('//span[@class="ant-picker-clear"]').click()

    def select_date(self, day: int, month: int, year: int) -> None:
        """Selects a specific date."""
        self.expand()
        self.datepicker.select_year(year)
        self.datepicker.select_month(month)
        self.datepicker.select_day(day, month, year)
        self.datepicker.wait_for_invisibility()

    def select_time(self, hour: int, minute: int) -> None:
        """Selects a specific time."""
        self.expand()
        self.datepicker.select_time(hour, minute)
        self.datepicker.wait_for_invisibility()

    def select_date_time(self, day: int, month: int, year: int, select_type: Literal['from', 'to'] = 'from',
                         hour: Optional[int] = 0, minute: Optional[int] = 0) -> None:
        """Selects a specific date and time."""
        self.expand()
        self.datepicker.select_date_time(day, month, year, hour, minute)
        if select_type == 'to':
            self.datepicker.wait_for_invisibility()
            self.find_element('//div[contains(@class,"ant-select-loading")]').raw.nth(-1).wait_for(state="hidden")

    def quick_select(self, option_text: str) -> None:
        """Selects a quick preset date range."""
        self.quick_select_button.click()
        self.find_element(
            f'//li[contains(@class,"ant-dropdown-menu-item")][contains(text(),"{option_text}")]').click()
        self.find_element('//div[contains(@class,"ant-select-loading")]').raw.nth(0).wait_for(state="hidden")
