import allure
import pytest
from appium import webdriver

from config.settings import settings
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductPage


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session")
def driver():
    d = webdriver.Remote(
        settings.appium_server_url, options=settings.appium.to_appium_options()
    )
    d.implicitly_wait(0)
    yield d
    d.quit()


# function scoped page fixtures, by default they're scoped
# to test function

@pytest.fixture
def catalog_page(driver) -> CatalogPage:
    return CatalogPage(driver)

@pytest.fixture
def login_page(driver, catalog_page) -> LoginPage:
    catalog_page.tap_menu()
    catalog_page.tap_login_from_menu()
    return LoginPage(driver)

@pytest.fixture
def product_detail_page(driver) -> ProductPage:
    return ProductPage(driver)

# Runs after every test regardless of pass/fail.
# terminate_app kills the process (clears any dialogs, stuck screens, broken state),
# then activate_app relaunches it fresh on the catalog screen.
# activate_app alone is not enough — it only works if the app is backgrounded.
# If it's in the foreground with a dialog, activate_app does nothing.
# Swallowed silently — if reset itself fails, we still want the next test to attempt.
@pytest.fixture(autouse=True)
def reset_to_catalog(driver):
    yield
    try:
        driver.terminate_app("com.saucelabs.mydemoapp.android")
        driver.activate_app("com.saucelabs.mydemoapp.android")
    except Exception:  # noqa: BLE001, S110
        pass


# Runs after every test. If the test itself failed (rep_call.failed),
# captures a screenshot and attaches it to the Allure report.
# tryfirst + hookwrapper in pytest_runtest_makereport (above) ensures
# rep_call is set before this fixture's teardown reads it.
@pytest.fixture(autouse=True)
def attach_screenshot_on_failure(request, driver):
    yield
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"failure-{request.node.name}",
            attachment_type=allure.attachment_type.PNG
        )

