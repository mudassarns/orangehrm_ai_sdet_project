import pytest
from playwright.sync_api import Page

from orangehrm.api.employees import EmployeeApi
from orangehrm.config import DASHBOARD_URL
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


@pytest.fixture
def api_employee(
    page: Page,
    credentials: dict,
    employee_repository,
    employee_persistence_data,
    run_cleanup_preserving_test_failure,
):
    login = LoginPage(page)
    login.open()
    login.login(credentials["username"], credentials["password"])
    page.wait_for_url("**/dashboard/**", timeout=10000)
    assert page.url.startswith(DASHBOARD_URL.rsplit("/", 1)[0])
    api = EmployeeApi(page.context.request)
    employee = employee_persistence_data

    test_exception = None
    try:
        yield api, employee
    except BaseException as exc:
        test_exception = exc
        raise
    finally:
        if employee["create_attempted"]:
            def cleanup():
                row = _database_employee(
                    employee_repository, employee["employee_id"]
                )
                if row is None:
                    return
                emp_number, employee_id, first_name, middle_name, last_name = row
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

                response = api.get_employee_by_id(employee_id)
                assert response.status == 200
                matches = api.matching_employee_id(response, employee_id)
                assert isinstance(matches, list)
                assert len(matches) == 1
                assert matches[0]["empNumber"] == emp_number
                delete_response = api.delete_employees([emp_number])
                assert delete_response.status == 200
                assert delete_response.json().get("data") == [emp_number]
                _assert_absent_from_database(
                    employee_repository, employee_id
                )

            run_cleanup_preserving_test_failure(test_exception, cleanup)


def _assert_absent_from_database(repository, employee_id):
    assert _database_employee(repository, employee_id) is None


def _create_employee(api, employee):
    employee["create_attempted"] = True
    response = api.create_employee(
        {
            "firstName": employee["first_name"],
            "middleName": "",
            "lastName": employee["last_name"],
            "employeeId": employee["employee_id"],
        }
    )
    assert response.status == 200
    body = response.json()
    assert {"data", "meta", "rels"} <= set(body)
    data = body["data"]
    assert data["employeeId"] == employee["employee_id"]
    assert isinstance(data["empNumber"], int)
    assert data["empNumber"] > 0
    employee["employee_number"] = data["empNumber"]
    return data


def test_api_create_persists_employee_in_database(
    api_employee, employee_repository
):
    api, employee = api_employee
    created = _create_employee(api, employee)
    row = _assert_database_employee(
        employee_repository,
        employee,
        employee["first_name"],
        employee["last_name"],
    )
    assert row[0] == created["empNumber"]


def test_api_update_persists_employee_in_database(
    api_employee, employee_repository
):
    api, employee = api_employee
    created = _create_employee(api, employee)
    before_update = _assert_database_employee(
        employee_repository,
        employee,
        employee["first_name"],
        employee["last_name"],
    )

    response = api.update_personal_details(
        created["empNumber"],
        {
            "firstName": employee["updated_first_name"],
            "middleName": "",
            "lastName": employee["updated_last_name"],
            "employeeId": employee["employee_id"],
        },
    )
    assert response.status == 200
    updated = response.json()["data"]
    assert updated["empNumber"] == created["empNumber"]
    assert updated["employeeId"] == employee["employee_id"]
    assert updated["firstName"] == employee["updated_first_name"]
    assert updated["middleName"] == ""
    assert updated["lastName"] == employee["updated_last_name"]

    after_update = _assert_database_employee(
        employee_repository,
        employee,
        employee["updated_first_name"],
        employee["updated_last_name"],
    )
    assert after_update[0] == before_update[0] == created["empNumber"]
    assert after_update[1] == before_update[1] == employee["employee_id"]


def test_api_delete_removes_employee_from_database(
    api_employee, employee_repository
):
    api, employee = api_employee
    created = _create_employee(api, employee)
    row = _assert_database_employee(
        employee_repository,
        employee,
        employee["first_name"],
        employee["last_name"],
    )
    assert row[0] == created["empNumber"]

    response = api.delete_employees([created["empNumber"]])
    assert response.status == 200
    assert response.json().get("data") == [created["empNumber"]]
    _assert_absent_from_database(employee_repository, employee["employee_id"])
    employee["create_attempted"] = False
