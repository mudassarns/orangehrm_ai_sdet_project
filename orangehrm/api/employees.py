from urllib.parse import parse_qs, urlsplit
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse, Response

from orangehrm.config import EMPLOYEES_API_URL


class EmployeeApi:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    @staticmethod
    def is_employee_search(response: Response, employee_id: str) -> bool:
        parsed_url = urlsplit(response.url)
        return (
            response.request.method == "GET"
            and parsed_url.path.endswith("/api/v2/pim/employees")
            and parse_qs(parsed_url.query).get("employeeId") == [employee_id]
        )

    @staticmethod
    def matching_employee_id(response: APIResponse, employee_id: str) -> Any:
        data = response.json().get("data")
        if not isinstance(data, list):
            return data
        return [
            employee
            for employee in data
            if employee.get("employeeId") == employee_id
        ]

    def create_employee(self, payload: dict) -> APIResponse:
        return self.request.post(EMPLOYEES_API_URL, data=payload)

    def get_employee_by_id(self, employee_id: str) -> APIResponse:
        return self.request.get(
            EMPLOYEES_API_URL,
            params={"employeeId": employee_id},
        )

    def get_personal_details(self, emp_number: int) -> APIResponse:
        return self.request.get(
            f"{EMPLOYEES_API_URL}/{emp_number}/personal-details"
        )

    def update_personal_details(
        self, emp_number: int, payload: dict
    ) -> APIResponse:
        return self.request.put(
            f"{EMPLOYEES_API_URL}/{emp_number}/personal-details",
            data=payload,
        )

    def delete_employees(self, emp_numbers: list[int]) -> APIResponse:
        return self.request.delete(
            EMPLOYEES_API_URL,
            data={"ids": emp_numbers},
        )
