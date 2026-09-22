# Appium Android Framework

UI test automation for the [Sauce Labs My Demo App](https://github.com/saucelabs/my-demo-app-android),
an open-source Android app built as a practice target for mobile automation. The suite drives a real
emulator or device through Appium 2 and UiAutomator2, produces Allure reports with step-level detail
and failure screenshots, and runs on every push via GitHub Actions on a headless emulator.

Five tests cover login and the product catalog. The point of the project is the framework underneath
them: a page object layer with no shared state, explicit waits everywhere, config driven entirely by
environment variables, and test isolation that holds up when a test fails mid-flow.

## Stack

| | |
|---|---|
| Language | Python 3.12 |
| Automation | Appium 2, UiAutomator2 driver |
| Client | appium-python-client >= 4.4, selenium >= 4.21 |
| Test runner | pytest >= 8.3 |
| Reporting | allure-pytest >= 2.13 |
| Config | pydantic-settings >= 2.3 |
| Tooling | uv, ruff, mypy, pre-commit |

## Architecture

Four layers, each with one job.

`config/settings.py` holds two pydantic models. `AppiumCapabilities` describes the session — platform,
device, APK path, package, activity, reset behaviour — and converts itself to a `UiAutomator2Options`
object. `Settings` wraps it along with the server URL and wait defaults. Both read from `.env`, using
`__` as the nesting delimiter, so `APPIUM__NO_RESET=true` sets `settings.appium.no_reset`. Nothing in
the test code constructs capabilities; there is one settings object and it comes from the environment.

`view_components/element_locator.py` is three functions that return `(strategy, value)` tuples:
`id_locator`, `xpath_locator`, `accessibility_locator`. Small, but it means locators are typed
(`ElementLocator`) and a page object never mentions `AppiumBy` directly.

`pages/base_page.py` is the only place that talks to Appium. Waits, taps, text reads, presence checks,
UiAutomator selector queries — all of it lives there, and the concrete pages inherit it. When
something about Appium interaction needs to change, there is one file to change.

`tests/conftest.py` owns the driver and the fixtures. `tests/base_test.py` is a two-line class that
attaches the failure-screenshot fixture to every test class that inherits it.

```
config/
  settings.py                  AppiumCapabilities + Settings, read from .env
pages/
  base_page.py                 every Appium interaction
  catalog_page.py              CatalogPage, SortOption
  login_page.py                LoginPage
  product_detail_page.py       ProductPage
  cart_page.py                 CartPage
view_components/
  element_locator.py           id / xpath / accessibility locator helpers
tests/
  conftest.py                  driver, page fixtures, autouse reset + screenshot
  base_test.py                 BaseTest
  test_shopping.py             the tests
.github/workflows/
  ci-emulator.yml              GitHub Actions emulator pipeline
```

## Design decisions

**Page objects hold no state.** Locators are class attributes; the only instance data is the driver.
Two tests can build the same page object in any order and neither can affect the other. It also means
a locator change is a one-line edit in one place rather than a hunt through setup code.

**One session-scoped driver, with resets between tests.** Creating an Appium session takes several
seconds, so the suite creates one and reuses it. The risk is obvious: a test that dies with a dialog
open leaves the next test staring at a dialog. Two things guard against that. An autouse fixture calls
`terminate_app` then `activate_app` before every test, and each test that mutates app state cleans up
in a `finally` block wrapped in `contextlib.suppress`, so a cleanup failure cannot cascade.

The kill-then-relaunch order matters. `activate_app` on its own does nothing when the app is already
in the foreground, which is exactly the case you are trying to recover from. Terminating first
guarantees a cold start. Running it in setup rather than teardown also means the first test gets a
clean launch, past any first-run UI that appeared while the session was being created.

**Implicit waits are off; every wait is explicit.** The driver is set to `implicitly_wait(0)`. Mixing
implicit and explicit waits produces timeouts that are neither value and are miserable to debug, so
there is only one waiting mechanism: `WebDriverWait` in `base_page`, with a per-call timeout.

**Taps retry on stale elements.** Android re-renders lists mid-transition, so an element found a
moment ago can be detached by the time you click it. `tap()` retries up to three times on
`StaleElementReferenceException` and re-raises on the last attempt. Other exceptions propagate
immediately — this handles one specific race, not failure in general.

**Navigation returns the next page.** `catalog_page.tap_login_from_menu()` returns a `LoginPage`, and
before returning it waits for an element that only exists on that screen. The wait is the assertion
that navigation actually happened, so tests read as a chain of screens and never have to sequence
their own waits.

**Row-scoped locators in the cart.** Cart rows repeat the same resource IDs, so `CartPage` splits its
locators: page-level ones resolve against the driver, item-level ones resolve against a row element
found by absolute XPath. Relative XPath (`./child`) is unreliable under UiAutomator2 and tends to
return empty lists, hence the absolute path.

## Setup

You need Python 3.12, [uv](https://docs.astral.sh/uv/), Node 20+, the Android SDK with platform-tools,
and a running emulator or a connected device.

```bash
git clone <this repo>
cd appium-android-portfolio
uv sync

npm install -g appium
appium driver install uiautomator2
```

Download the demo app APK:

```bash
curl -L -o sauceDemo.apk \
  https://github.com/saucelabs/my-demo-app-android/releases/download/2.2.0/mda-2.2.0-25.apk
```

Then copy `.env.example` to `.env` and point `APPIUM__APP` at that file. The path must be absolute.

```
APPIUM_SERVER_URL=http://127.0.0.1:4723
APPIUM__APP=/absolute/path/to/sauceDemo.apk
APPIUM__APP_PACKAGE=com.saucelabs.mydemoapp.android
APPIUM__APP_ACTIVITY=com.saucelabs.mydemoapp.android.view.activities.SplashActivity
APPIUM__APP_WAIT_ACTIVITY=com.saucelabs.mydemoapp.android.*
APPIUM__NO_RESET=true
IMPLICIT_WAIT=10
AUTO_START_SERVER=false
```

`APPIUM__NO_RESET=true` keeps the installed app between sessions, which is what you want locally.
CI sets it to `false` so every run installs the APK fresh.

Start Appium in its own terminal and leave it running:

```bash
appium
```

To install the pre-commit hooks (ruff and mypy run on every commit):

```bash
uv run pre-commit install
```

## Running tests

```bash
uv run pytest                          # everything
uv run pytest -m smoke                 # smoke only
uv run pytest -k test_valid_login       # one test
uv run pytest --collect-only            # should collect 5
```

Allure results are written on every run — `--alluredir=allure-results --clean-alluredir` is in the
pytest config, so there is nothing to remember. To view the report:

```bash
allure serve allure-results
```

Every page method is an `@allure.step`, so the report shows the actual sequence of taps and reads for
each test. Failures get a screenshot attached automatically by an autouse fixture. `pytest_sessionstart`
writes the app package, platform, device and Python version into the report as environment metadata.

## Tests

Five tests in `tests/test_shopping.py`, split into `TestAuthentication` and `TestProductCatalog`.

`test_valid_login` logs in as `bob@example.com` and confirms the menu item flipped from "Log In" to
"Log Out", then logs back out.

`test_invalid_login` is skipped. The demo app accepts invalid credentials and logs you in anyway, so
there is no failure state to assert on. The skip reason records the app bug rather than hiding the gap.

`test_product_catalog_loads` checks the catalog renders and that a known product is in it.

`test_product_detail_navigation` opens the first product and asserts the detail page shows the same
title the catalog did. Reaching the product requires a `UiScrollable` scroll and then clicking the
product image rather than its title, since the title is not the tap target.

`test_cart_item_value` raises the quantity to three on the product page, adds to cart, asserts the
cart badge reads three, opens the cart and asserts the row quantity matches. It removes the item in
`finally`.

The `smoke` marker currently tags the cart test. `regression` is declared and reserved for the
extended coverage below.

## CI

`.github/workflows/ci-emulator.yml` runs on pushes to `main` and on pull requests.

The job installs Python 3.12, uv, Node and Appium with the UiAutomator2 driver, then enables KVM —
hardware virtualisation is required for an x86_64 emulator on Linux, and forgetting it is the usual
reason Android CI fails. It downloads the demo APK from the Sauce Labs release, then hands off to
`reactivecircus/android-emulator-runner`, which boots a headless Pixel 6 on API 31 with animations
disabled, installs the APK over adb, starts Appium in the background and runs pytest. Capabilities
come in as environment variables, so no config file changes between local and CI.

Allure results and the Appium server log are uploaded as artifacts with `if: always()`, so a failed
run still leaves you a report and a server log to read.

## Roadmap

- Wire up `AUTO_START_SERVER=true` as the default. The `appium_server` fixture already starts and
  stops `AppiumService` programmatically; it is off by default while the manual workflow is in use.
- Jenkins pipelines for three more targets: a physical device, BrowserStack and AWS Device Farm. The
  `extra_caps` field on `AppiumCapabilities` exists for the vendor-specific capabilities these need.
- Catalog sort coverage. `SortOption` and `CatalogPage.tap_sort_by()` are implemented but untested.
- Checkout flow, starting from `CartPage.tap_proceed_to_checkout()`.
