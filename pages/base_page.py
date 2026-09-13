from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from view_components.element_locator import ElementLocator


class BasePage:
    # Tests calls Individual pages, ind pages
    # call BasePage and BasePage calls Appium for actions
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.driver.implicitly_wait(0)

    # Waits
    def _wait(self, timeout: int) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)

    def wait_for_element(self, locator: ElementLocator, timeout: int = 10) -> WebElement:
        return self._wait(timeout).until(EC.presence_of_element_located(locator))

    def wait_for_clickable(self, locator: ElementLocator, timeout: int = 10) -> WebElement:
        return self._wait(timeout).until(EC.element_to_be_clickable(locator))

    def wait_for_disappearance(self, locator: ElementLocator, timeout: int = 10):
        self._wait(timeout).until(EC.invisibility_of_element_located(locator))

    # Actions
    def tap(self, locator: ElementLocator, timeout: int = 10) -> None:
        self.wait_for_clickable(locator, timeout).click()

    def send_keys(self, locator: ElementLocator, text: str, timeout: int = 10) -> None:
        element = self.wait_for_clickable(locator, timeout)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: ElementLocator, timeout: int = 10) -> str:
        return self.wait_for_element(locator, timeout).text

    def get_elements(self, locator: ElementLocator, timeout: int = 10) -> list:
        self.wait_for_element(locator, timeout)
        # the *locator unpacks the strategy and value
        # for the method signature required by find_elements
        return self.driver.find_elements(*locator)

    def find_by_uiautomator(self, selector: str, timeout: int = 10) -> WebElement:
        from appium.webdriver.common.appiumby import AppiumBy
        return self._wait(timeout).until(
            EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, selector))
        )
