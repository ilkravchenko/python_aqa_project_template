import os
import time
from random import uniform

from playwright._impl._errors import TimeoutError

from pages import Pages
from pages.urls import Urls
from tests.fixtures.clean_up_fixtures import *
from tests.fixtures.creation_fixtures import *


fixtures = CREATION, CLEAN_UP


@pytest.fixture(scope="session")
def login(page):
    """
    Automate the login process.
    """
    pages = Pages(page)
    if page.url != Urls().home_url:
        for _ in range(3):
            try:
                pages.login_page.open_page()
                break
            except TimeoutError:
                time.sleep(uniform(0.5, 3))
        else:
            pages.login_page.open_page()
        pages.login_page.login_button.click()
        pages.auth_page.wait_for_page_load()
        # # # # # # # # # # # # # # # # # # # #
        #     SOME MANIPULATION FOR LOGIN     #
        # # # # # # # # # # # # # # # # # # # #
        pages.auth_page.signature_button.click()
    else:
        pages.home_page.reload()
    with pages.home_page.catch_response('**/userinfo**', timeout=30000) as response:
        pages.home_page.wait_for_page_load()
        os.environ['user_name'] = response.value.json()['user_name']
    # Get session cookie
    session_token = [cookie['value'] for cookie in page.context.cookies() if cookie['name'] == 'session'][0]
    os.environ['SESSION'] = session_token
    os.environ['BROWSER_VERSION'] = f'{page.context.browser.version.split(".")[0]}.0.0.0'
