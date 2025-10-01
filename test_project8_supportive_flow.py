import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from pages import UrbanRoutesPage
from helpers import retrieve_phone_code
import data


class TestProject8SupportiveFlow:
    @classmethod
    def setup_class(cls):
        # Build Chrome with performance logs enabled (needed for retrieve_phone_code)
        opts = webdriver.ChromeOptions()
        opts.add_argument("--window-size=1400,900")
        opts.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        # Enable performance log collection (critical for SMS code retrieval)
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        # If chromedriver is on PATH this is enough; otherwise use webdriver_manager in main.py style
        cls.driver = webdriver.Chrome(options=opts, service=Service())
        cls.driver.get(data.APP_URL)

        cls.page = UrbanRoutesPage(cls.driver)

    @classmethod
    def teardown_class(cls):
        try:
            cls.driver.quit()
        except Exception:
            pass

    def test_01_set_address(self):
        self.page.set_addresses(data.FROM_ADDR, data.TO_ADDR)

    def test_02_select_supportive_tariff(self):
        self.page.ensure_supportive_selected()

    def test_03_fill_phone_and_confirm(self):
        # pages.enter_phone_and_confirm will call retrieve_phone_code(self.driver) internally
        self.page.enter_phone_and_confirm(data.PHONE, retrieve_phone_code)

    def test_04_add_credit_card(self):
        self.page.add_credit_card(data.CARD_NUM, data.CARD_EXP, data.CARD_CVV)

    def test_05_write_comment(self):
        self.page.write_comment_for_driver(data.DRIVER_MSG)

    def test_06_toggle_blanket_and_handkerchiefs(self):
        self.page.toggle_blanket_and_verify()

    def test_07_order_two_ice_creams(self):
        self.page.order_ice_creams(2)

    def test_08_place_order_supportive_modal_appears(self):
        self.page.place_supportive_order(data.DRIVER_MSG_ORDER)
