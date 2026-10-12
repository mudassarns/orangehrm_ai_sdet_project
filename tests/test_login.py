import pytest
from playwright.sync_api import expect

from orangehrm.config import DASHBOARD_URL, LOGIN_URL
from orangehrm.pages.login_page import LoginPage


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
        field_names = ("username", "password")
    else:
        field_names = (field_name,)
    for field in field_names:
        field_group = page.locator(".oxd-input-group").filter(
            has=page.locator(f'input[name="{field}"]')
        )
        expect(
            field_group.locator(".oxd-input-field-error-message")
        ).to_have_text("Required")
        assert page.url == LOGIN_URL


def test_successful_authentication(page, credentials):
    login = LoginPage(page)
    login.open()
    login.login(credentials["username"], credentials["password"])
    page.wait_for_url("**/dashboard/**", timeout=10000)
    assert page.url.startswith(DASHBOARD_URL.rsplit("/", 1)[0])
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()


def test_valid_username_invalid_password(page, credentials):
    login = LoginPage(page)
    login.open()
    login.login(credentials["username"], "wrongpass")
    page.wait_for_selector("text=Invalid credentials", timeout=10000)
    assert page.locator("text=Invalid credentials").is_visible()
    assert page.url == LOGIN_URL


def test_invalid_username_valid_password(page, credentials):
    login = LoginPage(page)
    login.open()
    login.login("baduser", credentials["password"])
    page.wait_for_selector("text=Invalid credentials", timeout=10000)
    assert page.locator("text=Invalid credentials").is_visible()
    assert page.url == LOGIN_URL


def test_invalid_username_invalid_password(page):
    login = LoginPage(page)
    login.open()
    login.login("baduser", "wrongpass")
    page.wait_for_selector("text=Invalid credentials", timeout=10000)
    assert page.locator("text=Invalid credentials").is_visible()
    assert page.url == LOGIN_URL


def test_password_masking(page):
    login = LoginPage(page)
    login.open()
    login.password_input.fill("Password123")
    assert login.password_input.count() == 1
    assert login.password_input.evaluate("el => el.type") == "password"


def test_unauthenticated_dashboard_redirect(page):
    login = LoginPage(page)
    login.direct_dashboard_access()
    page.wait_for_url(LOGIN_URL, timeout=10000)
    page.wait_for_selector('input[name="username"]', timeout=10000)
    page.wait_for_selector('input[name="password"]', timeout=10000)
    assert page.url == LOGIN_URL
    assert login.username_input.is_visible()
    assert login.password_input.is_visible()
