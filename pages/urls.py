class Urls:

    @property
    def base_url(self) -> str:
        return 'https://base_url'

    @property
    def login_url(self) -> str:
        return f'{self.base_url}/login'

    @property
    def home_url(self) -> str:
        return f'{self.base_url}/home'

    # Other URLs (e.g.)
    @property
    def about_url(self) -> str:
        return f'{self.base_url}/about'


class ReportUrls:

    @property
    def base_url(self) -> str:
        return f'{self.base_url}/reports'

    # Other Report URLs (e.g.)
    @property
    def dashboards_url(self) -> str:
        return f'{self.base_url}/dashboards'
