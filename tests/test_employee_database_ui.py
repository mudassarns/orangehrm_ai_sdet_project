import pytest
from playwright.sync_api import expect

from orangehrm.config import DASHBOARD_URL
from orangehrm.pages.employee_page import EmployeePage
from orangehrm.pages.login_page import LoginPage


def _database_employee(repository, employee_id):
    rows = repository.find_by_employee_id(employee_id)
    assert len(rows) <= 1, "Employee Id unexpectedly matched multiple database rows."
    return rows[0] if rows else None


def _assert_database_employee(repository, employee, expected_first, expected_last):
    row = _database_employee(repository, employee["employee_id"])
    assert row is not None
    emp_number, employee_id, first_name, middle_name, last_name = row
    assert employee_id == employee["employee_id"]
    assert first_name == expected_first
    assert middle_name == ""
    assert last_name == expected_last
    if employee["employee_number"] is None:
        employee["employee_number"] = emp_number
    else:
        assert emp_number == employee["employee_number"]
    return row


def _assert_absent_from_database(repository, employee_id):
    assert _database_employee(repository, employee_id) is None


@pytest.fixture
def ui_employee(
    page,
    credentials,
    employee_repository,
    employee_persistence_data,
    run_cleanup_preserving_test_failure,
):
    employee = employee_persistence_data
    employee_page = EmployeePage(page)
    login = LoginPage(page)
    login.open()
    login.login(credentials["username"], credentials["password"])
    page.wait_for_url("**/dashboard/**", timeout=10000)
    assert page.url.startswith(DASHBOARD_URL.rsplit("/", 1)[0])

    test_exception = None
    try:
        yield employee_page, employee
    except BaseException as exc:
        test_exception = exc
        raise
    finally:
        if employee["create_attempted"]:
            def cleanup():
                row_data = _database_employee(
                    employee_repository, employee["employee_id"]
                )
                if row_data is None:
                    return
                emp_number, employee_id, first_name, middle_name, last_name = (
                    row_data
                )
                allowed_names = {
                    (employee["first_name"], employee["last_name"]),
                    (
                        employee["updated_first_name"],
                        employee["updated_last_name"],
                    ),
                }
                assert employee_id == employee["employee_id"]
                assert (
                    employee["employee_number"] is None
                    or emp_number == employee["employee_number"]
                )
                assert (first_name, last_name) in allowed_names
                assert middle_name == ""

                employee_page.search_by_employee_id(employee_id)
                row = employee_page.row_by_employee_id(employee_id)
                expect(row).to_have_count(1)
                cells = row.locator(".oxd-table-cell")
                expect(cells.nth(1)).to_have_text(employee_id)
                employee_page.delete_employee(row)
                _assert_absent_from_database(employee_repository, employee_id)

            run_cleanup_preserving_test_failure(test_exception, cleanup)


def _create_employee(page, employee_page, employee):
    employee_page.open_add_employee()
    employee_page.fill_new_employee(
        employee["first_name"], "", employee["last_name"], employee["employee_id"]
    )
    expect(employee_page.create_login_details_checkbox()).not_to_be_checked()
    employee["create_attempted"] = True
    employee_page.save_employee()
    expect(page.get_by_text("Successfully Saved")).to_be_visible()


def test_ui_create_persists_employee_in_database(
    page, ui_employee, employee_repository
):
    employee_page, employee = ui_employee
    _create_employee(page, employee_page, employee)

    row = _assert_database_employee(
        employee_repository,
        employee,
        employee["first_name"],
        employee["last_name"],
    )
    assert row[0] > 0


def test_ui_update_persists_employee_in_database(
    page, ui_employee, employee_repository
):
    employee_page, employee = ui_employee
    _create_employee(page, employee_page, employee)
    original = _assert_database_employee(
        employee_repository,
        employee,
        employee["first_name"],
        employee["last_name"],
    )

    employee_page.search_by_employee_id(employee["employee_id"])
    row = employee_page.row_by_employee_id(employee["employee_id"])
    expect(row).to_have_count(1)
    employee_page.edit_employee(row)
    employee_page.update_employee_name(
        employee["updated_first_name"], "", employee["updated_last_name"]
    )
    expect(page.get_by_text("Successfully Updated")).to_be_visible()

    updated = _assert_database_employee(
        employee_repository,
        employee,
        employee["updated_first_name"],
        employee["updated_last_name"],
    )
    assert updated[0] == original[0]
    assert updated[1] == original[1]


def test_ui_delete_removes_employee_from_database(
    page, ui_employee, employee_repository
):
    employee_page, employee = ui_employee
    _create_employee(page, employee_page, employee)
    created = _assert_database_employee(
        employee_repository,
        employee,
        employee["first_name"],
        employee["last_name"],
    )

    employee_page.search_by_employee_id(employee["employee_id"])
    row = employee_page.row_by_employee_id(employee["employee_id"])
    expect(row).to_have_count(1)
    employee_page.delete_employee(row)
    _assert_absent_from_database(employee_repository, employee["employee_id"])
    employee["create_attempted"] = False
    assert created[0] == employee["employee_number"]
