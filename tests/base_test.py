import pytest


@pytest.mark.usefixtures("attach_screenshot_on_failure")
class BaseTest:
    pass
