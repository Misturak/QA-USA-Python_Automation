from selenium.webdriver.common.by import By
from helpers import retrieve_phone_code

class UrbanRoutesPage:
    def __init__(self, driver):
        self.driver = driver

    # Locators
    FROM_FIELD = (By.ID, "from-field")
    TO_FIELD = (By.ID, "to-field")
    CALL_TAXI_BUTTON = (By.ID, "call-taxi-btn")
    SUPPORTIVE_PLAN = (By.XPATH, "//div[contains(@class, 'plan') and contains(text(), 'Supportive')]")
    ACTIVE_PLAN = (By.XPATH, "//div[contains(@class, 'plan active')]")
    PHONE_NUMBER_FIELD = (By.ID, "phone-number-field")
    CONFIRMATION_FIELD = (By.ID, "confirmation-field")
    PAYMENT_METHOD_BUTTON = (By.ID, "payment-method-btn")
    ADD_CARD_BUTTON = (By.ID, "add-card-btn")
    CARD_NUMBER_FIELD = (By.ID, "card-number-field")
    CARD_CODE_FIELD = (By.ID, "card-code-field")
    LINK_BUTTON = (By.ID, "link-btn")
    PAYMENT_METHOD_TEXT = (By.ID, "payment-method-text")
    COMMENT_FIELD = (By.ID, "driver-comment-field")
    BLANKET_SLIDER = (By.ID, "blanket-slider")
    ORDER_BUTTON = (By.ID, "order-supportive-btn")
    CAR_SEARCH_MODAL = (By.ID, "car-search-modal")
    ICE_CREAM_BUTTON = (By.ID, "ice-cream-btn")
    ICE_CREAM_COUNT = (By.ID, "ice-cream-count")

    # Address Methods
    def set_addresses(self, from_address: str, to_address: str):
        if not from_address or not to_address:
            raise Exception("Addresses cannot be empty!")
        self.driver.find_element(*self.FROM_FIELD).clear()
        self.driver.find_element(*self.FROM_FIELD).send_keys(from_address)
        self.driver.find_element(*self.TO_FIELD).clear()
        self.driver.find_element(*self.TO_FIELD).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.FROM_FIELD).get_attribute("value")

    def get_to(self):
        return self.driver.find_element(*self.TO_FIELD).get_attribute("value")

    # Supportive Plan
    def select_supportive_plan(self):
        self.driver.find_element(*self.CALL_TAXI_BUTTON).click()
        self.driver.find_element(*self.SUPPORTIVE_PLAN).click()

    def get_active_plan_text(self):
        return self.driver.find_element(*self.ACTIVE_PLAN).text

    # Phone Number
    def input_phone_number(self, phone_number: str):
        field = self.driver.find_element(*self.PHONE_NUMBER_FIELD)
        field.clear()
        field.send_keys(phone_number)
        code = retrieve_phone_code(self.driver)
        self.driver.find_element(*self.CONFIRMATION_FIELD).send_keys(code)

    def get_phone_number(self):
        return self.driver.find_element(*self.PHONE_NUMBER_FIELD).get_attribute("value")

    # Credit Card
    def add_credit_card(self, card_number: str, card_code: str):
        self.driver.find_element(*self.PAYMENT_METHOD_BUTTON).click()
        self.driver.find_element(*self.ADD_CARD_BUTTON).click()
        self.driver.find_element(*self.CARD_NUMBER_FIELD).clear()
        self.driver.find_element(*self.CARD_NUMBER_FIELD).send_keys(card_number)
        self.driver.find_element(*self.CARD_CODE_FIELD).clear()
        self.driver.find_element(*self.CARD_CODE_FIELD).send_keys(card_code)
        self.driver.find_element(*self.LINK_BUTTON).click()

    def payment_method_is_card(self):
        return self.driver.find_element(*self.PAYMENT_METHOD_TEXT).text == "Card"

    # Driver Comment
    def add_driver_comment(self, comment: str):
        field = self.driver.find_element(*self.COMMENT_FIELD)
        field.clear()
        field.send_keys(comment)

    def get_driver_comment(self):
        return self.driver.find_element(*self.COMMENT_FIELD).get_attribute("value")

    # Blanket
    def add_blanket_and_handkerchiefs(self):
        self.driver.find_element(*self.BLANKET_SLIDER).click()

    def blanket_added(self):
        return self.driver.find_element(*self.BLANKET_SLIDER).get_property("checked")

    # Ice Creams
    def order_ice_creams(self, count: int):
        for _ in range(count):
            self.driver.find_element(*self.ICE_CREAM_BUTTON).click()

    def get_ice_cream_count(self):
        return int(self.driver.find_element(*self.ICE_CREAM_COUNT).text)

    # Taxi Order
    def order_supportive_taxi(self):
        self.driver.find_element(*self.ORDER_BUTTON).click()

    def order_successful(self):
        return self.driver.find_element(*self.CAR_SEARCH_MODAL).is_displayed()