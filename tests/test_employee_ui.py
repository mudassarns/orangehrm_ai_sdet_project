import pytest
from playwright.sync_api import expect

from orangehrm.config import DASHBOARD_URL
from orangehrm.pages.employee_page import EmployeePage
from orangehrm.pages.login_page import LoginPage


@pytest.fixture
def employee_record(page, credentials, unique_employee_id):
    employee_page = EmployeePage(page)
    name_suffix = unique_employee_id[2:]
    record = {
        "first_name": f"UiFirst{name_suffix}",
        "last_name": f"UiLast{name_suffix}",
        "employee_id": unique_employee_id,
    }
    create_attempted = False

    try:
        login = LoginPage(page)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_url("**/dashboard/**", timeout=10000)
        assert page.url.startswith(DASHBOARD_URL.rsplit("/", 1)[0])
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        employee_page.open_add_employee()
        employee_page.fill_new_employee(
            record["first_name"], "", record["last_name"], record["employee_id"]
        )
        expect(employee_page.create_login_details_checkbox()).not_to_be_checked()

        create_attempted = True
        employee_page.save_employee()
        expect(page.get_by_text("Successfully Saved")).to_be_visible()
        yield record
    finally:
        if create_attempted:
            confirmation = page.get_by_role("dialog")
            if confirmation.count() == 1:
                expect(confirmation).to_contain_text(
                    "The selected record will be permanently deleted."
                )
                confirmation.get_by_role(
                    "button", name="No, Cancel"
                ).click()

            employee_page.search_by_employee_id(record["employee_id"])
            row = employee_page.row_by_employee_id(record["employee_id"])
            row_count = row.count()
            if row_count > 1:
                raise AssertionError(
                    "Cleanup found multiple rows for the generated Employee Id; "
                    "no employee was deleted."
                )
            if row_count == 1:
                cells = row.locator(".oxd-table-cell")
                if cells.nth(1).inner_text().strip() != record["employee_id"]:
                    raise AssertionError(
                        "Cleanup could not confirm the generated Employee Id; "
                        "no employee was deleted."
                    )
                employee_page.delete_employee(row)
                employee_page.search_by_employee_id(record["employee_id"])
                expect(
                    employee_page.row_by_employee_id(record["employee_id"])
                ).to_have_count(0)


def find_employee_row(employee_page, employee_id):
    employee_page.search_by_employee_id(employee_id)
    row = employee_page.row_by_employee_id(employee_id)
    expect(row).to_have_count(1)
    cells = row.locator(".oxd-table-cell")
    expect(cells.nth(1)).to_have_text(employee_id)
    return row, cells


def test_employee_add_functionality(page, employee_record):
    employee_page = EmployeePage(page)
    _, cells = find_employee_row(employee_page, employee_record["employee_id"])
    expect(cells.nth(2)).to_have_text(employee_record["first_name"])
    expect(cells.nth(3)).to_have_text(employee_record["last_name"])


def test_employee_search_functionality(page, employee_record):
    employee_page = EmployeePage(page)
    row, cells = find_employee_row(employee_page, employee_record["employee_id"])
    expect(row).to_contain_text(employee_record["first_name"])
    expect(row).to_contain_text(employee_record["last_name"])
    expect(cells.nth(1)).to_have_text(employee_record["employee_id"])


def test_employee_edit_functionality(page, employee_record):
    employee_page = EmployeePage(page)
    row, _ = find_employee_row(employee_page, employee_record["employee_id"])
    updated_first_name = f"EditFirst{employee_record['first_name'][-10:]}"
    updated_last_name = f"EditLast{employee_record['last_name'][-10:]}"

    employee_page.edit_employee(row)
    employee_page.update_employee_name(
        updated_first_name, "", updated_last_name
    )
    expect(page.get_by_text("Successfully Updated")).to_be_visible()

    page.reload(wait_until="domcontentloaded")
    _, cells = find_employee_row(employee_page, employee_record["employee_id"])
    expect(cells.nth(1)).to_have_text(employee_record["employee_id"])
    expect(cells.nth(2)).to_have_text(updated_first_name)
    expect(cells.nth(3)).to_have_text(updated_last_name)


def test_employee_delete_functionality(page, employee_record):
    employee_page = EmployeePage(page)
    row, _ = find_employee_row(employee_page, employee_record["employee_id"])

    employee_page.delete_employee(row)
    employee_page.search_by_employee_id(employee_record["employee_id"])
    expect(
        employee_page.row_by_employee_id(employee_record["employee_id"])
    ).to_have_count(0)
