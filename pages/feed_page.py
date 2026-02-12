import re
import time
import allure

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from pages.base_page import BasePage
from locators.feed_page_locators import FeedPageLocators


class FeedPage(BasePage):
    """
    /feed — Лента заказов.

    Фиксы:
    1) Открытие модалки заказа: URL может быть /feed/<digits> ИЛИ /feed/<hex>
    2) Счетчики "за все время" и "за сегодня" обновляются с задержкой -> ждём рост + refresh при необходимости
    """

    # Реальные селекторы модалки на StellarBurgers (не через CommonLocators)
    MODAL = (By.CSS_SELECTOR, "section[class*='Modal_modal__'], div[class*='Modal_modal__']")
    MODAL_CLOSE_BTN = (By.CSS_SELECTOR, "button[class*='Modal_modal__close']")

    # Самый стабильный клик в ленте — по <a href="/feed/<id>">
    ORDER_LINK = (By.XPATH, "//a[contains(@href,'/feed/') and not(contains(@href,'undefined'))]")

    def __init__(self, driver, timeout: int = 15):
        super().__init__(driver, timeout)
        self._all_time_baseline: int | None = None
        self._today_baseline: int | None = None
        self._refreshes_used: int = 0

    # ---------------- helpers ----------------
    def _url_has_order_id(self, url: str) -> bool:
        # /feed/12345 или /feed/698d5e04984270001be4a2da (hex/ObjectId)
        return re.search(r"/feed/(?:\d+|[0-9a-f]{10,})", url) is not None

    def _digits(self, text: str) -> int:
        text = text or ""
        d = re.sub(r"\D+", "", text)
        return int(d) if d else 0

    def _visible(self, locator, timeout: int = 15):
        return WebDriverWait(self.driver, timeout, poll_frequency=0.3).until(
            EC.visibility_of_element_located(locator)
        )

    def _any_present(self, locator, timeout: int = 15):
        return WebDriverWait(self.driver, timeout, poll_frequency=0.3).until(
            lambda d: len(d.find_elements(*locator)) > 0
        )

    def _click_force(self, el):
        try:
            self.scroll_to(el)
        except Exception:
            pass

        try:
            el.click()
            return
        except Exception:
            pass

        try:
            self.driver.execute_script("arguments[0].click();", el)
            return
        except Exception:
            pass

        ActionChains(self.driver).move_to_element(el).click().perform()

    def _find_first_order_link(self, timeout: int = 25):
        # Подождём, что лента отрисовалась (если локатор существует)
        if hasattr(FeedPageLocators, "IN_WORK_SECTION"):
            try:
                self.wait_for_visible(FeedPageLocators.IN_WORK_SECTION, timeout=timeout)
            except Exception:
                pass

        self._any_present(self.ORDER_LINK, timeout=timeout)
        els = self.driver.find_elements(*self.ORDER_LINK)
        els = [e for e in els if e.is_displayed()]
        if not els:
            raise TimeoutException("Не нашёл кликабельную ссылку заказа в ленте (/feed)")
        return els[0]

    def _wait_modal_open(self, timeout: int = 15):
        def opened(d):
            try:
                if d.find_elements(*self.MODAL_CLOSE_BTN):
                    return True
            except Exception:
                pass
            try:
                if d.find_elements(*self.MODAL):
                    return True
            except Exception:
                pass
            return False

        WebDriverWait(self.driver, timeout, poll_frequency=0.3).until(opened)
        return self._visible(self.MODAL, timeout=timeout)

    # ---------------- public ----------------
    @allure.step("Открыть первый заказ в ленте и дождаться модалки")
    def open_first_order(self):
        el = self._find_first_order_link(timeout=25)

        for attempt in range(1, 4):
            with allure.step(f"Клик по заказу: попытка {attempt}"):
                try:
                    self._click_force(el)
                except StaleElementReferenceException:
                    el = self._find_first_order_link(timeout=10)
                    continue
                except Exception:
                    el = self._find_first_order_link(timeout=10)

                # ждём: либо URL стал /feed/<id>, либо модалка появилась
                try:
                    WebDriverWait(self.driver, 10, poll_frequency=0.3).until(
                        lambda d: self._url_has_order_id(d.current_url)
                        or d.find_elements(*self.MODAL)
                        or d.find_elements(*self.MODAL_CLOSE_BTN)
                    )
                except Exception:
                    pass

                # финально ждём модалку видимой
                try:
                    self._wait_modal_open(timeout=15)
                    return
                except Exception:
                    el = self._find_first_order_link(timeout=10)

        raise TimeoutException("После клика по заказу модалка не открылась (или не была обнаружена)")

    # ---------------- counters ----------------
    def _read_counter(self, locator, timeout: int = 20) -> int:
        el = self.wait_for_visible(locator, timeout=timeout)
        return self._digits(el.text)

    def _wait_counter_increase(self, locator, baseline: int, timeout: int = 120) -> int:
        """
        Ждём, что значение станет >= baseline + 1.
        Если залипло — делаем refresh до 2 раз.
        """
        target = baseline + 1
        best = baseline
        end = time.time() + timeout

        # моменты, когда разрешаем refresh
        refresh_points = [0.35, 0.70]  # 35% времени и 70% времени
        next_refresh_idx = 0

        while time.time() < end:
            try:
                cur = self._read_counter(locator, timeout=10)
                best = max(best, cur)
                if best >= target:
                    return best
            except Exception:
                pass

            # refresh-пинок (если вебсокет “мёртвый”)
            progress = 1 - (end - time.time()) / timeout
            if next_refresh_idx < len(refresh_points) and progress >= refresh_points[next_refresh_idx]:
                if self._refreshes_used < 2:
                    self._refreshes_used += 1
                    try:
                        self.driver.refresh()
                        self.wait_for_page_ready(timeout=30)
                    except Exception:
                        pass
                next_refresh_idx += 1

            time.sleep(0.5)

        return best

    @allure.step("Счётчик 'Выполнено за все время'")
    def total_all_time(self) -> int:
        cur = self._read_counter(FeedPageLocators.TOTAL_ALL_TIME, timeout=20)
        if self._all_time_baseline is None:
            self._all_time_baseline = cur
            return cur

        after = self._wait_counter_increase(FeedPageLocators.TOTAL_ALL_TIME, self._all_time_baseline, timeout=120)
        self._all_time_baseline = max(self._all_time_baseline, after)
        return after

    @allure.step("Счётчик 'Выполнено за сегодня'")
    def total_today(self) -> int:
        cur = self._read_counter(FeedPageLocators.TOTAL_TODAY, timeout=20)
        if self._today_baseline is None:
            self._today_baseline = cur
            return cur

        after = self._wait_counter_increase(FeedPageLocators.TOTAL_TODAY, self._today_baseline, timeout=120)
        self._today_baseline = max(self._today_baseline, after)
        return after
