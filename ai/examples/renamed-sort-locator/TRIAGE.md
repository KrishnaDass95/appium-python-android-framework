# Triage: test_sort_by_name[name-asc]

**Verdict:** locator broken

**Evidence**
- Traceback ends at `pages/catalog_page.py:63` `self.tap(self._sort_button)` via `wait_for_clickable`, with `NoSuchElementError: An element could not be located on the page using the given search parameters.` The only recorded step, `Sort products by <SortOption.NAME_ASC ...>`, is broken, so the failure is on the first tap and not in the assertion.
- Source state in the report: `-    _sort_button = id_locator("sortIV")` / `+    _sort_button = id_locator("sortIV_renamed")` in `pages/catalog_page.py`, uncommitted. The run used `sortIV_renamed`.
- Page source: the catalog's real sort button is `com.saucelabs.mydemoapp.android:id/sortIV`. `sortIV_renamed` does not appear anywhere in the XML. Other catalog ids (`menuIV`, `cartRL`, `productRV`) are present, so the page source is the catalog.
- Screenshot: the app is on the Products catalog and the sort icon (A/B arrows, top right) is visible, so the app and the screen are fine.

**Suggested fix (human-applied):** set `_sort_button = id_locator("sortIV")` at `pages/catalog_page.py:20`. This is the uncommitted edit, so reverting it is enough.

**Confidence:** high. The diff, the missing id and the visible button agree. A related improvement would be to include the locator in `BasePage` wait errors; the TimeoutException message is currently empty.
