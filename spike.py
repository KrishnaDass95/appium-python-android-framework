# from appium import webdriver

# from config.settings import settings

# driver = webdriver.Remote(
#     settings.appium_server_url, options=settings.appium.to_appium_options()
# )


# print(driver.current_activity)
# driver.quit()

from appium import webdriver
from appium.options.android import UiAutomator2Options

options = UiAutomator2Options()
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.device_name = "emulator-5554"
options.app_package = "com.saucelabs.mydemoapp.android"
options.app_activity = "com.saucelabs.mydemoapp.android.view.activities.MainActivity"
options.app_wait_activity = "com.saucelabs.mydemoapp.android.view.activities.MainActivity"
options.no_reset = False

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

print("Current activity:", driver.current_activity)
print("Session ID:", driver.session_id)

driver.quit()