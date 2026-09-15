import allure

from pages.base_page import BasePage
from view_components.element_locator import id_locator


class LoginPage(BasePage):
    _username_field = id_locator("nameET")
    _password_field = id_locator("passwordET")
    _login_button = id_locator("loginBtn")

    @allure.step("Log in as {username}")
    def login(self, username: str, password: str):
        self.send_keys(self._username_field, username)
        self.send_keys(self._password_field, password)
        self.tap(self._login_button)
    
    