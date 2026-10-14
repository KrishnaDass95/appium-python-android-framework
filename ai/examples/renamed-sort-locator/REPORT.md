# Failure evidence (1 failed)

## Source state

- commit: `dfcfdf0`
- uncommitted changes in pages/tests/config:

```
M pages/catalog_page.py
```

```diff
diff --git a/pages/catalog_page.py b/pages/catalog_page.py
index 832bf6d..03fcda1 100644
--- a/pages/catalog_page.py
+++ b/pages/catalog_page.py
@@ -20 +20 @@ class CatalogPage(BasePage):
-    _sort_button = id_locator("sortIV")
+    _sort_button = id_locator("sortIV_renamed")
```

## test_sort_by_name[name-asc]

- full name: `tests.test_shopping.TestProductCatalog#test_sort_by_name`
- status: broken

### Error message

```
selenium.common.exceptions.TimeoutException: Message:
Stacktrace:
NoSuchElementError: An element could not be located on the page using the given search parameters.
    at AndroidUiautomator2Driver.findElOrEls (~/.appium/node_modules/appium-uiautomator2-driver/node_modules/appium-android-driver/lib/commands/find.ts:93:11)
    at processTicksAndRejections (node:internal/process/task_queues:103:5)
    at AndroidUiautomator2Driver.findElOrElsWithProcessing (~/.nvm/versions/node/v24.11.1/lib/node_modules/appium/node_modules/@appium/base-driver/lib/basedriver/commands/find.ts:60:12)
    at AndroidUiautomator2Driver.findElement (~/.nvm/versions/node/v24.11.1/lib/node_modules/appium/node_modules/@appium/base-driver/lib/basedriver/commands/find.ts:75:12)
```

### Traceback

```
tests/test_shopping.py:94: in test_sort_by_name
    catalog_page.tap_sort_by(option)
pages/catalog_page.py:63: in tap_sort_by
    self.tap(self._sort_button)
pages/base_page.py:34: in tap
    self.wait_for_clickable(locator, timeout).click()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pages/base_page.py:25: in wait_for_clickable
    return self._wait(timeout).until(EC.element_to_be_clickable(locator))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.12/site-packages/selenium/webdriver/support/wait.py:121: in until
    raise TimeoutException(message, screen, stacktrace)
E   selenium.common.exceptions.TimeoutException: Message:
E   Stacktrace:
E   NoSuchElementError: An element could not be located on the page using the given search parameters.
E       at AndroidUiautomator2Driver.findElOrEls (~/.appium/node_modules/appium-uiautomator2-driver/node_modules/appium-android-driver/lib/commands/find.ts:93:11)
E       at processTicksAndRejections (node:internal/process/task_queues:103:5)
E       at AndroidUiautomator2Driver.findElOrElsWithProcessing (~/.nvm/versions/node/v24.11.1/lib/node_modules/appium/node_modules/@appium/base-driver/lib/basedriver/commands/find.ts:60:12)
E       at AndroidUiautomator2Driver.findElement (~/.nvm/versions/node/v24.11.1/lib/node_modules/appium/node_modules/@appium/base-driver/lib/basedriver/commands/find.ts:75:12)
```

### Steps (what the test did before it failed)

```
[broken] Sort products by <SortOption.NAME_ASC: 'Ascending order by name'>
```

### Evidence files

- `test_sort_by_name_name-asc/log.txt`
- `test_sort_by_name_name-asc/failure-test_sort_by_name_name-asc.png`
- `test_sort_by_name_name-asc/page-source-test_sort_by_name_name-asc.xml`
