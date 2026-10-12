# OrangeHRM AI SDET Project

An employee-focused test automation project using **Python, pytest, Playwright, and MariaDB**. It combines UI testing, API testing, database persistence verification, and cross-layer CRUD validation, with automated CI reporting and failure diagnostics.

## Project Overview

The project tests the OrangeHRM application through three verification layers:

- **UI:** Validate employee operations through the application interface.
- **API:** Validate employee CRUD operations, response contracts, and negative scenarios through HTTP requests.
- **Database:** Verify that employee operations performed through the UI or API are persisted correctly in MariaDB.

The existing end-to-end CRUD lifecycle test combines these layers in a single workflow. The independent tests provide more focused coverage and make failures easier to isolate.

## Technology Stack

| Component | Purpose |
|---|---|
| Python | Test implementation |
| pytest | Test execution, fixtures, assertions, and test organization |
| Playwright | Browser automation and API requests |
| Page objects | Encapsulate login and employee UI interactions |
| Employee API helper | Encapsulate employee API operations |
| MariaDB | Read-only verification of employee persistence |
| Docker Compose | Local OrangeHRM and MariaDB environment |
| GitHub Actions | CI regression execution |
| pytest-html | Self-contained HTML test reporting |
| JUnit XML | Machine-readable test results for CI |
| Playwright screenshots and traces | Failure investigation |

## Architecture

The project separates UI interactions, API operations, and database verification.

- `orangehrm/pages/` contains the login and employee page objects.
- `orangehrm/api/employees.py` contains the employee API helper.
- `orangehrm/database.py` contains the MariaDB connection and read-only employee repository.
- Root `conftest.py` loads environment settings and provides shared authentication and Employee ID fixtures.
- `tests/conftest.py` provides database and employee-persistence fixtures for the database verification tests.
- `pytest.ini` configures reporting and failure diagnostics for normal pytest runs.
- `.github/workflows/pytest.yml` configures the CI test environment and artifact upload.

The project uses the authenticated Playwright browser context for API operations where appropriate. Database assertions use read-only queries against the employee table.

## Test Coverage

The current suite covers login, employee CRUD through the UI and API, database persistence, and a combined CRUD lifecycle workflow.

| Test module | Coverage |
|---|---|
| `tests/test_login.py` | Required login fields, successful authentication, invalid credentials, password masking, and unauthenticated dashboard redirection |
| `tests/test_employee_ui.py` | Employee creation, search, editing, and deletion through the UI |
| `tests/test_employee_api.py` | API create-and-get, update, complete CRUD lifecycle, unknown Employee ID search, and update against a nonexistent employee number |
| `tests/test_employee_database_ui.py` | Verify UI-created employees in MariaDB, verify UI updates persist, and verify UI deletion removes the database record |
| `tests/test_employee_database_api.py` | Verify API-created employees in MariaDB, verify API updates persist, and verify API deletion removes the database record |
| `tests/test_employee_crud_lifecycle.py` | Combined UI, API, and MariaDB employee CRUD workflow |

### Verification Matrix

| Operation | Action performed through | Verification |
|---|---|---|
| Employee create | UI | UI assertions and MariaDB |
| Employee update | UI | UI assertions and MariaDB |
| Employee delete | UI | UI state and MariaDB |
| Employee create | API | HTTP response and MariaDB |
| Employee update | API | HTTP response, subsequent API read, and MariaDB |
| Employee delete | API | HTTP response and MariaDB |
| Combined lifecycle | UI and API | UI, API, and MariaDB |

The API negative tests verify the application's observed behavior for an unknown Employee ID and an update request against a nonexistent employee number. Expected status codes and response fields follow the verified OrangeHRM API contract.

The local full suite has passed with **25 tests**. The test count may change as coverage evolves.

## Project Structure

```text
orangehrm_ai_sdet_project/
├── .github/
│   └── workflows/
│       └── pytest.yml
├── docker-orangehrm/
│   └── docker-compose.yml
├── orangehrm/
│   ├── api/
│   │   └── employees.py
│   ├── pages/
│   │   ├── employee_page.py
│   │   └── login_page.py
│   ├── config.py
│   └── database.py
├── tests/
│   ├── conftest.py
│   ├── test_login.py
│   ├── test_employee_ui.py
│   ├── test_employee_api.py
│   ├── test_employee_database_ui.py
│   ├── test_employee_database_api.py
│   └── test_employee_crud_lifecycle.py
├── .gitignore
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

Generated reports and failure diagnostics are stored under `reports/` and `test-results/`; these output directories are ignored by Git.

## Prerequisites

- Windows with PowerShell for the documented local commands.
- Python and the project virtual environment at `.venv`.
- Docker Desktop and Docker Compose.
- A local OrangeHRM application at `http://localhost:8080`.
- Accessible MariaDB database settings for database verification.

The current environment has been verified with Python 3.14.6, pytest 9.1.1, Playwright 1.63.0, and MariaDB Python driver 1.1.14. These observed versions are not a declared Python support range.

## Installation

From the project root:

```powershell
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m playwright install chromium
```

## Docker Environment

The Docker Compose configuration is located at:

`docker-orangehrm/docker-compose.yml`

### Start OrangeHRM and MariaDB

Run from the project root:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml up -d
```

To wait for services to reach a running or healthy state:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml up -d --wait
```

Open OrangeHRM at:

http://localhost:8080

### Check container status

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml ps
```

Include stopped containers:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml ps -a
```

### View logs

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs
```

OrangeHRM logs:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs orangehrm
```

MariaDB logs:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs mariadb
```

Follow logs continuously with `-f`. Press `Ctrl+C` to stop following them without stopping the containers.

### Stop and restart services

Stop without removing containers:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml stop
```

Start existing stopped containers:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml start
```

Restart OrangeHRM:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml restart orangehrm
```

Restart MariaDB:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml restart mariadb
```

### Docker data precautions

- MariaDB data is stored in the named volume `mariadb_data`.
- The OrangeHRM application currently has configuration stored in an anonymous volume. Its `Conf.php` configuration was restored into the existing application volume.
- If Compose proposes to recreate the OrangeHRM container, inspect the container and volume configuration before proceeding.
- Do not run `docker compose down -v`, manually delete volumes, or remove the existing local OrangeHRM container without first securing the application configuration and database data.
- The CI workflow uses its own fresh Docker environment and performs cleanup after the test run. Do not copy destructive CI cleanup commands into your local workflow without understanding their effects.

## Environment Variables

The root `conftest.py` loads the root `.env` file through `python-dotenv`.

### Authentication

- `ORANGEHRM_USERNAME`
- `ORANGEHRM_PASSWORD`

### MariaDB

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

Keep `.env` private. It is excluded by `.gitignore`. Never commit or share credentials.

## Running Tests

Reporting is configured in `pytest.ini`; reporting parameters are not required on the command line.

### Run the full suite

```powershell
python -m pytest tests -q
```

### Run login tests

```powershell
python -m pytest tests/test_login.py -q
```

### Run UI employee CRUD tests

```powershell
python -m pytest tests/test_employee_ui.py -q
```

### Run API employee CRUD tests

```powershell
python -m pytest tests/test_employee_api.py -q
```

### Run UI-to-database persistence tests

```powershell
python -m pytest tests/test_employee_database_ui.py -q
```

### Run API-to-database persistence tests

```powershell
python -m pytest tests/test_employee_database_api.py -q
```

### Run the combined CRUD lifecycle test

```powershell
python -m pytest tests/test_employee_crud_lifecycle.py -q
```

The reporting defaults also apply to focused test runs. A failing test causes pytest to return a non-zero exit code and is recorded in the reports.

## Test Data Isolation and Cleanup

Tests generate unique Employee IDs for records they create. They verify results through the relevant application layer and clean up test-owned records.

- UI tests perform employee creation, updates, and deletion through the UI.
- API tests perform employee creation, updates, and deletion through the API.
- Database persistence tests use MariaDB for read-only verification; they do not write directly to the database.
- Cleanup checks employee identity and, where available, the internal employee number before deletion.
- Cleanup targets only records created by the current test and verifies record absence when applicable.
- Ambiguous or mismatched records must not be deleted.

The existing lifecycle test remains a broader workflow that combines UI operations, API requests, and MariaDB checks.

## Reporting and Failure Diagnostics

Normal pytest runs automatically generate reports and configure failure diagnostics through `pytest.ini`.

| Output | Location | Purpose |
|---|---|---|
| HTML report | `reports/report.html` | Human-readable test results |
| JUnit XML | `reports/junit.xml` | Machine-readable test outcomes |
| Failure screenshots | `test-results/` | Visual evidence captured on test failure |
| Playwright traces | `test-results/` | Browser action and page-state diagnostics retained on failure |

The `reports/` and `test-results/` directories are created automatically. The HTML report is self-contained. Screenshots and traces are stored as separate files; they are not automatically embedded in the HTML report.

### GitHub Actions artifacts

The CI workflow runs the suite on pushes to `dev` and pull requests targeting `dev`. It starts a fresh Docker Compose environment, initializes OrangeHRM, installs dependencies and Chromium, and runs pytest.

The workflow uploads the `reports/` and `test-results/` directories as an artifact named `pytest-reports-and-failure-diagnostics`. Upload runs with `if: always()`, retains artifacts for seven days, and occurs before Docker cleanup.

To inspect a run:

1. Open the repository's **Actions** tab.
2. Select the relevant workflow run.
3. Open the artifacts section and download `pytest-reports-and-failure-diagnostics`.
4. Open `reports/report.html` to review results, or inspect the PNG screenshots and Playwright traces for failures.

If no test fails, the `test-results/` directory may contain no screenshot or trace files.

## Continuous Integration Secrets

Configure these GitHub repository secrets for the workflow:

- `DB_NAME`
- `DB_PASSWORD`
- `ORANGEHRM_USERNAME`
- `ORANGEHRM_PASSWORD`

The workflow maps these secrets to the environment variables required by the application, database, and tests. It validates the required secrets before starting the stack and avoids printing credential values.

## Current Status

The reporting configuration is committed on `dev` as `cdd1f42` (`Configure automatic pytest reporting`). The latest observed GitHub Actions run for that commit succeeded, and the local full suite passed with 25 tests.

## Limitations

- The project does not declare a formal Python support range.
- Coverage is currently focused on login and employee CRUD, with API negative tests and database persistence checks.
- Failure screenshots and traces support diagnosis, but the HTML report does not embed them.
