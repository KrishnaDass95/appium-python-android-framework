from appium.options.android import UiAutomator2Options
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Container to hold capabilities
class AppiumCapabilities(BaseModel):
    platform_name: str = "Android"
    automation_name: str = "UiAutomator2"
    device_name: str = "emulator-5554"
    app: str
    app_package: str = "com.saucelabs.mydemoapp.android"
    app_activity: str = "com.saucelabs.mydemoapp.android.view.activities.SplashActivity"
    app_wait_activity: str = "com.saucelabs.mydemoapp.android.*"
    no_reset: bool = False
    new_command_timeout: int = 600

    def to_appium_options(self):
        options = UiAutomator2Options()
        options.platform_name = self.platform_name
        options.automation_name = self.automation_name
        options.device_name = self.device_name
        options.app = self.app
        options.app_package = self.app_package
        options.app_activity = self.app_activity
        options.app_wait_activity = self.app_wait_activity
        options.no_reset = self.no_reset
        options.new_command_timeout = self.new_command_timeout
        return options


def create_default_caps():
    return AppiumCapabilities(
        app="/Users/kaydeee/Developer/portfolio-projects/appium-project/appium-android-portfolio/sauceDemo.apk",
    )


class Settings(BaseSettings):
    # model_config - giving Base settings instructions on how to read env file
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )

    appium_server_url: str = "http://127.0.0.1:4723"
    implicit_wait: int = 10
    appium: AppiumCapabilities = Field(
        # default factory, calls the function each time and reserves new memory for appium caps
        default_factory=create_default_caps
    )


settings = Settings()
