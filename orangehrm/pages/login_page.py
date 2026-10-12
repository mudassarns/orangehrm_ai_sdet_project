from orangehrm.config import DASHBOARD_URL, LOGIN_URL


class LoginPage:
    def __init__(self, page):
        self.page = page

    @property
    def username_input(self):
        return self.page.locator('input[name="username"]')

    @property
    def password_input(self):
        return self.page.locator('input[name="password"]')

    @property
    def submit_button(self):
        return self.page.locator('button[type="submit"]')

    def open(self):
        self.page.goto(LOGIN_URL, wait_until="domcontentloaded")

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()

    def direct_dashboard_access(self):
        self.page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
