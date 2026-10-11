import warnings
from urllib.parse import urlsplit
from uuid import uuid4

from playwright.sync_api import expect

from orangehrm.api.employees import EmployeeApi
from orangehrm.config import DASHBOARD_URL
from orangehrm.database import EmployeeRepository, connect_database
from orangehrm.pages.employee_page import EmployeePage
from orangehrm.pages.login_page import LoginPage


def test_employee_crud_lifecycle(page, credentials, db_settings):
    missing_settings = [name for name, value in db_settings.items() if not value]
    assert not missing_settings, (
        "Database settings missing from the project environment: "
        + ", ".join(missing_settings)
    )
    db_port = db_settings["DB_PORT"]
    assert db_port is not None

    connection = connect_database(db_settings)
    employee_repository = EmployeeRepository(connection)
    employee_page = EmployeePage(page)
    employee_api = EmployeeApi(page.context.request)

    suffix = uuid4().hex[:7].upper()
    first_name = f"QA{suffix}"
    middle_name = f"Middle{suffix}"
    last_name = f"Last{suffix}"
    updated_first_name = f"API{suffix}"
    updated_middle_name = f"Update{suffix}"
    updated_last_name = f"UpdateLast{suffix}"
    employee_id = f"E{suffix}"
    emp_number = None
    create_submitted = False
    test_exception = None

    def read_employee():
        return employee_repository.find_by_employee_id(employee_id)

    def search_employee_in_ui_and_api():
        with page.expect_response(
            lambda response: employee_api.is_employee_search(
                response, employee_id
            )
        ) as response_info:
            employee_page.search_by_employee_id(employee_id)

        response = response_info.value
        assert response.status == 200
        matches = employee_api.matching_employee_id(response, employee_id)
        assert isinstance(matches, list)
        return matches, employee_page.row_by_employee_id(employee_id)

    def delete_employee_from_ui(row):
        employee_page.delete_employee(row)

    try:
        login = LoginPage(page)
        login.open()
        login.login(credentials["username"], credentials["password"])
        page.wait_for_url("**/dashboard/**", timeout=10000)
        assert page.url.startswith(DASHBOARD_URL.rsplit("/", 1)[0])
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        employee_page.open_add_employee()
        employee_page.fill_new_employee(
            first_name, middle_name, last_name, employee_id
        )
        create_login_checkbox = employee_page.create_login_details_checkbox()
        expect(create_login_checkbox).not_to_be_checked()

        create_submitted = True
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path.endswith("/api/v2/pim/employees")
        ) as create_response_info:
            employee_page.save_employee()

        create_response = create_response_info.value
        assert create_response.status == 200
        created_employee = create_response.json()["data"]
        emp_number = created_employee["empNumber"]
        assert created_employee["employeeId"] == employee_id
        expect(page.get_by_text("Successfully Saved")).to_be_visible()

        created_rows = read_employee()
        assert len(created_rows) == 1
        assert created_rows[0] == (
            emp_number,
            employee_id,
            first_name,
            middle_name,
            last_name,
        )

        update_payload = {
            "firstName": updated_first_name,
            "middleName": updated_middle_name,
            "lastName": updated_last_name,
            "employeeId": employee_id,
        }
        update_response = employee_api.update_personal_details(
            emp_number,
            update_payload,
        )
        assert update_response.status == 200
        updated_employee = update_response.json()["data"]
        assert updated_employee["empNumber"] == emp_number
        assert updated_employee["employeeId"] == employee_id
        assert updated_employee["firstName"] == updated_first_name
        assert updated_employee["middleName"] == updated_middle_name
        assert updated_employee["lastName"] == updated_last_name

        updated_rows = read_employee()
        assert len(updated_rows) == 1
        assert updated_rows[0] == (
            emp_number,
            employee_id,
            updated_first_name,
            updated_middle_name,
            updated_last_name,
        )

        matching_employees, employee_row = search_employee_in_ui_and_api()
        assert len(matching_employees) == 1
        employee_cells = employee_row.locator(".oxd-table-cell")
        expect(employee_cells.nth(1)).to_have_text(employee_id)
        expect(employee_cells.nth(2)).to_have_text(
            f"{updated_first_name} {updated_middle_name}"
        )
        expect(employee_cells.nth(3)).to_have_text(updated_last_name)
        delete_employee_from_ui(employee_row)

        absent_employees, absent_row = search_employee_in_ui_and_api()
        assert absent_employees == []
        expect(absent_row).to_have_count(0)
        assert read_employee() == []
    except BaseException as exc:
        test_exception = exc
        raise
    finally:
        cleanup_exception = None
        connection_exception = None
        try:
            if create_submitted:
                database_employees = read_employee()
                assert len(database_employees) <= 1

                if database_employees:
                    database_emp_number, database_employee_id, *database_names = (
                        database_employees[0]
                    )
                    assert database_employee_id == employee_id
                    assert tuple(database_names) in (
                        (first_name, middle_name, last_name),
                        (
                            updated_first_name,
                            updated_middle_name,
                            updated_last_name,
                        ),
                    )
                    if emp_number is not None:
                        assert database_emp_number == emp_number

                    matching_employees, employee_row = (
                        search_employee_in_ui_and_api()
                    )
                    assert len(matching_employees) == 1
                    assert matching_employees[0]["empNumber"] == database_emp_number
                    delete_employee_from_ui(employee_row)
                else:
                    matching_employees, employee_row = (
                        search_employee_in_ui_and_api()
                    )
                    assert matching_employees == []
                    expect(employee_row).to_have_count(0)

                absent_employees, absent_row = search_employee_in_ui_and_api()
                assert absent_employees == []
                expect(absent_row).to_have_count(0)
                assert read_employee() == []
        except BaseException as exc:
            cleanup_exception = exc
        finally:
            try:
                connection.close()
            except BaseException as exc:
                connection_exception = exc

        if test_exception is not None:
            if cleanup_exception is not None:
                warnings.warn(
                    "Employee cleanup also failed: "
                    f"{type(cleanup_exception).__name__}: {cleanup_exception}",
                    RuntimeWarning,
                )
            if connection_exception is not None:
                warnings.warn(
                    "Closing the MariaDB connection also failed: "
                    f"{type(connection_exception).__name__}: {connection_exception}",
                    RuntimeWarning,
                )
        elif cleanup_exception is not None:
            if connection_exception is not None:
                warnings.warn(
                    "Closing the MariaDB connection also failed: "
                    f"{type(connection_exception).__name__}: {connection_exception}",
                    RuntimeWarning,
                )
            raise cleanup_exception
        elif connection_exception is not None:
            raise connection_exception
