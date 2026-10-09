from uuid import uuid4

from playwright.sync_api import expect

from test_login import LoginPage, credentials


def test_successful_add_employee(page, credentials):
    login = LoginPage(page)
    login.open()
    login.login(credentials["username"], credentials["password"])
    login.assert_dashboard_visible()

    page.get_by_role("link", name="PIM").click()
    page.get_by_role("link", name="Add Employee").click()

    unique_suffix = uuid4().hex[:8].upper()
    first_name = "QA"
    middle_name = "MCP"
    last_name = f"Employee{unique_suffix}"
    employee_id = f"QA{unique_suffix}"

    page.get_by_placeholder("First Name").fill(first_name)
    page.get_by_placeholder("Middle Name").fill(middle_name)
    page.get_by_placeholder("Last Name").fill(last_name)
    employee_id_group = page.locator(".oxd-input-group").filter(has_text="Employee Id")
    employee_id_group.locator("input").fill(employee_id)
    page.get_by_role("button", name="Save").click()

    expect(page.get_by_text("Successfully Saved")).to_be_visible()

    page.get_by_role("link", name="PIM").click()
    page.get_by_role("link", name="Employee List").click()
    employee_id_group = page.locator(".oxd-input-group").filter(has_text="Employee Id")
    employee_id_group.locator("input").fill(employee_id)
    page.get_by_role("button", name="Search").click()

    employee_row = page.locator(
        ".oxd-table-body .oxd-table-row"
    ).filter(has_text=employee_id)
    expect(employee_row).to_have_count(1)
    employee_cells = employee_row.locator(".oxd-table-cell")
    expect(employee_cells.nth(1)).to_have_text(employee_id)
    expect(employee_cells.nth(2)).to_have_text(f"{first_name} {middle_name}")
    expect(employee_cells.nth(3)).to_have_text(last_name)
