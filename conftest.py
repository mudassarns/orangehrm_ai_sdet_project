import os
from uuid import uuid4

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def credentials():
    username = os.getenv("ORANGEHRM_USERNAME")
    password = os.getenv("ORANGEHRM_PASSWORD")
    if not username or not password:
        pytest.skip(
            "ORANGEHRM_USERNAME and ORANGEHRM_PASSWORD must be set "
            "for valid login tests."
        )
    return {"username": username, "password": password}


@pytest.fixture
def unique_employee_id():
    employee_id = f"UI{uuid4().hex[:8].upper()}"
    assert len(employee_id) <= 10
    return employee_id
