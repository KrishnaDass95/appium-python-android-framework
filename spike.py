from appium import webdriver

caps = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "emulator-5554",
    "appium:appPackage": "com.saucelabs.mydemoapp.rn",
    "appium:appActivity": ".MainActivity",
    "appium:noReset": True,
}

driver = webdriver.Remote("http://127.0.0.1:4723", caps)

print(driver.current_activity)

driver.quit()
