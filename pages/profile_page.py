import time
import allure

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from locators.profile_page_locators import ProfilePageLocators
from locators.main_page_locators import MainPageLocators


class ProfilePage(BasePage):
    @allure.step("Открыть историю заказов")
    def open_order_history(self):
        self.click(ProfilePageLocators.ORDER_HISTORY_SECTION)

    @allure.step("Проверить, что заказ с номером есть в истории")
    def order_in_history_exists(self, order_number: str) -> bool:
        end = time.time() + 15
        while time.time() < end:
            if self.driver.find_elements(By.XPATH, f"//*[text()='{order_number}']"):
                return True
            time.sleep(0.5)
        return False

    @allure.step("Выйти из аккаунта")
    def logout(self):
        """
        Тест ожидает profile.logout()
        """
        try:
            self.click(ProfilePageLocators.LOGOUT_BUTTON)
        except Exception:
            self.driver.find_element(By.XPATH, "//button[contains(.,'Выход')]").click()

        # ждём, что вернулись на страницу логина
        try:
            self.wait_url_contains("login")
        except Exception:
            # либо появилась кнопка логина на главной
            self.wait_for_visible(MainPageLocators.LOGIN_MAIN_BUTTON)
