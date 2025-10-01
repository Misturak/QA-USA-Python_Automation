# main.py
import os
import tempfile
import pytest

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

import data
from helpers import retrieve_phone_code
from pages import UrbanRoutesPage


class TestUrbanRoutes:
    # ---------- Driver bootstrap ----------
    @classmethod
    def _build_driver(cls):
        # Chrome options
        opts = webdriver.ChromeOptions()
        opts.add_argument("--window-size=1400,900")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--remote-allow-origins=*")
        opts.add_argument("--no-first-run")
        opts.add_argument("--no-default-browser-check")
        # Isolate profile (helps stability)
        opts.add_argument(f"--user-data-dir={os.path.join(tempfile.gettempdir(), 'chrome_s8_profile')}")

        # Quieter logs
        opts.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        # ✅ Enable performance logging for SMS code retrieval
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)

        driver.get(data.APP_URL)
        return driver

    @classmethod
    def setup_class(cls):
        cls.driver = cls._build_driver()
        cls.page = UrbanRoutesPage(cls.driver)

        # If you had this in Project 7, it lives here now:
        try:
            from helpers import is_url_reachable
            if callable(is_url_reachable) and not is_url_reachable(data.APP_URL):
                raise RuntimeError(f"App URL not reachable: {data.APP_URL}")
        except Exception:
            # ignore if helper not present
            pass

    @classmethod
    def teardown_class(cls):
        try:
            cls.driver.quit()
        except Exception:
            pass

    # ---------- Session resilience ----------
    def _ensure_alive(self):
        """Ping the session; if dead, rebuild driver & page."""
        try:
            self.driver.execute_script("return 1")
        except (InvalidSessionIdException, WebDriverException, AttributeError):
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = self._build_driver()
            self.page = UrbanRoutesPage(self.driver)

    def _retry_if_session_dies(self, action, *args, tries=2, **kwargs):
        """
        Run an action; if the session dies mid-step, rebuild and retry once.
        Usage: self._retry_if_session_dies(lambda: self.page.method(...))
        """
        last_exc = None
        for _ in range(tries):
            self._ensure_alive()
            try:
                return action(*args, **kwargs)
            except (InvalidSessionIdException, WebDriverException) as e:
                last_exc = e
                # loop to rebuild & retry
        if last_exc:
            raise last_exc
        raise RuntimeError("Unknown failure")

    # ---------- Tests (Project 8) ----------
    def test_set_addresses(self):
        self._retry_if_session_dies(lambda: self.page.set_addresses(data.FROM_ADDR, data.TO_ADDR))

    def test_select_supportive_plan(self):
        self._retry_if_session_dies(lambda: self.page.ensure_supportive_selected())

    def test_fill_phone_and_confirm(self):
        try:
            # Re-establish preconditions in case the page reloaded
            self._retry_if_session_dies(
                lambda: self.page.set_addresses(data.FROM_ADDR, data.TO_ADDR).ensure_supportive_selected()
            )
            # Actual phone flow
            self._retry_if_session_dies(
                lambda: self.page.enter_phone_and_confirm(data.PHONE, retrieve_phone_code)
            )
        except Exception as e:
            # --- DIAGNOSTICS ---
            import time, os
            ts = time.strftime("%Y%m%d-%H%M%S")
            os.makedirs("artifacts", exist_ok=True)
            try:
                self.driver.save_screenshot(f"artifacts/phone_fail_{ts}.png")
            except Exception:
                pass
            try:
                with open(f"artifacts/phone_dom_{ts}.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            except Exception:
                pass
            raise e

    def test_add_credit_card(self):
        self._retry_if_session_dies(lambda: self.page.add_credit_card(data.CARD_NUM, data.CARD_EXP, data.CARD_CVV))

    def test_write_comment(self):
        self._retry_if_session_dies(lambda: self.page.write_comment_for_driver(data.DRIVER_MSG))

    def test_toggle_blanket_and_handkerchiefs(self):
        self._retry_if_session_dies(lambda: self.page.toggle_blanket_and_verify())

    def test_order_two_ice_creams(self):
        self._retry_if_session_dies(lambda: self.page.order_ice_creams(2))

    def test_place_order_modal_appears(self):
        self._retry_if_session_dies(lambda: self.page.place_supportive_order(data.DRIVER_MSG_ORDER))


if __name__ == "__main__":
    # Allow `python main.py` to run tests too
    import sys
    sys.exit(pytest.main([__file__, "-vv"]))
