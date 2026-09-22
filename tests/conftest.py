import os
import sys
from urllib.parse import urlparse

import allure
import pytest
from appium import webdriver
from appium.webdriver.appium_service import AppiumService

from config.settings import settings
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage
from pages.product_detail_page import ProductPage


def pytest_sessionstart(session):
    os.makedirs("allure-results", exist_ok=True)
    with open("allure-results/environment.properties", "w") as f:
        f.write(f"App={settings.appium.app_package}\n")
        f.write(f"Platform={settings.appium.platform_name}\n")
        f.write(f"Device={settings.appium.device_name}\n")
        f.write(f"Python={sys.version_info.major}.{sys.version_info.minor}\n")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session")
def appium_server():
    if not settings.auto_start_server:
        yield
        return
    service = AppiumService()
    parsed = urlparse(settings.appium_server_url)
    host = parsed.hostname
    port = parsed.port
    try:
        service.start(args=["--address", host, "--port", str(port)])
    except Exception as e:
        pytest.exit(f"Appium server could not start: {e}", returncode=3)
    yield
    service.stop()


@pytest.fixture(scope="session")
def driver(appium_server):
    d = webdriver.Remote(settings.appium_server_url, options=settings.appium.to_appium_options())
    d.implicitly_wait(0)
    yield d
    d.quit()


# function scoped page fixtures, by default they're scoped
# to test function


@pytest.fixture
def catalog_page(driver, reset_to_catalog) -> CatalogPage:
    # Explicit dependency on reset_to_catalog ensures the app is already in a
    # clean state (terminate + activate) before we wait for the catalog.
    page = CatalogPage(driver)
    page.wait_for_element(page._menu_button, timeout=15)
    return page


@pytest.fixture
def login_page(driver, catalog_page) -> LoginPage:
    catalog_page.tap_menu()
    catalog_page.tap_login_from_menu()
    return LoginPage(driver)


@pytest.fixture
def product_detail_page(driver) -> ProductPage:
    return ProductPage(driver)


# Runs before every test.
# terminate_app kills the process (clears any dialogs, stuck screens, broken state),
# then activate_app relaunches fresh on the catalog screen.
# activate_app alone is not enough — if the app is in the foreground with a dialog,
# activate_app does nothing; terminate first to guarantee a clean relaunch.
# Running in setup (not teardown) means the first test also gets a clean launch,
# bypassing any first-run UI that appears when the session creates the driver.
# Swallowed silently — if reset fails we still want the next test to attempt.
@pytest.fixture(autouse=True)
def reset_to_catalog(driver):
    try:
        driver.terminate_app("com.saucelabs.mydemoapp.android")
        driver.activate_app("com.saucelabs.mydemoapp.android")
    except Exception:  # noqa: BLE001, S110
        pass
    yield


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
            attachment_type=allure.attachment_type.PNG,
        )
