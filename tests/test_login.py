import os

import pytest
from playwright.sync_api import expect

LOGIN_URL = "http://localhost:8080/web/index.php/auth/login"
DASHBOARD_URL = "http://localhost:8080/web/index.php/dashboard/index"


@pytest.fixture(scope="session")
def credentials():
    username = os.getenv("ORANGEHRM_USERNAME")
    password = os.getenv("ORANGEHRM_PASSWORD")
    if not username or not password:
        pytest.skip("ORANGEHRM_USERNAME and ORANGEHRM_PASSWORD must be set for valid login tests.")
    return {"username": username, "password": password}


class LoginPage:
    def __init__(self, page):
        self.page = page

    def open(self):
        self.page.goto(LOGIN_URL, wait_until="domcontentloaded")

    def login(self, username, password):
        self.page.locator('input[name="username"]').fill(username)
        self.page.locator('input[name="password"]').fill(password)
        self.page.locator('button[type="submit"]').click()

    def assert_required(self, field_name):
        field_group = self.page.locator(
            ".oxd-input-group"
        ).filter(has=self.page.locator(f'input[name="{field_name}"]'))

        expect(
            field_group.locator(".oxd-input-field-error-message")
        ).to_have_text("Required")
        assert self.page.url == LOGIN_URL

    def assert_invalid_credentials(self):
        self.page.wait_for_selector("text=Invalid credentials", timeout=10000)
        assert self.page.locator("text=Invalid credentials").is_visible()
        assert self.page.url == LOGIN_URL

    def assert_dashboard_visible(self):
        self.page.wait_for_url("**/dashboard/**", timeout=10000)
        assert self.page.url.startswith("http://localhost:8080/web/index.php/dashboard")
        expect(
            self.page.get_by_role("heading", name="Dashboard")
        ).to_be_visible()

    def assert_login_page_visible(self):
        self.page.wait_for_url(LOGIN_URL, timeout=10000)
        self.page.wait_for_selector('input[name="username"]', timeout=10000)
        self.page.wait_for_selector('input[name="password"]', timeout=10000)
        assert self.page.url == LOGIN_URL
        assert self.page.locator('input[name="username"]').is_visible()
        assert self.page.locator('input[name="password"]').is_visible()

    def direct_dashboard_access(self):
        self.page.goto(DASHBOARD_URL, wait_until="domcontentloaded")

    def assert_password_masked(self):
        password_input = self.page.locator("input[type='password']")
        assert password_input.count() == 1
        assert password_input.evaluate("el => el.type") == "password"


@pytest.mark.parametrize(
    "username,password,field_name",
    [
        ("", "Password123", "username"),
        ("validuser", "", "password"),
        ("", "", "both"),
    ],
)
def test_required_fields(page, username, password, field_name):
    login = LoginPage(page)
    login.open()
    login.login(username, password)
    if field_name == "both":
        login.assert_required("username")
        login.assert_required("password")
    else:
        login.assert_required(field_name)


def test_successful_authentication(page, credentials):
    login = LoginPage(page)
    login.open()
    login.login(credentials["username"], credentials["password"])
    login.assert_dashboard_visible()


def test_valid_username_invalid_password(page, credentials):
    login = LoginPage(page)
    login.open()
    login.login(credentials["username"], "wrongpass")
    login.assert_invalid_credentials()


def test_invalid_username_valid_password(page, credentials):
    login = LoginPage(page)
    login.open()
    login.login("baduser", credentials["password"])
    login.assert_invalid_credentials()


def test_invalid_username_invalid_password(page):
    login = LoginPage(page)
    login.open()
    login.login("baduser", "wrongpass")
    login.assert_invalid_credentials()


def test_password_masking(page):
    login = LoginPage(page)
    login.open()
    password = login.page.get_by_role("textbox", name="Password")
    password.fill("Password123")
    login.assert_password_masked()


def test_unauthenticated_dashboard_redirect(page):
    login = LoginPage(page)
    login.direct_dashboard_access()
    login.assert_login_page_visible()
