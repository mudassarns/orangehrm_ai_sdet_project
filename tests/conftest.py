import warnings

import pytest

from orangehrm.config import database_settings_from_environment
from orangehrm.database import EmployeeRepository, connect_database


@pytest.fixture
def db_settings():
    return database_settings_from_environment()


@pytest.fixture
def employee_repository(db_settings):
    connection = connect_database(db_settings)
    try:
        yield EmployeeRepository(connection)
    finally:
        connection.close()


@pytest.fixture
def employee_persistence_data(unique_employee_id, employee_repository):
    existing = employee_repository.find_by_employee_id(unique_employee_id)
    assert not existing, (
        "Generated Employee ID already exists in the database; "
        "refusing to use an existing employee."
    )

    suffix = unique_employee_id[2:]
    return {
        "employee_id": unique_employee_id,
        "first_name": f"Persist{suffix}",
        "last_name": f"Record{suffix}",
        "updated_first_name": f"Update{suffix}",
        "updated_last_name": f"Saved{suffix}",
        "create_attempted": False,
        "employee_number": None,
    }


@pytest.fixture
def run_cleanup_preserving_test_failure():
    def run(test_exception, cleanup):
        try:
            cleanup()
        except BaseException as cleanup_exception:
            if test_exception is None:
                raise
            warnings.warn(
                "Employee persistence cleanup also failed: "
                f"{type(cleanup_exception).__name__}",
                RuntimeWarning,
            )

    return run
