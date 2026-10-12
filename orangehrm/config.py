import os


BASE_URL = "http://localhost:8080/web/index.php"
LOGIN_URL = f"{BASE_URL}/auth/login"
DASHBOARD_URL = f"{BASE_URL}/dashboard/index"
EMPLOYEES_API_URL = f"{BASE_URL}/api/v2/pim/employees"

DATABASE_ENVIRONMENT_VARIABLES = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
)


def database_settings_from_environment():
    return {
        name: os.getenv(name)
        for name in DATABASE_ENVIRONMENT_VARIABLES
    }
