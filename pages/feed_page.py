import time
import re
import allure

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from pages.base_page import BasePage
from locators.feed_page_locators import FeedPageLocators
from locators.common_locators import CommonLocators


class FeedPage(BasePage):


    def _find_first_order_element(self, timeout: int = 12):
        """Находим кликабельный заказ в ленте.

        Важно: кликабельный элемент обычно <a> с href вида /feed/<номер>.
        """
        # ждём, что список заказов вообще отрисовался
        self.wait_for_visible(FeedPageLocators.IN_WORK_SECTION, timeout=timeout)

        def pick_first_order(d):
            links = d.find_elements(By.CSS_SELECTOR, "a[href*='/feed/']")
            for a in links:
                href = a.get_attribute("href") or ""
                # отсекаем ссылку на сам /feed
                if re.search(r"/feed/\d+", href):
                    return a
            # fallback: если вдруг href прячут, пробуем старый локатор
            els = d.find_elements(*FeedPageLocators.FIRST_ORDER)
            return els[0] if els else False

        return WebDriverWait(self.driver, timeout, poll_frequency=0.25).until(pick_first_order)

    @allure.step("Открыть первый заказ в ленте (клик -> модалка)")
    def open_first_order(self):
        for attempt in range(1, 6):
            try:
                el = self._find_first_order_element(timeout=15)
                self.scroll_to(el)

                # 1) клик по элементу
                try:
                    el.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", el)

                # 2) ждём модалку
                try:
                    self.wait_for_visible(CommonLocators.MODAL, timeout=7)
                    return
                except TimeoutException:
                    # fallback: если клик не открыл модалку — попробуем открыть заказ напрямую по href
                    href = ""
                    try:
                        href = el.get_attribute("href") or ""
                    except Exception:
                        pass

                    if re.search(r"/feed/\d+", href):
                        self.driver.get(href)
                        self.wait_for_visible(CommonLocators.MODAL, timeout=7)
                        return
                    raise

            except (TimeoutException, StaleElementReferenceException):
                # иногда нужно дать странице дорендериться
                time.sleep(0.5)
                continue

        raise TimeoutException("Не удалось открыть первый заказ в ленте: модалка не появилась")
    @allure.step("Получить счётчик 'выполнено за всё время'")
    def total_all_time(self) -> int:
        self.wait_for_visible(FeedPageLocators.TOTAL_ALL_TIME)
        txt = self.text(FeedPageLocators.TOTAL_ALL_TIME).strip()
        return int(txt) if txt.isdigit() else 0

    @allure.step("Получить счётчик 'выполнено за сегодня'")
    def total_today(self) -> int:
        self.wait_for_visible(FeedPageLocators.TOTAL_TODAY)
        txt = self.text(FeedPageLocators.TOTAL_TODAY).strip()
        return int(txt) if txt.isdigit() else 0
