from appium import webdriver

from config.settings import settings

driver = webdriver.Remote(
    settings.appium_server_url, options=settings.appium.to_appium_options()
)


print(driver.current_activity)
driver.quit()
