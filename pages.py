# pages.py
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


class UrbanRoutesPage:
    """Page Object Model for Urban Routes app."""

    # ---------- Locators (adjust if your app differs) ----------
    FROM_INPUT = (By.ID, "from")
    TO_INPUT   = (By.ID, "to")

    COOKIE_ACCEPT = (By.CSS_SELECTOR, "[data-test='accept-cookies'], #accept, .cookie-accept")

    # Supportive tariff (we click the “card” that has title Supportive)
    SUPPORTIVE_CARD = (By.XPATH, "//div[contains(@class,'tcard')]"
                                 "[.//div[contains(@class,'tcard-title') and normalize-space()='Supportive']]")
    SUPPORTIVE_CARD_BTN = (By.XPATH, ".//button[contains(@class,'tcard-i')]")  # inside the card
    SUPPORTIVE_CARD_BTN_ACTIVE = (By.XPATH, ".//button[contains(@class,'tcard-i') and contains(@class,'active')]")

    # Phone/SMS
    # We’ll detect dynamically via robust locators in the method; these are defaults:
    PHONE_INPUT       = (By.CSS_SELECTOR, "input[name='phone']")
    SEND_CODE_BTN     = (By.CSS_SELECTOR, "[data-test='send-sms-code']")
    CODE_INPUT        = (By.CSS_SELECTOR, "input[name='sms_code']")
    CONFIRM_PHONE_BTN = (By.CSS_SELECTOR, "[data-test='confirm-phone']")

    # Card (left as-is; you can keep your working version)
    ADD_CARD_BTN     = (By.CSS_SELECTOR, "[data-test='add-card']")
    CARD_IFRAME      = (By.CSS_SELECTOR, "iframe[name*='card'], iframe[src*='card'], iframe.card-iframe")
    CARD_NUMBER      = (By.CSS_SELECTOR, "input[name='card-number']")
    CARD_EXPIRY      = (By.CSS_SELECTOR, "input[name='card-expiry']")
    CARD_CVV         = (By.CSS_SELECTOR, "input[name='card-cvv']")
    LINK_CARD_BTN    = (By.CSS_SELECTOR, "[data-test='link-card']")
    CARD_LINKED_BADGE= (By.CSS_SELECTOR, "[data-test='card-linked']")

    # Comment / extras / order (use what you already had if it works)
    COMMENT_TEXTAREA = (By.CSS_SELECTOR, "textarea[name='driver-comment']")
    BLANKET_TOGGLE       = (By.CSS_SELECTOR, "[data-test='toggle-blanket']")
    BLANKET_STATE_ASSERT = (By.CSS_SELECTOR, "[data-test='blanket-state'].on")
    ICECREAM_PLUS = (By.CSS_SELECTOR, "[data-test='ice-cream-plus']")
    ICECREAM_QTY  = (By.CSS_SELECTOR, "[data-test='ice-cream-qty']")
    ORDER_BTN            = (By.CSS_SELECTOR, "[data-test='order-supportive']")
    DRIVER_MESSAGE_INPUT = (By.CSS_SELECTOR, "textarea[name='driver-message']")
    SEARCH_MODAL         = (By.CSS_SELECTOR, "[data-test='car-search-modal']")

    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------- Small helpers ----------
    def _maybe_click(self, locator, timeout=2):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator)).click()
        except TimeoutException:
            pass

    def _scroll_into_view(self, el):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", el)

    def _try_js_click(self, el):
        self.driver.execute_script("arguments[0].click();", el)

    # ---------- Common actions ----------
    def set_addresses(self, from_addr: str, to_addr: str):
        self._maybe_click(self.COOKIE_ACCEPT)
        f = self.wait.until(EC.element_to_be_clickable(self.FROM_INPUT))
        f.clear(); f.send_keys(from_addr)
        t = self.wait.until(EC.element_to_be_clickable(self.TO_INPUT))
        t.clear(); t.send_keys(to_addr)
        return self

    def ensure_supportive_selected(self):
        """
        Select the 'Supportive' tariff card and wait until its inner button gains 'active'.
        Handles overlays/tooltip intercepts by clicking alternate targets and JS-click fallback.
        """
        from selenium.webdriver import ActionChains

        # 1) Find the card by its title
        card = self.wait.until(EC.visibility_of_element_located(self.SUPPORTIVE_CARD))
        self._scroll_into_view(card)

        # Helper to read active state safely
        def _is_active():
            try:
                btn = card.find_element(*self.SUPPORTIVE_CARD_BTN)
                cls = btn.get_attribute("class") or ""
                return "active" in cls
            except Exception:
                return False

        # If already active, we're done
        if _is_active():
            return self

        # 2) Prefer the inner button if it's displayed
        click_targets = []
        try:
            btn = card.find_element(*self.SUPPORTIVE_CARD_BTN)
            if btn.is_displayed():
                click_targets.append(btn)
        except Exception:
            pass

        # Fallbacks: title, then the card itself
        try:
            title = card.find_element(By.XPATH, ".//div[contains(@class,'tcard-title')]")
            click_targets.append(title)
        except Exception:
            pass
        click_targets.append(card)

        # 3) Try a few ways to click: normal click → Actions → JS click
        for target in click_targets:
            self._scroll_into_view(target)
            try:
                # normal click if clickable
                try:
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, ".")))  # noop wait
                except Exception:
                    pass
                target.click()
            except Exception:
                # try Actions (moves past overlays)
                try:
                    ActionChains(self.driver).move_to_element(target).pause(0.05).click().perform()
                except Exception:
                    # JS fallback
                    try:
                        self._try_js_click(target)
                    except Exception:
                        continue  # try next target

            # 4) Check if it became active after any click attempt
            if self.wait.until(lambda d: _is_active(), message="Supportive still not active after click attempts"):
                return self

        # If we got here, no target succeeded
        raise TimeoutException("Could not activate 'Supportive' tariff card (button never became active).")

    # ---------- Phone flow (robust + uses helpers.retrieve_phone_code(driver)) ----------
    def ensure_phone_section_visible(self):
        """
        If the phone field is in a tab/accordion/modal, try to reveal it gracefully.
        Safe to call even if it's already visible.
        """
        from selenium.webdriver.common.by import By

        # if already present & visible, stop
        for loc in [
            (By.CSS_SELECTOR, "input[name='phone']"),
            (By.CSS_SELECTOR, "input[type='tel']"),
            (By.XPATH, "//input[@inputmode='tel' or @inputmode='numeric']"),
        ]:
            els = self.driver.find_elements(*loc)
            if els:
                try:
                    if WebDriverWait(self.driver, 2).until(EC.visibility_of(els[0])):
                        self._scroll_into_view(els[0])
                        return self
                except TimeoutException:
                    pass

        # try common triggers
        triggers = [
            (By.XPATH, "//*[self::button or self::a or self::div][contains(., 'Phone') and not(contains(., 'Micro'))]"),
            (By.XPATH, "//button[contains(., 'Enter phone') or contains(., 'Add phone')]"),
            (By.CSS_SELECTOR, "[data-test='phone-tab'], [data-test='open-phone']"),
            (By.XPATH, "//button[contains(., 'Continue') or contains(., 'Next')]"),
        ]
        for loc in triggers:
            els = self.driver.find_elements(*loc)
            if not els:
                continue
            try:
                el = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(loc))
                self._scroll_into_view(el); el.click(); return self
            except Exception:
                try:
                    self._try_js_click(els[0]); return self
                except Exception:
                    continue
        return self

    def enter_phone_and_confirm(self, phone: str, code_provider):
        """
        1) type phone
        2) click 'Send code'
        3) call retrieve_phone_code(self.driver)
        4) type code
        5) confirm
        """
        from helpers import retrieve_phone_code  # optional, you already pass the provider
        self._maybe_click(self.COOKIE_ACCEPT, timeout=2)
        self.ensure_phone_section_visible()

        # tolerant locators
        phone_locs = [
            (By.CSS_SELECTOR, "input[name='phone']"),
            (By.CSS_SELECTOR, "input[type='tel']"),
            (By.XPATH, "//input[@inputmode='tel' or @inputmode='numeric']"),
            (By.XPATH, "//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'phone')]"),
        ]
        send_code_locs = [
            self.SEND_CODE_BTN,
            (By.XPATH, "//button[contains(., 'Send code') or contains(., 'Send Code') or contains(., 'SMS') "
                       "or contains(., 'Next') or contains(., 'Continue')]"),
        ]
        code_locs = [
            self.CODE_INPUT,
            (By.CSS_SELECTOR, "input[name='code']"),
            (By.XPATH, "//input[@maxlength='4' or @maxlength='6' or @name='code']"),
        ]
        confirm_locs = [
            self.CONFIRM_PHONE_BTN,
            (By.XPATH, "//button[contains(., 'Confirm') or contains(., 'Verify') or contains(., 'Continue') or contains(., 'OK')]"),
        ]

        def _first_clickable(cands, to=12):
            for loc in cands:
                try:
                    return WebDriverWait(self.driver, to).until(EC.element_to_be_clickable(loc))
                except TimeoutException:
                    continue
            raise TimeoutException(f"No clickable control among: {cands}")

        # type phone (handle mask)
        p = _first_clickable(phone_locs)
        try: p.clear()
        except Exception: pass
        p.send_keys(Keys.CONTROL, "a"); p.send_keys(Keys.DELETE); p.send_keys(phone)

        # click 'Send code'
        try:
            btn = _first_clickable(send_code_locs, to=8)
            self._scroll_into_view(btn)
            try: btn.click()
            except ElementClickInterceptedException: self._try_js_click(btn)
        except TimeoutException:
            # Some UIs auto-send after typing phone; proceed
            pass

        # retrieve SMS code from performance log (helpers.py expects driver)
        code = str(code_provider(self.driver)).strip()

        # type code
        c = _first_clickable(code_locs, to=15)
        try: c.clear()
        except Exception: pass
        c.send_keys(code)

        # confirm
        try:
            confirm = _first_clickable(confirm_locs, to=6)
            self._scroll_into_view(confirm)
            try: confirm.click()
            except ElementClickInterceptedException: self._try_js_click(confirm)
        except TimeoutException:
            c.send_keys(Keys.ENTER)  # fallback

        return self

    # ---------- The rest (as you already had) ----------
    def add_credit_card(self, number: str, expiry: str, cvv: str):
        self.wait.until(EC.element_to_be_clickable(self.ADD_CARD_BTN)).click()
        switched = False
        try:
            frame = self.wait.until(EC.presence_of_element_located(self.CARD_IFRAME))
            self.driver.switch_to.frame(frame); switched = True
        except TimeoutException:
            pass
        self.wait.until(EC.element_to_be_clickable(self.CARD_NUMBER)).send_keys(number)
        self.driver.find_element(*self.CARD_EXPIRY).send_keys(expiry)
        cvv_el = self.driver.find_element(*self.CARD_CVV)
        cvv_el.send_keys(cvv); cvv_el.send_keys(Keys.TAB)
        if switched:
            self.driver.switch_to.default_content()
        self.wait.until(EC.element_to_be_clickable(self.LINK_CARD_BTN)).click()
        self.wait.until(EC.visibility_of_element_located(self.CARD_LINKED_BADGE))
        return self

    def write_comment_for_driver(self, text: str):
        area = self.wait.until(EC.element_to_be_clickable(self.COMMENT_TEXTAREA))
        area.clear(); area.send_keys(text)
        return self

    def toggle_blanket_and_verify(self):
        self.wait.until(EC.element_to_be_clickable(self.BLANKET_TOGGLE)).click()
        self.wait.until(EC.visibility_of_element_located(self.BLANKET_STATE_ASSERT))
        return self

    def order_ice_creams(self, qty: int):
        for _ in range(qty):
            self.wait.until(EC.element_to_be_clickable(self.ICECREAM_PLUS)).click()
        self.wait.until(lambda d: int(d.find_element(*self.ICECREAM_QTY).text) >= qty)
        return self

    def place_supportive_order(self, driver_message: str):
        if self.driver.find_elements(*self.DRIVER_MESSAGE_INPUT):
            area = self.driver.find_element(*self.DRIVER_MESSAGE_INPUT)
            area.clear(); area.send_keys(driver_message)
        self.wait.until(EC.element_to_be_clickable(self.ORDER_BTN)).click()
        self.wait.until(EC.visibility_of_element_located(self.SEARCH_MODAL))
        return self
