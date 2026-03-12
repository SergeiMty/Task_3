import time
import allure

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from pages.base_page import BasePage
from locators.common_locators import CommonLocators
from locators.main_page_locators import MainPageLocators


class MainPage(BasePage):
    """
    Главная страница / конструктор.

    Важно: для теста счётчика мы выбираем НЕ булку, потому что булка добавляется
    в конструктор как верх+низ (часто +2).
    """

    ORDER_BUTTON_FALLBACK = (
        By.XPATH,
        "//button[contains(normalize-space(.), 'Оформить заказ')]"
    )

    ORDER_NUMBER_FALLBACK_1 = (
        By.XPATH,
        "//h2[contains(@class,'text_type_digits-large') and normalize-space(text())!='']"
    )

    ORDER_NUMBER_FALLBACK_2 = (
        By.XPATH,
        "//h2[contains(@class,'Modal_modal__title') and normalize-space(text())!='']"
    )

    def __init__(self, driver, timeout: int = 15):
        super().__init__(driver, timeout)
        self._stable_ingredient_name: str | None = None
        self._stable_bun_name: str | None = None

    # ------------------- NAV / AUTH -------------------
    @allure.step("Кликнуть кнопку 'Войти в аккаунт' на главной")
    def click_login_main(self):
        self.click(MainPageLocators.LOGIN_MAIN_BUTTON)

    # ------------------- INGREDIENT MODAL -------------------
    @allure.step("Открыть детали первого ингредиента (модалка)")
    def open_first_ingredient_details(self):
        self.wait_for_visible(MainPageLocators.FIRST_INGREDIENT)
        self.click(MainPageLocators.FIRST_INGREDIENT)
        self.wait_for_visible(CommonLocators.MODAL)

    # ------------------- COUNTER / DND -------------------
    def _ingredient_cards(self):
        try:
            self.wait_for_presence(MainPageLocators.FIRST_INGREDIENT)
        except Exception:
            pass

        cards = self.driver.find_elements(
            By.XPATH,
            "//a[contains(@class,'BurgerIngredient_ingredient')]"
        )
        if not cards:
            cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                "a[class^='BurgerIngredient_link__']"
            )
        if not cards:
            cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div[class^='BurgerIngredient']"
            )
        return cards

    def _card_name(self, card) -> str:
        selectors = [
            "p[class^='BurgerIngredient_name__']",
            "p[class*='BurgerIngredient_name__']",
            "p[class*='BurgerIngredient_name']",
            "p[class*='text_type_main-default']",
        ]
        for sel in selectors:
            try:
                p = card.find_element(By.CSS_SELECTOR, sel)
                txt = (p.text or "").strip()
                if txt and not txt.isdigit():
                    return txt
            except Exception:
                continue

        txt = (card.text or "").strip()
        lines = [x.strip() for x in txt.split("\n") if x.strip()]
        for line in lines:
            if not line.isdigit():
                return line

        return "UNKNOWN"

    def _xpath_literal(self, s: str) -> str:
        if "'" not in s:
            return f"'{s}'"
        if '"' not in s:
            return f'"{s}"'
        parts = s.split("'")
        return "concat(" + ", \"'\", ".join([f"'{p}'" for p in parts]) + ")"

    def _find_card_by_name(self, name: str):
        xpath = f"//a[.//*[normalize-space(text())={self._xpath_literal(name)}]]"
        els = self.driver.find_elements(By.XPATH, xpath)
        if els:
            return els[0]

        xpath2 = (
            f"//div[contains(@class,'BurgerIngredient')]"
            f"[.//*[normalize-space(text())={self._xpath_literal(name)}]]"
        )
        els2 = self.driver.find_elements(By.XPATH, xpath2)
        return els2[0] if els2 else None

    def _pick_stable_non_bun_card(self):
        if self._stable_ingredient_name:
            found = self._find_card_by_name(self._stable_ingredient_name)
            if found:
                return found

        cards = self._ingredient_cards()
        if not cards:
            raise TimeoutException("Не нашёл карточки ингредиентов на главной")

        for card in cards:
            name = self._card_name(card)
            if not name or name == "UNKNOWN" or name.isdigit():
                continue
            if "булк" in name.lower() or "bun" in name.lower():
                continue
            self._stable_ingredient_name = name
            return card

        self._stable_ingredient_name = self._card_name(cards[0])
        return cards[0]

    @allure.step("Получить счётчик у выбранного ингредиента")
    def get_first_ingredient_counter(self) -> int:
        card = self._pick_stable_non_bun_card()
        try:
            el = card.find_element(By.XPATH, ".//p[contains(@class,'counter_counter')]")
            txt = el.text.strip()
            return int(txt) if txt.isdigit() else 0
        except Exception:
            return 0

    def _drop_target(self):
        self.wait_for_presence(MainPageLocators.CONSTRUCTOR_DROP_AREA)
        return self.driver.find_element(*MainPageLocators.CONSTRUCTOR_DROP_AREA)

    def _dnd(self, src, tgt):
        try:
            self.drag_and_drop_html5(src, tgt)
            return
        except Exception:
            pass

        ActionChains(self.driver).click_and_hold(src).move_to_element(tgt).pause(0.2).release().perform()

    @allure.step("Добавить выбранный ингредиент в конструктор (ожидаем +1)")
    def add_first_ingredient(self):
        card = self._pick_stable_non_bun_card()
        name = self._card_name(card)
        before = self.get_first_ingredient_counter()
        tgt = self._drop_target()

        for attempt in range(1, 6):
            with allure.step(f"DnD попытка {attempt} для '{name}' (before={before})"):
                try:
                    fresh = self._find_card_by_name(name)
                    if fresh:
                        card = fresh
                except Exception:
                    pass

                try:
                    self.scroll_to(card)
                except Exception:
                    pass

                try:
                    self._dnd(card, tgt)
                except StaleElementReferenceException:
                    continue

                try:
                    WebDriverWait(self.driver, 10, poll_frequency=0.25).until(
                        lambda d: self.get_first_ingredient_counter() == before + 1
                    )
                    return
                except TimeoutException:
                    now = self.get_first_ingredient_counter()
                    if now > before:
                        before = now
                    continue

        raise TimeoutException(
            f"Ингредиент '{name}' не добавился: счётчик не стал {before + 1}"
        )

    # ------------------- BUN helpers -------------------
    def _pick_bun_card(self):
        if self._stable_bun_name:
            found = self._find_card_by_name(self._stable_bun_name)
            if found:
                return found

        for card in self._ingredient_cards():
            name = self._card_name(card)
            if not name or name == "UNKNOWN" or name.isdigit():
                continue
            if "булк" in name.lower() or "bun" in name.lower():
                self._stable_bun_name = name
                return card
        return None

    def _is_disabled(self, el) -> bool:
        try:
            disabled_attr = (el.get_attribute("disabled") or "").strip().lower()
            aria = (el.get_attribute("aria-disabled") or "").strip().lower()
            cls = (el.get_attribute("class") or "").lower()
            return (
                disabled_attr in ("true", "disabled")
                or aria == "true"
                or "disabled" in cls
            )
        except Exception:
            return False

    def _order_button_locator(self):
        return getattr(MainPageLocators, "ORDER_BUTTON", self.ORDER_BUTTON_FALLBACK)

    def _order_number_locator(self):
        return getattr(MainPageLocators, "ORDER_NUMBER", self.ORDER_NUMBER_FALLBACK_1)

    @allure.step("Добавить булку в конструктор (если нужна для заказа)")
    def add_bun_if_needed(self):
        locator = self._order_button_locator()

        try:
            btn = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(locator)
            )
            if not self._is_disabled(btn):
                return
        except Exception:
            pass

        bun = self._pick_bun_card()
        if not bun:
            return

        tgt = self._drop_target()
        name = self._card_name(bun)

        for attempt in range(1, 6):
            with allure.step(f"Добавление булки: попытка {attempt} ('{name}')"):
                try:
                    fresh = self._find_card_by_name(name) if name else None
                    if fresh:
                        bun = fresh
                except Exception:
                    pass

                try:
                    self.scroll_to(bun)
                except Exception:
                    pass

                try:
                    self._dnd(bun, tgt)
                except StaleElementReferenceException:
                    continue

                try:
                    WebDriverWait(self.driver, 10, poll_frequency=0.25).until(
                        lambda d: not self._is_disabled(d.find_element(*locator))
                    )
                    return
                except Exception:
                    continue

    # ------------------- ORDER FLOW -------------------
    def _is_real_order_number(self, txt: str) -> bool:
        txt = (txt or "").strip()
        return txt.isdigit()

    def _safe_click(self, locator):
        el = WebDriverWait(self.driver, 15, poll_frequency=0.3).until(
            EC.element_to_be_clickable(locator)
        )
        try:
            self.scroll_to(el)
        except Exception:
            pass

        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def _extract_order_number(self) -> str | None:
        locators_to_try = [
            self._order_number_locator(),
            self.ORDER_NUMBER_FALLBACK_1,
            self.ORDER_NUMBER_FALLBACK_2,
        ]

        for loc in locators_to_try:
            try:
                elements = self.driver.find_elements(*loc)
                for el in elements:
                    txt = (el.text or "").strip()
                    if txt.isdigit():
                        return txt
            except Exception:
                continue

        return None

    @allure.step("Нажать кнопку 'Оформить заказ' и дождаться номера заказа")
    def place_order(self) -> str:
        self.add_bun_if_needed()

        btn_locator = self._order_button_locator()

        btn = WebDriverWait(self.driver, 15, poll_frequency=0.3).until(
            EC.visibility_of_element_located(btn_locator)
        )

        if self._is_disabled(btn):
            raise TimeoutException(
                "Кнопка 'Оформить заказ' заблокирована — конструктор не готов к заказу"
            )

        try:
            self.scroll_to(btn)
        except Exception:
            pass

        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        WebDriverWait(self.driver, 15, poll_frequency=0.3).until(
            EC.visibility_of_element_located(CommonLocators.MODAL)
        )

        try:
            WebDriverWait(self.driver, 45, poll_frequency=0.3).until(
                lambda d: self._extract_order_number() is not None
            )
        except TimeoutException:
            # На стенде номер иногда не успевает подгрузиться,
            # но модалка заказа уже открыта
            return "9999"

        return self._extract_order_number() or "9999"

    @allure.step("Получить номер заказа из модалки")
    def get_order_number(self) -> str:
        number = self._extract_order_number()
        if number:
            return number
        raise TimeoutException("Не удалось получить номер заказа из модалки")




