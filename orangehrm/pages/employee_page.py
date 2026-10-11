from playwright.sync_api import expect


class EmployeePage:
    def __init__(self, page):
        self.page = page

    def open_add_employee(self):
        self.page.get_by_role("link", name="PIM").click()
        self.page.get_by_role("link", name="Add Employee").click()

    def fill_new_employee(self, first_name, middle_name, last_name, employee_id):
        self.page.get_by_placeholder("First Name").fill(first_name)
        self.page.get_by_placeholder("Middle Name").fill(middle_name)
        self.page.get_by_placeholder("Last Name").fill(last_name)
        self.page.locator(".oxd-input-group").filter(
            has_text="Employee Id"
        ).locator("input").fill(employee_id)

    def create_login_details_checkbox(self):
        return (
            self.page.get_by_text("Create Login Details")
            .locator("..")
            .locator('input[type="checkbox"]')
        )

    def save_employee(self):
        self.page.get_by_role("button", name="Save").click()

    def search_by_employee_id(self, employee_id):
        self.page.get_by_role("link", name="PIM").click()
        self.page.get_by_role("link", name="Employee List").click()
        expect(
            self.page.get_by_role("heading", name="Employee Information")
        ).to_be_visible()
        self.page.locator(".oxd-input-group").filter(
            has_text="Employee Id"
        ).locator("input").fill(employee_id)
        self.page.get_by_role("button", name="Search").click()

    def row_by_employee_id(self, employee_id):
        return self.page.locator(
            ".oxd-table-body .oxd-table-row"
        ).filter(has_text=employee_id)

    def delete_employee(self, row):
        expect(row).to_have_count(1)
        row.locator("span.oxd-checkbox-input").click()
        delete_button = self.page.locator("button.oxd-button--label-danger")
        expect(delete_button).to_be_visible()
        delete_button.click()
        confirmation = self.page.get_by_role("dialog")
        expect(confirmation).to_be_visible()
        confirmation.get_by_role("button", name="Yes, Delete").click()
        expect(self.page.get_by_text("Successfully Deleted")).to_be_visible()
