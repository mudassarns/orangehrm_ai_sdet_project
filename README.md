# OrangeHRM AI SDET

Python UI/API/database tests for the local OrangeHRM application. The project uses Python, Playwright, pytest, and MariaDB.

## Prerequisites and local setup

- Windows and the project virtual environment at `.venv`.
- The current project environment was verified with Python 3.14.6, Playwright 1.63.0, pytest 9.1.1, and MariaDB Python driver 1.1.14. These are observed versions, not a declared support range.
- A local OrangeHRM application at `http://localhost:8080` and an accessible MariaDB database are required for the CRUD lifecycle test.
- The root `conftest.py` loads `.env` using `python-dotenv`. Set the required environment variable names below in the root `.env`; `.gitignore` excludes that file. Do not commit or share credentials.

Install the pinned Python dependencies and the Playwright Chromium browser from the project root in PowerShell:

```powershell
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' -m playwright install chromium
```

## Docker commands

Run these commands from the project root:

`D:\Automation\orangehrm_ai_sdet_project`

The Docker Compose file is located at `docker-orangehrm/docker-compose.yml`.

### Start OrangeHRM and MariaDB

Use the established startup command:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml up -d
```

To wait for services to reach a running or healthy state before the command returns:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml up -d --wait
```

Open OrangeHRM in your browser:

http://localhost:8080

### Check container status

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml ps
```

Include stopped containers in the status output:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml ps -a
```

### View logs

View logs from both services:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs
```

View OrangeHRM logs:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs orangehrm
```

View MariaDB logs:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs mariadb
```

Follow logs continuously by adding `-f`, for example:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml logs -f orangehrm
```

Press `Ctrl+C` to stop following logs. This does not stop the containers.

### Stop and restart the services

Stop the running services without removing their containers:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml stop
```

Start the existing stopped containers:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml start
```

Restart OrangeHRM only:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml restart orangehrm
```

Restart MariaDB only:

```powershell
docker compose --env-file .env -f docker-orangehrm/docker-compose.yml restart mariadb
```

### Important data and configuration precautions

- Docker volumes preserve data independently of a normal laptop reboot or container stop.
- The MariaDB database uses the named volume `mariadb_data`.
- The OrangeHRM application currently has configuration stored in an anonymous volume. Its `Conf.php` configuration was restored into the existing application volume.
- The established `up -d` command works for starting the existing stack. If Compose proposes to recreate the OrangeHRM container, inspect the container and volume configuration first.
- Do **not** run `docker compose down -v`, manually delete volumes, or remove the existing OrangeHRM container without first securing the application configuration and database data.
- Keep `.env` private. Never commit or share its credentials.

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

GitHub Actions runs the suite on pushes to `dev` and pull requests targeting `dev`. The workflow starts a fresh Docker Compose stack, initializes OrangeHRM with its bundled CLI installer, and runs the tests. Configure these repository secrets:

- `DB_NAME`
- `DB_PASSWORD`
- `ORANGEHRM_USERNAME`
- `ORANGEHRM_PASSWORD`

The workflow maps the OrangeHRM credentials to `ORANGEHRM_USERNAME` and `ORANGEHRM_PASSWORD`, and maps MariaDB connection settings to the `DB_*` variables consumed by the tests.

## Employee CRUD lifecycle test

`tests/test_employee_crud_lifecycle.py` uses the existing credentials fixture and `LoginPage` flow. It creates a uniquely identified employee through the PIM UI, leaves the photo untouched, and keeps Create Login Details disabled. It verifies the Employee Id and names in MariaDB, updates the names with the employee personal-details API while preserving the Employee Id, then verifies the updated values in MariaDB and the Employee List row. It deletes the employee through the UI confirmation flow and verifies absence through the employee-list API and MariaDB. Failure-path cleanup targets only the generated Employee Id and checks uniqueness and the internal employee number when available; the database connection is closed in all cases.

## Project structure

- `conftest.py` loads `.env` and provides shared authentication and database settings fixtures.
- `orangehrm/config.py` contains application URLs and database environment-setting names.
- `orangehrm/pages/` contains the login and PIM employee page objects.
- `orangehrm/api/employees.py` contains employee API request and response helpers.
- `orangehrm/database.py` opens MariaDB connections and provides read-only employee lookups.
- `tests/` contains the login and CRUD lifecycle workflows and their assertions.

## Unverified setup details and limitations

- The project does not declare a Python support range; dependency versions are pinned in `requirements.txt`.
- A successful GitHub Actions run still needs to verify the workflow in the target repository with the required secrets configured.
