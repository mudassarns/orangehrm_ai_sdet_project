import os

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
