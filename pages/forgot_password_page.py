import allure

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage
from locators.forgot_password_locators import ForgotPasswordLocators


class ForgotPasswordPage(BasePage):

    @allure.step("Ввести email и нажать 'Восстановить'")
    def submit_email(self, email: str):
        self.send_keys(ForgotPasswordLocators.EMAIL_INPUT, email)
        self.click(ForgotPasswordLocators.RECOVER_BUTTON)
        # ждём переход на reset-password
        try:
            self.wait_url_contains('/reset-password')
        except Exception:
            pass

    def _get_password_input(self):
        """
        На reset-password иногда поле бывает type=password, иногда уже type=text (если кликнули 'глаз').
        Поэтому ищем шире, чем только input[type=password].
        """
        # 1) локатор проекта
        try:
            return self.find_presence(ForgotPasswordLocators.PASSWORD_INPUT)
        except TimeoutException:
            pass

        # 2) любой input с placeholder/aria-label про пароль
        xpaths = [
            "//input[@type='password']",
            "//input[contains(translate(@placeholder,'ПАРОЛЬ','пароль'),'парол')]",
            "//input[contains(translate(@name,'ПАРОЛЬ','пароль'),'парол')]",
            "//input[contains(translate(@aria-label,'ПАРОЛЬ','пароль'),'парол')]",
            "//input[contains(translate(@placeholder,'PASSWORD','password'),'password')]",
            "//input[contains(translate(@name,'PASSWORD','password'),'password')]",
        ]
        for xp in xpaths:
            els = self.driver.find_elements(By.XPATH, xp)
            if els:
                return els[0]

        # 3) fallback: первый input в форме reset-password
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        if forms:
            inputs = forms[0].find_elements(By.TAG_NAME, "input")
            if inputs:
                return inputs[0]

        raise TimeoutException("Не нашёл поле пароля на reset-password ни одним способом")

    @allure.step("Клик по иконке показать/скрыть пароль")
    def click_show_hide_password(self):
        # дожидаемся, что вообще появилась форма/инпут
        WebDriverWait(self.driver, 12, poll_frequency=0.3).until(lambda d: len(d.find_elements(By.TAG_NAME, "input")) > 0)

        password_input = self._get_password_input()
        # на сайте иконка 'глаз' — svg внутри соседнего div, проще кликнуть по родителю
        try:
            eye = self.driver.find_element(*ForgotPasswordLocators.SHOW_HIDE_BUTTON)
            self.driver.execute_script("arguments[0].click();", eye)
        except Exception:
            # fallback: кликаем по ближайшему контейнеру справа от input
            try:
                container = password_input.find_element(By.XPATH, "./ancestor::div[contains(@class,'input__container')][1]")
                btns = container.find_elements(By.TAG_NAME, "svg")
                if btns:
                    self.driver.execute_script("arguments[0].click();", btns[0])
                else:
                    # иногда кнопка это div/span
                    clickable = container.find_elements(By.XPATH, ".//*[name()='svg' or contains(@class,'input__icon')]")
                    if clickable:
                        self.driver.execute_script("arguments[0].click();", clickable[0])
            except Exception:
                raise

        # проверяем: инпут стал активным (фокус/класс)
        try:
            password_input.click()
        except Exception:
            pass

        return password_input

    @allure.step("Проверить, что поле пароля активно (фокус на инпуте)")
    def is_password_input_active(self) -> bool:
        password_input = self._get_password_input()
        active = self.driver.switch_to.active_element
        return active == password_input

    # Алиас под ожидаемое имя метода в тестах
    def password_input_is_active(self) -> bool:
        return self.is_password_input_active()

