import allure
from pages.base_page import BasePage
from locators.login_page_locators import LoginPageLocators


class LoginPage(BasePage):

    @allure.step("Открыть страницу логина")
    def open_login(self, url: str):
        self.open(url)

    @allure.step("Авторизация")
    def login(self, email: str, password: str):
        self.type(LoginPageLocators.EMAIL_INPUT, email)
        self.type(LoginPageLocators.PASSWORD_INPUT, password)
        self.click(LoginPageLocators.LOGIN_BUTTON)

        # Ждём редирект (после логина обычно уходим с /login)
        try:
            self.wait.until(lambda d: '/login' not in d.current_url)
        except Exception:
            pass

    @allure.step("Перейти в восстановление пароля")
    def go_to_forgot_password(self):
        self.click(LoginPageLocators.FORGOT_PASSWORD_LINK)
