import re
import time
import allure

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage
from locators.common_locators import CommonLocators


class FeedPage(BasePage):

    FEED_ITEMS = (
        By.XPATH,
        "//*[contains(@class,'OrderHistory_link') or contains(@class,'OrderHistory_textBox')]"
    )

    FIRST_ORDER_NUMBER = (
        By.XPATH,
        "(//*[contains(@class,'text_type_digits-default')])[1]"
    )

    ALL_TIME_COUNTER = (
        By.XPATH,
        "//*[contains(text(),'Выполнено за все время')]/following::*[contains(@class,'text_type_digits-large')][1]"
    )

    TODAY_COUNTER = (
        By.XPATH,
        "//*[contains(text(),'Выполнено за сегодня')]/following::*[contains(@class,'text_type_digits-large')][1]"
    )

    def open(self, url: str):
        self.driver.get(url)

    def _parse_int(self, text: str) -> int:
        digits = re.findall(r"\d+", text or "")
        if not digits:
            return 0
        return int("".join(digits))

    @allure.step("Открыть первый заказ в ленте")
    def open_first_order(self, timeout: int = 30):
    # ждём, пока в ленте появятся элементы
        WebDriverWait(self.driver, timeout, poll_frequency=0.3).until(
            lambda d: d.find_elements(*self.FEED_ITEMS)
        )

    # несколько вариантов клика по первому заказу
        click_targets = [
            (By.XPATH, "(//a[contains(@class,'OrderHistory_link')])[1]"),
            (By.XPATH, "(//*[contains(@class,'OrderHistory_textBox')])[1]"),
            (By.XPATH, "(//*[contains(@class,'text_type_digits-default')])[1]"),
        ]

        last_err = None

        for _ in range(5):
            for locator in click_targets:
                try:
                    element = WebDriverWait(self.driver, 10, poll_frequency=0.3).until(
                        EC.presence_of_element_located(locator)
                    )

                    try:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});", element
                        )
                    except Exception:
                        pass

                    try:
                        element.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", element)

                    # ждём не только общий MODAL, а любой признак открывшегося окна
                    WebDriverWait(self.driver, 12, poll_frequency=0.3).until(
                        lambda d: (
                            d.find_elements(*CommonLocators.MODAL)
                            or d.find_elements(*CommonLocators.MODAL_CLOSE_BUTTON)
                            or d.find_elements(By.XPATH, "//*[contains(text(),'Состав')]")
                            or d.find_elements(By.XPATH, "//*[contains(text(),'Детали заказа')]")
                        )
                    )
                    return

                except Exception as e:
                    last_err = e
                    continue

            # если с первого раза не сработало — обновляем страницу и пробуем ещё
            try:
                self.driver.refresh()
                WebDriverWait(self.driver, 20, poll_frequency=0.3).until(
                    lambda d: d.find_elements(*self.FEED_ITEMS)
                )
            except Exception:
                pass

            time.sleep(0.8)

        raise TimeoutException(f"Не удалось открыть первый заказ в ленте: {last_err}")

    @allure.step("Получить счётчик 'Выполнено за все время'")
    def get_total_all_time(self) -> int:
        el = WebDriverWait(self.driver, 15, poll_frequency=0.3).until(
            EC.visibility_of_element_located(self.ALL_TIME_COUNTER)
        )
        return self._parse_int(el.text)

    @allure.step("Получить счётчик 'Выполнено за сегодня'")
    def get_total_today(self) -> int:
        el = WebDriverWait(self.driver, 15, poll_frequency=0.3).until(
            EC.visibility_of_element_located(self.TODAY_COUNTER)
        )
        return self._parse_int(el.text)

    @allure.step("Дождаться увеличения счётчиков ленты")
    def wait_counters_increase(self, before_all: int, before_today: int, timeout: int = 180):
        end_time = time.time() + timeout
        last_all = before_all
        last_today = before_today

        while time.time() < end_time:
            try:
                self.driver.refresh()

                WebDriverWait(self.driver, 20, poll_frequency=0.3).until(
                    EC.visibility_of_element_located(self.ALL_TIME_COUNTER)
                )
                WebDriverWait(self.driver, 20, poll_frequency=0.3).until(
                    EC.visibility_of_element_located(self.TODAY_COUNTER)
                )

                last_all = self.get_total_all_time()
                last_today = self.get_total_today()

                if last_all >= before_all + 1 and last_today >= before_today + 1:
                    return last_all, last_today

            except Exception:
                pass

            time.sleep(2)

        raise TimeoutException(
            f"Счётчики не увеличились. Было: all={before_all}, today={before_today}. "
            f"Стало: all={last_all}, today={last_today}"
        )
    @allure.step("Дождаться появления номера заказа в блоке 'В работе'")
    def wait_order_in_progress(self, order_number: str, timeout: int = 180):
        order_number = str(order_number).strip()

        xpath = (
            f"//*[contains(text(),'В работе')]"
            f"/following::*[contains(text(), '{order_number}')]"
        )

        WebDriverWait(self.driver, timeout, poll_frequency=1).until(
            lambda d: d.find_elements(By.XPATH, xpath)
        )