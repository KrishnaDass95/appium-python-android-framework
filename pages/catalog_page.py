from enum import Enum

import allure

from pages.base_page import BasePage
from pages.login_page import LoginPage
from view_components.element_locator import accessibility_locator, id_locator


class SortOption(Enum):
    NAME_ASC = "Ascending order by name"
    NAME_DESC = "Descending order by name"
    PRICE_ASC = "Ascending order by price"
    PRICE_DESC = "Descending order by price"


class CatalogPage(BasePage):
    _sort_button = id_locator("sortIV")
    _menu_button = id_locator("menuIV")
    _cart_button = id_locator("cartRL")
    _product_titles = id_locator("titleTV")
    _product_images = id_locator("productIV")
    _login_menu_button = accessibility_locator("Login Menu Item")
    _logout_menu_button = accessibility_locator("Logout Menu Item")
    _logout_confirm_button = id_locator("android:id/button1")

    @allure.step("Tap product by name {name}")
    def tap_product_by_name(self, name: str) -> None:
        self.find_by_uiautomator(
            f"new UiScrollable(new UiSelector().scrollable(true))"
            f'.scrollIntoView(new UiSelector().text("{name}"))'
        ).click()

    @allure.step("Tap product at index {index}")
    def tap_product_by_index(self, index: int) -> None:
        self.get_elements(self._product_images)[index].click()

    @allure.step("Get all product titles")
    def get_product_titles(self) -> list[str]:
        return [t.text for t in self.get_elements(self._product_titles)]

    @allure.step("Sort products by {option}")
    def tap_sort_by(self, option: SortOption) -> None:
        self.tap(self._sort_button)
        self.tap(accessibility_locator(option.value))

    @allure.step("Tap cart icon")
    def tap_cart(self) -> None:
        self.tap(self._cart_button)

    @allure.step("Tap menu")
    def tap_menu(self) -> None:
        self.tap(self._menu_button)

    @allure.step("Tap login from hamburger menu")
    def tap_login_from_menu(self):
        self.tap(self._login_menu_button)
        return LoginPage(driver=self.driver)

    def get_logout_state_text(self) -> str:
        return self.get_text(self._logout_menu_button)

    @allure.step("Logout")
    def logout_if_logged_in(self):
        if not self.is_element_present(self._logout_menu_button, timeout=2):
            self.tap(self._menu_button)
        if self.get_text(self._logout_menu_button) == "Log Out":
            self.tap(self._logout_menu_button)
            self.tap(self._logout_confirm_button)
        else:
            self.driver.back()

