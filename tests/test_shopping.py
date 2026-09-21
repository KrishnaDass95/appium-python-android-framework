import contextlib

import allure
import pytest

from tests.base_test import BaseTest


@allure.feature("Authentication")
class TestAuthentication(BaseTest):
    @allure.story("Valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.smoke
    def test_valid_login(self, catalog_page):
        try:
            catalog_page.tap_menu()
            login_page = catalog_page.tap_login_from_menu()
            login_page.login("bob@example.com", "10203040")
            catalog_page.tap_menu()
            assert catalog_page.get_logout_state_text() == "Log Out"
        finally:
            # Swallow teardown errors so a cleanup failure doesn't cascade
            # into the next test. reset_to_catalog fixture handles app state reset.
            with contextlib.suppress(Exception):
                catalog_page.logout_if_logged_in()

    @allure.story("Invalid credentials")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="App bug: Invalid creds bypass login")
    def test_invalid_login(self, login_page, catalog_page):

        catalog_page.tap_menu()
        catalog_page.tap_login_from_menu()
        login_page.login("wrongGibber", "wrongJabber")


@allure.feature("Product Catalog")
class TestProductCatalog(BaseTest):
    @allure.story("Test product catalog loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_catalog_loads(self, catalog_page):

        titles = catalog_page.get_product_titles()
        print(titles)
        assert len(titles) > 0
        assert "Sauce Labs Backpack" in titles

    @allure.story("Test product detail page")
    @allure.severity(allure.severity_level.NORMAL)
    # @pytest.mark.smoke
    def test_product_detail_navigation(self, catalog_page):

        titles = catalog_page.get_product_titles()
        first_product_title = titles[0]
        product_page = catalog_page.tap_product_by_name(first_product_title)
        assert first_product_title == product_page.get_product_name()

    @allure.story("Cart reflects correct item quantity")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_cart_item_value(self, catalog_page):

        qty_to_add = 2
        # default qty is 1, so after adding 2, we're asserting the total qty
        total_qty = 3
        cart_page = None
        try:
            titles = catalog_page.get_product_titles()
            first_product_title = titles[0]
            product_page = catalog_page.tap_product_by_name(first_product_title)
            product_page.increase_quantity(qty_to_add)
            product_page.add_product_to_cart()
            assert product_page.get_cart_count() == total_qty

            cart_page = product_page.tap_cart()
            assert cart_page.get_item_quantity(0) == total_qty + 4  # failure added to test allure
        finally:
            with contextlib.suppress(Exception):
                if cart_page is not None:
                    cart_page.remove_item(0)
