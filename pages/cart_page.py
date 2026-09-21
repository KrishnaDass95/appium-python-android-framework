import allure
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage
from view_components.element_locator import id_locator, xpath_locator


class CartPage(BasePage):
    # Page-level locators — used with driver (self.wait_for_element, self.tap, etc.)
    _cart_title = id_locator("productTV")
    _proceed_to_checkout_btn = id_locator("cartBt")
    _total_items_label = id_locator("itemsTV")
    _total_price_label = id_locator("totalPriceTV")

    # Absolute XPath to cart rows — UiAutomator2 does not support relative XPath
    # (element.find_elements(XPATH, "./child")) reliably; always returns empty.
    # Full resource-id in the XPath string is required because id_locator's
    # auto-prefix only applies to AppiumBy.ID, not raw XPath strings.
    _cart_item_rows = xpath_locator(
        "//androidx.recyclerview.widget.RecyclerView"
        '[@resource-id="com.saucelabs.mydemoapp.android:id/productRV"]'
        "/android.view.ViewGroup"
    )

    # Item-scoped locators — used with element.find_element(*locator), NOT driver
    # These IDs repeat in every row, so they only make sense within a specific row element
    _ITEM_TITLE = id_locator("titleTV")
    _ITEM_PRICE = id_locator("priceTV")
    _ITEM_QTY = id_locator("noTV")
    _ITEM_PLUS_BTN = id_locator("plusIV")
    _ITEM_MINUS_BTN = id_locator("minusIV")
    _ITEM_REMOVE_BTN = id_locator("removeBt")

    # --- Private helpers ---

    def _get_cart_items(self) -> list[WebElement]:
        return self.get_elements(self._cart_item_rows)

    def _get_item(self, index: int) -> WebElement:
        items = self._get_cart_items()
        if index >= len(items):
            raise IndexError(f"Cart has {len(items)} item(s), index {index} is out of range")
        return items[index]

    # --- Cart item actions ---

    @allure.step("Increase quantity of item at index {item_index}")
    def increase_item_quantity(self, item_index: int) -> None:
        item = self._get_item(item_index)
        item.find_element(*self._ITEM_PLUS_BTN).click()

    @allure.step("Decrease quantity of item at index {item_index}")
    def decrease_item_quantity(self, item_index: int) -> None:
        item = self._get_item(item_index)
        item.find_element(*self._ITEM_MINUS_BTN).click()

    @allure.step("Remove item at index {item_index}")
    def remove_item(self, item_index: int) -> None:
        item = self._get_item(item_index)
        item.find_element(*self._ITEM_REMOVE_BTN).click()

    # --- Cart item reads ---

    @allure.step("Get name of item at index {item_index}")
    def get_item_name(self, item_index: int) -> str:
        item = self._get_item(item_index)
        return item.find_element(*self._ITEM_TITLE).text

    @allure.step("Get price of item at index {item_index}")
    def get_item_price(self, item_index: int) -> str:
        item = self._get_item(item_index)
        return item.find_element(*self._ITEM_PRICE).text

    @allure.step("Get quantity of item at index {item_index}")
    def get_item_quantity(self, item_index: int) -> int:
        item = self._get_item(item_index)
        return int(item.find_element(*self._ITEM_QTY).text)

    @allure.step("Get cart item count")
    def get_item_count(self) -> int:
        return len(self._get_cart_items())

    # --- Page-level reads and actions ---

    @allure.step("Get total items label")
    def get_total_items_label(self) -> str:
        return self.get_text(self._total_items_label)

    @allure.step("Get total price")
    def get_total_price(self) -> str:
        return self.get_text(self._total_price_label)

    @allure.step("Tap Proceed to Checkout")
    def tap_proceed_to_checkout(self):
        self.tap(self._proceed_to_checkout_btn)
