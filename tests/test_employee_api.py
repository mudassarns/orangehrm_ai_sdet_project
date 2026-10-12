import warnings

import pytest
from playwright.sync_api import Page

from orangehrm.api.employees import EmployeeApi
from orangehrm.config import DASHBOARD_URL
from orangehrm.pages.login_page import LoginPage


@pytest.fixture
def employee_api(page: Page, credentials: dict) -> EmployeeApi:
    login = LoginPage(page)
    login.open()
    login.login(credentials["username"], credentials["password"])
    page.wait_for_url("**/dashboard/**", timeout=10000)
    assert page.url.startswith(DASHBOARD_URL.rsplit("/", 1)[0])
    return EmployeeApi(page.context.request)


@pytest.fixture
def employee_data(unique_employee_id: str) -> dict:
    suffix = unique_employee_id[2:]
    return {
        "employee_id": unique_employee_id,
        "first_name": f"ApiFirst{suffix}",
        "middle_name": "",
        "last_name": f"ApiLast{suffix}",
        "updated_first_name": f"ApiUpdate{suffix}",
        "updated_last_name": f"ApiLastUp{suffix}",
    }


def _matching_employees(api: EmployeeApi, employee_id: str) -> list[dict]:
    response = api.get_employee_by_id(employee_id)
    assert response.status == 200
    body = response.json()
    assert isinstance(body.get("data"), list)
    return [
        employee
        for employee in body["data"]
        if employee.get("employeeId") == employee_id
    ]


def _cleanup_employee(
    api: EmployeeApi,
    employee: dict,
    known_emp_number: int | None = None,
) -> None:
    matches = _matching_employees(api, employee["employee_id"])
    if not matches:
        return
    if len(matches) != 1:
        raise AssertionError(
            "Cleanup found multiple employees for the generated Employee Id."
        )

    match = matches[0]
    emp_number = match.get("empNumber")
    if (
        not isinstance(emp_number, int)
        or isinstance(emp_number, bool)
        or (known_emp_number is not None and emp_number != known_emp_number)
    ):
        raise AssertionError(
            "Cleanup could not verify the generated employee number."
        )
    expected_name_pairs = {
        (employee["first_name"], employee["last_name"]),
        (employee["updated_first_name"], employee["updated_last_name"]),
    }
    if (
        match.get("employeeId") != employee["employee_id"]
        or (match.get("firstName"), match.get("lastName"))
        not in expected_name_pairs
    ):
        raise AssertionError(
            "Cleanup refused to delete an employee with unexpected identity data."
        )

    delete_response = api.delete_employees([emp_number])
    assert delete_response.status == 200
    assert delete_response.json().get("data") == [emp_number]
    assert _matching_employees(api, employee["employee_id"]) == []


@pytest.fixture
def employee_cleanup(employee_api: EmployeeApi, employee_data: dict):
    test_exception = None
    try:
        yield employee_data
    except BaseException as exc:
        test_exception = exc
        raise
    finally:
        try:
            _cleanup_employee(
                employee_api,
                employee_data,
                known_emp_number=employee_data.get("emp_number"),
            )
        except BaseException as cleanup_exception:
            if test_exception is None:
                raise
            warnings.warn(
                "Employee API cleanup also failed: "
                f"{type(cleanup_exception).__name__}",
                RuntimeWarning,
            )


@pytest.fixture
def created_employee(
    employee_api: EmployeeApi, employee_cleanup: dict
) -> dict:
    response = employee_api.create_employee(
        {
            "firstName": employee_cleanup["first_name"],
            "middleName": employee_cleanup["middle_name"],
            "lastName": employee_cleanup["last_name"],
            "employeeId": employee_cleanup["employee_id"],
        }
    )
    body = response.json()
    data = body.get("data")
    employee_cleanup.update(
        {
            "create_response": response,
            "create_body": body,
            "create_data": data,
            "emp_number": (
                data.get("empNumber") if isinstance(data, dict) else None
            ),
        }
    )
    return employee_cleanup


def _assert_employee_fields(employee: dict, expected: dict) -> None:
    assert employee["empNumber"] == expected["emp_number"]
    assert employee["employeeId"] == expected["employee_id"]
    assert employee["firstName"] == expected["first_name"]
    assert employee["middleName"] == expected["middle_name"]
    assert employee["lastName"] == expected["last_name"]


def _update_payload(employee: dict) -> dict:
    return {
        "firstName": employee["updated_first_name"],
        "middleName": "",
        "lastName": employee["updated_last_name"],
        "employeeId": employee["employee_id"],
    }


def test_create_and_get_employee(employee_api, created_employee):
    assert created_employee["create_response"].status == 200
    assert {"data", "meta", "rels"} <= set(created_employee["create_body"])
    assert isinstance(created_employee["create_data"], dict)
    assert isinstance(created_employee["emp_number"], int)
    assert created_employee["emp_number"] > 0
    _assert_employee_fields(created_employee["create_data"], created_employee)

    matches = _matching_employees(
        employee_api, created_employee["employee_id"]
    )
    assert len(matches) == 1
    _assert_employee_fields(matches[0], created_employee)


def test_update_employee(employee_api, created_employee):
    response = employee_api.update_personal_details(
        created_employee["emp_number"], _update_payload(created_employee)
    )
    assert response.status == 200
    body = response.json()
    assert {"data", "meta", "rels"} <= set(body)
    updated_employee = body["data"]
    _assert_employee_fields(
        updated_employee,
        {
            "emp_number": created_employee["emp_number"],
            "employee_id": created_employee["employee_id"],
            "first_name": created_employee["updated_first_name"],
            "middle_name": "",
            "last_name": created_employee["updated_last_name"],
        },
    )

    matches = _matching_employees(
        employee_api, created_employee["employee_id"]
    )
    assert len(matches) == 1
    _assert_employee_fields(
        matches[0],
        {
            "emp_number": created_employee["emp_number"],
            "employee_id": created_employee["employee_id"],
            "first_name": created_employee["updated_first_name"],
            "middle_name": "",
            "last_name": created_employee["updated_last_name"],
        },
    )


def test_employee_crud_lifecycle_api(employee_api, created_employee):
    matches = _matching_employees(
        employee_api, created_employee["employee_id"]
    )
    assert len(matches) == 1
    _assert_employee_fields(matches[0], created_employee)

    update_response = employee_api.update_personal_details(
        created_employee["emp_number"], _update_payload(created_employee)
    )
    assert update_response.status == 200
    _assert_employee_fields(
        update_response.json()["data"],
        {
            "emp_number": created_employee["emp_number"],
            "employee_id": created_employee["employee_id"],
            "first_name": created_employee["updated_first_name"],
            "middle_name": "",
            "last_name": created_employee["updated_last_name"],
        },
    )
    updated_matches = _matching_employees(
        employee_api, created_employee["employee_id"]
    )
    assert len(updated_matches) == 1
    _assert_employee_fields(
        updated_matches[0],
        {
            "emp_number": created_employee["emp_number"],
            "employee_id": created_employee["employee_id"],
            "first_name": created_employee["updated_first_name"],
            "middle_name": "",
            "last_name": created_employee["updated_last_name"],
        },
    )

    delete_response = employee_api.delete_employees(
        [created_employee["emp_number"]]
    )
    assert delete_response.status == 200
    assert delete_response.json().get("data") == [created_employee["emp_number"]]
    assert _matching_employees(
        employee_api, created_employee["employee_id"]
    ) == []


def test_get_employee_with_unknown_employee_id(employee_api, employee_data):
    response = employee_api.get_employee_by_id(employee_data["employee_id"])
    assert response.status == 200
    body = response.json()
    assert {"data", "meta", "rels"} <= set(body)
    assert body["data"] == []


def test_update_nonexistent_employee(
    employee_api: EmployeeApi,
    employee_cleanup: dict,
):
    employee_data = employee_cleanup
    employee_number = 1_500_000_000 + (
        int(employee_data["employee_id"][2:], 16) % 500_000_000
    )
    precheck = employee_api.get_personal_details(employee_number)
    assert precheck.status == 422
    precheck_error = precheck.json()["error"]
    assert precheck_error["status"] == "422"
    assert precheck_error["message"] == "Invalid Parameter"
    assert precheck_error["data"]["invalidParamKeys"] == ["empNumber"]

    update_response = employee_api.update_personal_details(
        employee_number, _update_payload(employee_data)
    )
    assert update_response.status == 422
    update_error = update_response.json()["error"]
    assert update_error["status"] == "422"
    assert update_error["message"] == "Invalid Parameter"
    assert update_error["data"]["invalidParamKeys"] == ["empNumber"]

    assert _matching_employees(employee_api, employee_data["employee_id"]) == []
