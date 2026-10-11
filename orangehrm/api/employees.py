from urllib.parse import parse_qs, urlsplit

from orangehrm.config import EMPLOYEES_API_URL


class EmployeeApi:
    def __init__(self, request):
        self.request = request

    @staticmethod
    def is_employee_search(response, employee_id):
        parsed_url = urlsplit(response.url)
        return (
            response.request.method == "GET"
            and parsed_url.path.endswith("/api/v2/pim/employees")
            and parse_qs(parsed_url.query).get("employeeId") == [employee_id]
        )

    @staticmethod
    def matching_employee_id(response, employee_id):
        data = response.json().get("data")
        if not isinstance(data, list):
            return data
        return [
            employee
            for employee in data
            if employee.get("employeeId") == employee_id
        ]

    def update_personal_details(self, emp_number, payload):
        return self.request.put(
            f"{EMPLOYEES_API_URL}/{emp_number}/personal-details",
            data=payload,
        )
