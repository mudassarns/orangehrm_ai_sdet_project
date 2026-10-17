# OrangeHRM AI SDET Project

[![GitHub Actions](https://github.com/mudassarns/orangehrm_ai_sdet_project/actions/workflows/pytest.yml/badge.svg?branch=dev)](https://github.com/mudassarns/orangehrm_ai_sdet_project/actions/workflows/pytest.yml)

An employee-focused automation project using **Python, pytest, Playwright, and MariaDB**. It combines UI testing, API testing, database persistence verification, and cross-layer CRUD validation, with automated CI reporting and failure diagnostics.

## What this project demonstrates

- UI automation with Playwright page objects.
- Employee API CRUD tests, including selected negative scenarios.
- Read-only MariaDB checks to verify persistence after UI/API operations.
- A combined CRUD lifecycle workflow across UI, API, and database layers.
- Reusable pytest fixtures, unique Employee IDs, and safe test-owned-record cleanup.
- Automatic HTML and JUnit reporting, failure screenshots, and retained Playwright traces.
- Docker Compose setup and GitHub Actions execution.

## Technology stack

| Component | Purpose |
|---|---|
| Python | Test implementation |
| pytest | Test execution, fixtures, assertions, and organization |
| Playwright | Browser automation and API requests |
| Page objects and API helper | Reusable UI and API operations |
| MariaDB | Read-only verification of employee persistence |
| Docker Compose | Local OrangeHRM and MariaDB services |
| GitHub Actions | CI regression execution and artifact upload |
| pytest-html and JUnit XML | Human-readable and machine-readable reports |
| Playwright screenshots and traces | Failure investigation |

## Architecture

- `orangehrm/pages/` contains the login and employee page objects.
- `orangehrm/api/employees.py` contains the employee API helper.
- `orangehrm/database.py` provides the MariaDB connection and read-only employee repository.
- Root `conftest.py` loads `.env` and provides shared authentication and unique Employee ID fixtures.
- `tests/conftest.py` provides database and employee-persistence fixtures.
- `pytest.ini` configures reports and failure diagnostics for ordinary pytest runs.
- `.github/workflows/pytest.yml` defines the CI environment, Docker setup, test run, and artifact upload.

The API tests use the authenticated Playwright request context. Database assertions use read-only queries; test operations that create or modify employees are performed through the application UI or API.

## Test coverage

| Test module | Coverage |
|---|---|
| `tests/test_login.py` | Required fields, successful authentication, invalid credentials, password masking, and unauthenticated dashboard redirection |
| `tests/test_employee_ui.py` | Employee creation, search, update, and deletion through the UI |
| `tests/test_employee_api.py` | API create/read, update, CRUD lifecycle, unknown Employee ID search, and update for a nonexistent employee number |
| `tests/test_employee_database_ui.py` | Verify UI-created, updated, and deleted employees in MariaDB |
| `tests/test_employee_database_api.py` | Verify API-created, updated, and deleted employees in MariaDB |
| `tests/test_employee_crud_lifecycle.py` | Combined UI, API, and MariaDB employee CRUD workflow |

### Verification matrix

| Operation | Performed through | Verification |
|---|---|---|
| Employee create/update/delete | UI | UI assertions and MariaDB |
| Employee create/update/delete | API | HTTP response, subsequent API read where applicable, and MariaDB |
| Combined CRUD lifecycle | UI and API | UI, API, and MariaDB |

The negative API tests cover an unknown Employee ID and an update request for a nonexistent employee number. Expected responses are based on the observed OrangeHRM API contract.

## Project structure

```text
orangehrm_ai_sdet_project/
├── .github/workflows/pytest.yml
├── docker-orangehrm/docker-compose.yml
├── orangehrm/
│   ├── api/employees.py
│   ├── pages/employee_page.py
│   ├── pages/login_page.py
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
├── .env.example
├── .gitignore
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Prerequisites

- Windows with PowerShell for the commands below (Docker and Python are also available on other platforms).
- Python 3.14 and project dependencies.
- Docker Desktop with Docker Compose.
- A local OrangeHRM application at `http://localhost:8080`.
- Database connection settings for MariaDB.
- OrangeHRM administrator credentials for login and authenticated API tests.

## Local setup

Run commands from the repository root.

1. Create and activate a virtual environment:

   ```powershell
   py -3.14 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies and the Playwright Chromium browser:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

3. Create your private environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

   Edit `.env` and replace the placeholder passwords. Keep `MARIADB_ROOT_PASSWORD`, `MARIADB_PASSWORD`, and `DB_PASSWORD` consistent with the local database setup. The template leaves `MARIADB_DATABASE` empty to match the existing CI/installer flow; `DB_NAME` should contain the actual database name after installation.

4. Start the local containers:

   ```powershell
   docker compose --env-file .env -f docker-orangehrm/docker-compose.yml up -d --wait
   docker compose --env-file .env -f docker-orangehrm/docker-compose.yml ps
   ```

5. On a fresh database, complete the OrangeHRM installation before running tests. The GitHub Actions workflow's **Start and initialize Docker stack** step documents the automated installer sequence. It is designed for CI and should not be copied blindly into a local environment. Use the local values in `.env` and verify the installer targets only the disposable local database.

6. Confirm OrangeHRM is accessible at `http://localhost:8080` and that the database connection values in `.env` match the installed instance.

## Docker operations

Run from the project root:

```powershell
# Check status
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml ps

# View logs
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs

# Follow OrangeHRM logs
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs -f orangehrm

# Stop containers without deleting database data
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml stop

# Start stopped containers
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml start
```

MariaDB data is stored in the named `mariadb_data` volume. Before recreating containers or removing volumes, back up any data or configuration you need. Avoid `docker compose down -v` on an environment whose data you want to preserve.

## Environment variables

The root `conftest.py` loads the root `.env` file using `python-dotenv`.

- `ORANGEHRM_USERNAME` and `ORANGEHRM_PASSWORD`: test administrator credentials.
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`: database connection used by persistence tests.
- `MARIADB_ROOT_PASSWORD`, `MARIADB_DATABASE`, `MARIADB_USER`, and `MARIADB_PASSWORD`: Docker Compose database initialization values.

Keep `.env` private. The `.gitignore` excludes local environment files and generated test artifacts. Never commit real credentials, tokens, OAuth files, or database dumps.

## Running tests

Reports are configured in `pytest.ini`; do not add reporting flags to normal commands.

Run the full suite:

```powershell
python -m pytest tests -q
```

Run focused modules:

```powershell
python -m pytest tests/test_login.py -q
python -m pytest tests/test_employee_ui.py -q
python -m pytest tests/test_employee_api.py -q
python -m pytest tests/test_employee_database_ui.py -q
python -m pytest tests/test_employee_database_api.py -q
python -m pytest tests/test_employee_crud_lifecycle.py -q
```

A failed test causes pytest to return a non-zero exit code and is recorded in the reports.

## Reporting and failure diagnostics

| Output | Location | Purpose |
|---|---|---|
| HTML report | `reports/report.html` | Human-readable test results |
| JUnit XML | `reports/junit.xml` | Machine-readable test outcomes |
| Screenshots | `test-results/` | Evidence captured on test failure |
| Playwright traces | `test-results/` | Browser action and page-state diagnostics retained on failure |

The `reports/` and `test-results/` directories are created automatically. The HTML report is self-contained; screenshots and traces remain separate diagnostic files.

### GitHub Actions artifacts

The workflow runs on pushes to `dev` and pull requests targeting `dev`. It prepares a fresh Docker environment, installs OrangeHRM, installs dependencies and Chromium, and runs the pytest suite.

The workflow uploads `reports/` and `test-results/` as the `pytest-reports-and-failure-diagnostics` artifact using `if: always()`, with seven-day retention. Artifact upload runs before Docker cleanup.

To inspect results, open the repository's **Actions** tab, select a workflow run, and download the artifact. Open `reports/report.html` for the summary or inspect screenshots and traces for failures. A successful run may have no screenshot or trace files.

## CI secrets

Configure the following GitHub repository secrets for the existing workflow:

- `DB_NAME`
- `DB_PASSWORD`
- `ORANGEHRM_USERNAME`
- `ORANGEHRM_PASSWORD`

The workflow maps secrets to the environment variables needed by the application, database, and tests. Secret values are not stored in this repository.

## Limitations

- The project focuses on login and employee CRUD, with selected API negative tests and UI/API database-persistence checks.
- The repository does not declare a formal Python support range.
- Screenshots and traces are separate artifacts rather than embedded in the HTML report.
- The local installation steps assume a disposable OrangeHRM/MariaDB environment; do not run destructive cleanup against shared or production data.
