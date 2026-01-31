import allure
from pages.login_page import LoginPage
from pages.forgot_password_page import ForgotPasswordPage


@allure.epic("Task_3 UI")
@allure.feature("Восстановление пароля")
class TestPasswordRecovery:

    @allure.title("Переход на страницу восстановления пароля по кнопке 'Восстановить пароль'")
    def test_go_to_forgot_password_page(self, driver, ui_url):
        login = LoginPage(driver)
        login.open(f"{ui_url}/login")
        login.go_to_forgot_password()
        assert "/forgot-password" in driver.current_url

    @allure.title("Ввод почты и клик 'Восстановить'")
    def test_restore_by_email(self, driver, ui_url):
        login = LoginPage(driver)
        login.open(f"{ui_url}/forgot-password")

        forgot = ForgotPasswordPage(driver)
        forgot.submit_email("test@mail.ru")

        assert "/reset-password" in driver.current_url

    @allure.title("Кнопка показать/скрыть пароль делает поле активным")
    def test_password_field_becomes_active(self, driver, ui_url):
        forgot = ForgotPasswordPage(driver)
        forgot.open(f"{ui_url}/reset-password")

        forgot.click_show_hide_password()
        assert forgot.password_input_is_active() is True
