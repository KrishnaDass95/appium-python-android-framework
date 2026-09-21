from appium.webdriver.common.appiumby import AppiumBy

# Standard locator - driver.find_element(AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/loginBtn")
type ElementLocator = tuple[str, str]


def id_locator(element_id: str) -> ElementLocator:
    return (AppiumBy.ID, element_id)


def xpath_locator(xpath: str) -> ElementLocator:
    return (AppiumBy.XPATH, xpath)


def accessibility_locator(label: str) -> ElementLocator:
    return (AppiumBy.ACCESSIBILITY_ID, label)
