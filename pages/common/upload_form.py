import time
from typing import Optional

from playwright.sync_api import Page, Locator

from pages.common.base_component import BaseComponent
from pages.common.base_element import BaseElement


class InvalidUploadedFile(BaseComponent):
    """
    Represents an invalid uploaded file component in the UI. It provides properties to retrieve the file's
    name and size, as well as the ability to remove the file from the UI.

    Properties:
        name (str): Returns the name of the uploaded file.
        size (str): Returns the size of the uploaded file.

    Methods:
        remove (): Removes the uploaded file by clicking the remove button.
    """

    @property
    def name(self) -> str:
        """
        Get the name of the uploaded file.

        Returns:
            str: The name of the file as displayed in the UI.
        """
        return self.child_el('//div[contains(@class,"fileName")]').text

    @property
    def size(self) -> str:
        """
        Get the size of the uploaded file.

        Returns:
            str: The size of the file as displayed in the UI.
        """
        return self.child_el('//div[contains(@class,"fileSize")]').text

    def remove(self) -> None:
        """
        Removes the uploaded file by clicking the remove icon.
        """
        self.child_el('//i[@ref="fileStatusRemove"]').click()


class UploadedFile(BaseComponent):
    """
    Represents an uploaded file component in the UI. It provides properties to retrieve the file's
    name and size, as well as the ability to remove the file from the UI.

    Properties:
        name (str): Returns the name of the uploaded file.
        size (str): Returns the size of the uploaded file.

    Methods:
        remove (): Removes the uploaded file by clicking the remove button.
    """

    @property
    def name(self) -> str:
        """
        Get the name of the uploaded file.

        Returns:
            str: The name of the file as displayed in the UI.
        """
        return self.child_el('//a[@ref="fileLink"]').text

    @property
    def size(self) -> str:
        """
        Get the size of the uploaded file.

        Returns:
            str: The size of the file as displayed in the UI.
        """
        return self.child_el('//div[contains(text()," kB")]').text

    def remove(self) -> None:
        """
        Removes the uploaded file by clicking the remove icon.
        """
        self.child_el('//i[@ref="removeLink"]').click()
        self.element.wait_until_hidden()
        time.sleep(0.2)

    def download(self) -> None:
        self.child_el('//a[@ref="fileLink"]').click()


class BaseUploadForm(BaseComponent):
    """
    Represents a base upload form component, which allows uploading files and accessing details
    about the uploaded files.

    Args:
        label (str): The label text used to identify the upload form.
        page (Page): The Playwright page instance used to interact with the UI.
        selector (Optional[str]): Optional custom selector to locate the upload form. If not provided,
                                  a default selector based on the label will be used.

    Properties:
        title (str): The title or label of the upload form.
        is_required (bool): Checks whether the form input is marked as required.
        input_field (BaseElement): Represents the input field where files are uploaded.
        upload_link (BaseElement): Represents the "browse" link for uploading files.
        uploaded_files (list[UploadedFile]): List of uploaded files.

    Methods:
        upload_file(file_paths: list[str]): Uploads one or more files using the file input field.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Optional[Locator] = None):
        """
        Initialize the upload form component by locating it via the label or an optional selector.

        Args:
            label (str): The label used to identify the form.
            page (Page): The Playwright page instance.
            selector (Optional[str]): Optional custom selector for locating the form.
        """
        if not selector:
            selector = f'//div[@ref="fileDrop"]/../span[contains(text(),"{label}")]/..'
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    @property
    def title(self) -> str:
        """
        Get the title or label of the upload form.

        Returns:
            str: The title or label of the form.
        """
        return self.child_el('//label').text

    @property
    def is_required(self) -> bool:
        """
        Check if the form's input field is marked as required.

        Returns:
            bool: True if the input field is required, otherwise False.
        """
        return 'field-required' in self.child_el('//span').get_attribute('class')

    @property
    def input_field(self) -> BaseElement:
        """
        Access the input field element of the form.

        Returns:
            BaseElement: The input field element where files are uploaded.
        """
        return self.child_el('//input')

    @property
    def upload_link(self) -> BaseElement:
        """
        Access the "browse" link for uploading files.

        Returns:
            BaseElement: The browse link element.
        """
        return self.child_el('//a[@class="browse"]')

    @property
    def validation_error(self) -> BaseElement:
        """
        Access the validation error element of the form.

        This property locates and returns the element that displays validation errors
        in the form. The element is identified by its CSS classes.

        Returns:
            BaseElement: The element representing the validation error message.
        """
        return self.child_el('//div[@class="alert alert-danger bg-error"]')

    @property
    def required_error(self) -> BaseElement:
        """
        Access the required error element of the form.

        This property locates and returns the element that displays validation errors
        in the form. The element is identified by its CSS classes.

        Returns:
            BaseElement: The element representing the validation error message.
        """
        return self.child_el('//div[@class="formio-errors invalid-feedback"]')

    @property
    def uploaded_files(self) -> list[UploadedFile]:
        """
        Get the list of uploaded files.

        Returns:
            list[UploadedFile]: A list of UploadedFile objects representing the uploaded files.
        """
        return self.get_list_of_components('//li[@class="list-group-item"]', UploadedFile)

    @property
    def description(self) -> str:
        """
        Retrieve the description text of the upload form.

        This property locates and returns the text content of the description element
        within the upload form. The description is typically displayed as a muted text
        below the form input field.

        Returns:
            str: The description text of the upload form.
        """
        return self.child_el('//div[@class="form-text text-muted"]').text

    @property
    def invalid_uploaded_files(self) -> list[InvalidUploadedFile]:
        """
        Get the list of invalid uploaded files.

        This property locates and returns a list of InvalidUploadedFile objects
        representing the invalid files in the upload form.

        Returns:
            list[InvalidUploadedFile]: A list of InvalidUploadedFile objects.
        """
        return self.get_list_of_components('//div[@class="file"]', InvalidUploadedFile)

    def wait_for_files(self):
        """
        Wait until the files in the form become visible.
        """
        self.child_el('//li[@class="list-group-item"]').raw.nth(0).wait_for(state='visible')
        return self

    def upload_file(self, file_paths: list[str]) -> None:
        """
        Upload one or more files using the file input field.

        Args:
            file_paths (list[str]): A list of file paths to be uploaded.
        """
        for file_path in file_paths:
            # Expecting a file chooser to appear when clicking the upload link
            with self.page.expect_file_chooser() as fc_info:
                self.upload_link.click()

            # Once the file chooser is opened, set the file(s) to be uploaded
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)
            time.sleep(0.5)
            self.find_element('//div[@role="progressbar"]').wait_until_hidden()


class BaseUploadReadForm(BaseComponent):
    """
    Represents a read-only upload form component, typically used for viewing uploaded files
    and accessing related details.

    Args:
        label (str): The label text used to identify the upload form.
        page (Page): The Playwright page instance used to interact with the UI.
        selector (Optional[str]): Optional custom selector to locate the upload form. If not provided,
                                  a default selector based on the label will be used.

    Properties:
        title (str): The title or label of the upload form.
        is_required (bool): Checks whether the form input is marked as required.
        uploaded_files (list[UploadedFile]): List of uploaded files available for reading.
    """

    def __init__(self, label: str, page: Page, selector: Optional[str] = None, root: Optional[Locator] = None):
        """
        Initialize the read-only upload form component by locating it via the label or an optional selector.

        Args:
            label (str): The label used to identify the form.
            page (Page): The Playwright page instance.
            selector (Optional[str]): Optional custom selector for locating the form.
        """
        if not selector:
            selector = f'//div[contains(@class,"mdtuddm-file")]/span[contains(text(),"{label}")]/..'
        if not root:
            super().__init__(page.locator(selector), page)
        else:
            super().__init__(root.locator(selector), page)

    def __bool__(self) -> bool:
        """
        Determines the “truthfulness” of a component by checking its visibility on the page.
        """
        try:
            return self.root.is_visible(timeout=1000)
        except Exception:
            return False

    @property
    def title(self) -> str:
        """
        Get the title or label of the upload form.

        Returns:
            str: The title or label of the form.
        """
        return self.child_el('//label').text

    @property
    def is_required(self) -> bool:
        """
        Check if the form's input field is marked as required.

        Returns:
            bool: True if the input field is required, otherwise False.
        """
        return 'field-required' in self.child_el('//label').get_attribute('class')

    @property
    def uploaded_files(self) -> list[UploadedFile]:
        """
        Get the list of uploaded files.

        Returns:
            list[UploadedFile]: A list of UploadedFile objects representing the uploaded files.
        """
        return self.get_list_of_components('//li[@class="list-group-item"]', UploadedFile)

    def wait_for_files(self):
        """
        Wait until the files in the form become visible.
        """
        self.child_el('//li[@class="list-group-item"]').raw.nth(0).wait_for(state='visible')
        return self
