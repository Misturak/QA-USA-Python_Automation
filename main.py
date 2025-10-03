import data
import helpers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages import UrbanRoutesPage
import pytest

class TestUrbanRoutes:
    @classmethod
    def setup_class(cls):
        # ✅ Updated for Selenium v4+
        options = Options()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)

        if helpers.is_url_reachable(data.URBAN_ROUTES_URL):
            print("Connected to the Urban Routes server")
        else:
            print("Cannot connect to Urban Routes. Check the server is on and still running")

    def test_set_addresses(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        page.set_addresses(data.ADDRESS_FROM, data.ADDRESS_TO)
        assert page.get_from() == data.ADDRESS_FROM
        assert page.get_to() == data.ADDRESS_TO

    def test_select_supportive_plan(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        page.set_addresses(data.ADDRESS_FROM, data.ADDRESS_TO)
        page.select_supportive_plan()
        assert "Supportive" in page.get_active_plan_text()

    def test_fill_phone_number(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        page.set_addresses(data.ADDRESS_FROM, data.ADDRESS_TO)
        page.select_supportive_plan()
        page.input_phone_number(data.PHONE_NUMBER)
        assert page.get_phone_number() == data.PHONE_NUMBER

    def test_add_credit_card(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        page.set_addresses(data.ADDRESS_FROM, data.ADDRESS_TO)
        page.select_supportive_plan()
        page.add_credit_card(data.CARD_NUMBER, data.CARD_CODE)
        assert page.payment_method_is_card()

    def test_add_driver_comment(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        page.set_addresses(data.ADDRESS_FROM, data.ADDRESS_TO)
        page.select_supportive_plan()
        page.add_driver_comment(data.MESSAGE_FOR_DRIVER)
        assert page.get_driver_comment() == data.MESSAGE_FOR_DRIVER

    def test_add_blanket_and_handkerchiefs(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        page.set_addresses(data.ADDRESS_FROM, data.ADDRESS_TO)
        page.select_supportive_plan()
        page.add_blanket_and_handkerchiefs()
        assert page.blanket_added()

    def test_order_ice_creams(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        page.set_addresses(data.ADDRESS_FROM, data.ADDRESS_TO)
        page.select_supportive_plan()
        page.order_ice_creams(2)
        assert page.get_ice_cream_count() == 2

    def test_order_supportive_taxi(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        page.set_addresses(data.ADDRESS_FROM, data.ADDRESS_TO)
        page.select_supportive_plan()
        page.input_phone_number(data.PHONE_NUMBER)
        page.add_driver_comment(data.MESSAGE_FOR_DRIVER)
        page.order_supportive_taxi()
        assert page.order_successful()

    def test_edge_case_empty_addresses(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        page = UrbanRoutesPage(self.driver)
        with pytest.raises(Exception, match="Addresses cannot be empty!"):
            page.set_addresses("", "")

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()