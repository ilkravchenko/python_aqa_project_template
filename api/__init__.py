import os
from functools import cached_property


class APIs:
    def __init__(self, session_token: str = None):
        self.session_token = session_token if session_token else os.getenv('SESSION_TOKEN')

    # List of cached_property for APIs
    @cached_property
    def test_user_api(self) -> TestUserApi:
        return TestUserApi(self.session_token)

    @cached_property
    def another_test_api(self) -> AnotherTestApi:
        return AnotherTestApi(self.session_token)
