from playwright.sync_api import Locator, Page, expect


class EmployeePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open_add_employee(self) -> None:
        self.page.get_by_role("link", name="PIM").click()
        self.page.get_by_role("link", name="Add Employee").click()

    def _fill_name_fields(
        self, first_name: str, middle_name: str, last_name: str
    ) -> None:
        for field_name, value in (
            ("First Name", first_name),
            ("Middle Name", middle_name),
            ("Last Name", last_name),
        ):
            field = self.page.get_by_placeholder(field_name)
            field.click()
            field.fill(value)

    def fill_new_employee(
        self, first_name: str, middle_name: str, last_name: str, employee_id: str
    ) -> None:
        self._fill_name_fields(first_name, middle_name, last_name)
        self.page.locator(".oxd-input-group").filter(
            has_text="Employee Id"
        ).locator("input").fill(employee_id)

    def create_login_details_checkbox(self) -> Locator:
        return (
            self.page.get_by_text("Create Login Details")
            .locator("..")
            .locator('input[type="checkbox"]')
        )

    def save_employee(self) -> None:
        self.page.get_by_role("button", name="Save").click()

    def search_by_employee_id(self, employee_id: str) -> None:
        self.page.get_by_role("link", name="PIM").click()
        self.page.get_by_role("link", name="Employee List").click()
        expect(
            self.page.get_by_role("heading", name="Employee Information")
        ).to_be_visible()
        self.page.locator(".oxd-input-group").filter(
            has_text="Employee Id"
        ).locator("input").fill(employee_id)
        self.page.get_by_role("button", name="Search").click()

    def row_by_employee_id(self, employee_id: str) -> Locator:
        return self.page.locator(
            ".oxd-table-body .oxd-table-row"
        ).filter(has_text=employee_id)

    def edit_employee(self, row: Locator) -> None:
        expect(row).to_have_count(1)
        edit_button = row.locator("button").filter(
            has=self.page.locator("i.bi-pencil-fill")
        )
        expect(edit_button).to_have_count(1)
        edit_button.click()

    def update_employee_name(
        self, first_name: str, middle_name: str, last_name: str
    ) -> None:
        self._fill_name_fields(first_name, middle_name, last_name)
        self.save_employee()

    def delete_employee(self, row: Locator) -> None:
        expect(row).to_have_count(1)
        row.locator("span.oxd-checkbox-input").click()
        delete_button = self.page.locator("button.oxd-button--label-danger")
        expect(delete_button).to_be_visible()
        delete_button.click()
        confirmation = self.page.get_by_role("dialog")
        expect(confirmation).to_be_visible()
        confirmation.get_by_role("button", name="Yes, Delete").click()
        expect(self.page.get_by_text("Successfully Deleted")).to_be_visible()
