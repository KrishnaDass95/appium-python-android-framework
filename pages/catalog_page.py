from enum import Enum

import allure

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductPage
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
    def tap_product_by_name(self, name: str) -> ProductPage:
        # scrollIntoView makes the item visible. The product image (productIV) is
        # the actual click target — clicking titleTV doesn't trigger navigation.
        # After scrolling, we match the title's visible index to the image at the
        # same position (RecyclerView renders them in the same order).
        self.find_by_uiautomator(
            f"new UiScrollable(new UiSelector().scrollable(true))"
            f'.scrollIntoView(new UiSelector().text("{name}"))'
        )
        visible_titles = self.get_elements(self._product_titles)
        index = next(i for i, t in enumerate(visible_titles) if t.text == name)
        self.get_elements(self._product_images)[index].click()
        product_detail = ProductPage(driver=self.driver)
        product_detail.wait_for_element(product_detail._product_price)
        return product_detail

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
        login = LoginPage(driver=self.driver)
        login.wait_for_element(login._login_button)
        return login

    @allure.step("Get logout menu item text")
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
