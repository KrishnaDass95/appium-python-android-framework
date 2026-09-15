import allure
import pytest

from tests.base_test import BaseTest


@allure.feature("Authentication")
class TestAuthentication(BaseTest):
    @allure.story("Valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_valid_login(self, catalog_page):
        try:
            catalog_page.tap_menu()
            login_page = catalog_page.tap_login_from_menu()
            login_page.login("test123@sauceDemo", "sauceDemo")
            catalog_page.tap_menu()
            assert catalog_page.get_logout_state_text() == "Log Out"
        finally:
            # Swallow teardown errors so a cleanup failure doesn't cascade
            # into the next test. reset_to_catalog fixture handles app state reset.
            try:
                catalog_page.logout_if_logged_in()
            except Exception:  # noqa: BLE001, S110
                pass


    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="App bug: Invalid creds bypass login")
    def test_invalid_login(self, login_page, catalog_page):

        catalog_page.tap_menu()
        catalog_page.tap_login_from_menu()
        login_page.login("wrongGibber", "wrongJabber")


@allure.feature("Product Catalog")
class TestProductCatalog(BaseTest):

    @allure.story("Test product catalog loads")
    def test_product_catalog_loads(self, catalog_page):

        titles = catalog_page.get_product_titles()
        print(titles)
        assert len(titles) > 0
        assert "Sauce Labs Backpack" in titles


