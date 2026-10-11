# OrangeHRM AI SDET

Python UI/API/database tests for the local OrangeHRM application. The project uses Python, Playwright, pytest, and MariaDB.

## Prerequisites and local setup

- Windows and the project virtual environment at `.venv`.
- The current project environment was verified with Python 3.14.6, Playwright 1.63.0, pytest 9.1.1, and MariaDB Python driver 1.1.14. These are observed versions, not a declared support range.
- A local OrangeHRM application at `http://localhost:8080` and an accessible MariaDB database are required for the CRUD lifecycle test.
- The root `conftest.py` loads `.env` using `python-dotenv`. Set the required environment variable names below in the root `.env`; `.gitignore` excludes that file. Do not commit or share credentials.

Dependency installation instructions, a dependency lock/manifest, and commands to provision or start OrangeHRM and MariaDB are not present in the verified project configuration.

## Environment variables

Authentication:

- `ORANGEHRM_USERNAME`
- `ORANGEHRM_PASSWORD`

MariaDB:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

## Running tests

From the project root in PowerShell:

```powershell
& '.\.venv\Scripts\python.exe' -m pytest tests -q
```

Run only the employee CRUD lifecycle test:

```powershell
& '.\.venv\Scripts\python.exe' -m pytest '.\tests\test_employee_crud_lifecycle.py' -q
```

VS Code pytest discovery is configured for the `tests` directory in `.vscode/settings.json`.

## Employee CRUD lifecycle test

`tests/test_employee_crud_lifecycle.py` uses the existing credentials fixture and `LoginPage` flow. It creates a uniquely identified employee through the PIM UI, leaves the photo untouched, and keeps Create Login Details disabled. It verifies the Employee Id and names in MariaDB, updates the names with the employee personal-details API while preserving the Employee Id, then verifies the updated values in MariaDB and the Employee List row. It deletes the employee through the UI confirmation flow and verifies absence through the employee-list API and MariaDB. Failure-path cleanup targets only the generated Employee Id and checks uniqueness and the internal employee number when available; the database connection is closed in all cases.

## Unverified setup details and limitations

- The project does not declare a Python support range or pin dependencies in a requirements/lock file.
- The exact steps to install dependencies and provision/start the local OrangeHRM and MariaDB services are not documented in the verified configuration.
- CI configuration or CI availability has not been established.
