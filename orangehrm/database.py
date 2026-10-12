import mariadb


def connect_database(settings):
    missing_settings = [
        name for name, value in settings.items() if not value
    ]
    if missing_settings:
        raise ValueError(
            "Database settings are missing: " + ", ".join(missing_settings)
        )
    return mariadb.connect(
        host=settings["DB_HOST"],
        port=int(settings["DB_PORT"]),
        database=settings["DB_NAME"],
        user=settings["DB_USER"],
        password=settings["DB_PASSWORD"],
    )


class EmployeeRepository:
    def __init__(self, connection):
        self.connection = connection

    def find_by_employee_id(self, employee_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("START TRANSACTION READ ONLY")
            cursor.execute(
                """
                SELECT emp_number, employee_id, emp_firstname,
                       emp_middle_name, emp_lastname
                FROM hs_hr_employee
                WHERE employee_id = ?
                """,
                (employee_id,),
            )
            return cursor.fetchall()
        finally:
            try:
                cursor.close()
            finally:
                self.connection.rollback()
