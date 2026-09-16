import allure

from pages.base_page import BasePage
from pages.cart_page import CartPage
from view_components.element_locator import accessibility_locator, id_locator


class ProductPage(BasePage):
    _product_title = id_locator("productTV")
    _product_price = id_locator("priceTV")
    _add_to_cart_button = accessibility_locator("Tap to add product to cart")
    _increase_count_button = id_locator("plusIV")
    _decrease_count_button = id_locator("minusIV")
    _cart_button = id_locator("cartIV")
    _cart_count_button = id_locator("cartTV")

    @allure.step("Get product title")
    def get_product_name(self) -> str:
        return self.get_text(self._product_title)

    @allure.step("Get product price")
    def get_product_price(self) -> str:
        return self.get_text(self._product_price)

    @allure.step("Increase quantity by {quantity}")
    def increase_quantity(self, quantity: int) -> None:
        for _ in range(quantity):
            self.tap(self._increase_count_button)

    @allure.step("Decrease quantity by {quantity}")
    def decrease_quantity(self, quantity: int) -> None:
        for _ in range(quantity):
            self.tap(self._decrease_count_button)

    @allure.step("Tap Add to Cart")
    def add_product_to_cart(self) -> None:
        self.tap(self._add_to_cart_button)

    @allure.step("Tap cart icon")
    def tap_cart(self) -> CartPage:
        self.tap(self._cart_button)
        cart_page = CartPage(driver=self.driver)
        cart_page.wait_for_element(cart_page._cart_title)
        return cart_page

    @allure.step("Get cart badge count")
    def get_cart_count(self) -> int:
        return int(self.get_text(self._cart_count_button))

    @allure.step("Navigate back")
    def go_back(self) -> None:
        self.driver.back()
