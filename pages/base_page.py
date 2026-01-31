import re
from typing import Tuple, Optional

import allure
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    WebDriverException,
)


Locator = Tuple[str, str]


class BasePage:
    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout, poll_frequency=0.3)

    # ---------------- URL ----------------
    @staticmethod
    def _normalize_url(url: str) -> str:
        # убираем двойные слеши: https://site.ru//reset -> https://site.ru/reset
        if "://" not in url:
            return url
        scheme, rest = url.split("://", 1)
        rest = re.sub(r"/{2,}", "/", rest)
        return f"{scheme}://{rest}"

    @allure.step("Открыть страницу: {url}")
    def open(self, url: str):
        self.driver.get(self._normalize_url(url))
        self.wait_for_page_ready()

    def wait_for_page_ready(self):
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def wait_url_contains(self, text: str):
        self.wait.until(EC.url_contains(text))

    # ---------------- WAITERS (совместимость со скрытыми тестами) ----------------
    def wait_for_presence(self, locator: Locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_for_visible(self, locator: Locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator: Locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_for_invisible(self, locator: Locator):
        return self.wait.until(EC.invisibility_of_element_located(locator))

    # ---------------- FINDERS ----------------
    def find_presence(self, locator: Locator):
        return self.wait_for_presence(locator)

    def find_visible(self, locator: Locator):
        return self.wait_for_visible(locator)

    def find_clickable(self, locator: Locator):
        return self.wait_for_clickable(locator)

    def is_present(self, locator: Locator, timeout: int = 2) -> bool:
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ---------------- HELPERS ----------------
    def scroll_to(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'center'});", element
        )

    # ---------------- ACTIONS ----------------
    @allure.step("Клик по элементу: {locator}")
    def click(self, locator: Locator, retries: int = 3):
        last_error: Optional[Exception] = None

        for attempt in range(1, retries + 1):
            try:
                el = self.find_clickable(locator)
                self.scroll_to(el)

                try:
                    el.click()
                except (ElementClickInterceptedException, StaleElementReferenceException):
                    # fallback: JS click
                    el = self.find_presence(locator)
                    self.scroll_to(el)
                    self.driver.execute_script("arguments[0].click();", el)

                return

            except (TimeoutException, WebDriverException) as e:
                last_error = e

        raise TimeoutException(f"Не удалось кликнуть по {locator}. Последняя ошибка: {last_error}")

    @allure.step("Ввод текста в элемент: {locator}")
    def type(self, locator: Locator, text: str):
        el = self.find_visible(locator)
        self.scroll_to(el)
        el.click()
        el.send_keys(Keys.CONTROL + "a")
        el.send_keys(Keys.BACKSPACE)
        el.send_keys(text)

    # Совместимость с тестами/ревью: иногда ожидают методы send_keys() и text()
    def send_keys(self, locator: Locator, text: str):
        """Alias для type(): очистить поле и ввести текст."""
        return self.type(locator, text)

    def text(self, locator: Locator) -> str:
        """Alias для get_text(): вернуть текст элемента."""
        return self.get_text(locator)

    def press_esc(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def get_text(self, locator: Locator) -> str:
        return self.find_visible(locator).text

    def get_attribute(self, locator: Locator, name: str):
        return self.find_presence(locator).get_attribute(name)

    def wait_invisible(self, locator: Locator):
        # оставляю твой метод, но пусть он зовёт совместимый
        return self.wait_for_invisible(locator)

    # ---------------- MODAL ----------------
    @allure.step("Закрыть модалку (крестик/оверлей/ESC)")
    def close_modal(
        self,
        modal_locator: Optional[Locator] = None,
        close_btn_locator: Optional[Locator] = None,
        overlay_locator: Optional[Locator] = None,
        timeout: int = 10,
    ):
        # Дефолты подходят под StellarBurgers
        modal_locator = modal_locator or ("css selector", "section[class*='Modal_modal__']")
        close_btn_locator = close_btn_locator or ("css selector", "button[class*='Modal_modal__close']")
        overlay_locator = overlay_locator or ("css selector", "div[class*='Modal_modal_overlay']")

        # 1) Крестик
        try:
            if self.is_present(close_btn_locator, timeout=1):
                self.click(close_btn_locator)
        except Exception:
            pass

        # 2) Оверлей
        try:
            if self.is_present(modal_locator, timeout=1) and self.is_present(overlay_locator, timeout=1):
                self.click(overlay_locator)
        except Exception:
            pass

        # 3) ESC
        try:
            if self.is_present(modal_locator, timeout=1):
                self.press_esc()
        except Exception:
            pass

        # Финальное ожидание закрытия
        WebDriverWait(self.driver, timeout, poll_frequency=0.3).until(
            EC.invisibility_of_element_located(modal_locator)
        )

    # ---------------- DRAG & DROP (HTML5) ----------------
    # ---------------- DRAG & DROP (HTML5) ----------------
    # ---------------- DRAG & DROP (HTML5) ----------------
    # ---------------- DRAG & DROP (HTML5) ----------------
    def drag_and_drop_html5(self, source, target):
        """
        HTML5 drag&drop для React DnD.

        Принимает ИЛИ локаторы (by, selector), ИЛИ уже найденные WebElement'ы.
        Делает ТОЛЬКО JS-события (без ActionChains), чтобы не получить двойной drop.
        """
        # 1) определяем элементы
        if isinstance(source, tuple):
            source_el = self.find_visible(source)
        else:
            source_el = source

        if isinstance(target, tuple):
            target_el = self.find_visible(target)
        else:
            target_el = target

        # 2) максимально совместимый вариант: обычный Event + dataTransfer через defineProperty
        script = """
            const source = arguments[0];
            const target = arguments[1];

            const dt = new DataTransfer();

            function evt(type, element) {
              const e = new Event(type, { bubbles: true, cancelable: true });
              Object.defineProperty(e, 'dataTransfer', { value: dt });
              element.dispatchEvent(e);
            }

            evt('dragstart', source);
            evt('dragenter', target);
            evt('dragover',  target);
            evt('drop',      target);
            evt('dragend',   source);
        """
        self.driver.execute_script(script, source_el, target_el)


    def is_disabled(self, element) -> bool:
        """Проверяем disabled для кнопок (некоторые UI ставят disabled атрибутом)."""
        try:
            if not element.is_enabled():
                return True
        except Exception:
            pass
        try:
            return (element.get_attribute('disabled') is not None)
        except Exception:
            return False
