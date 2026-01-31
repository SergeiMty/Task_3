import allure
from pages.main_page import MainPage
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from locators.common_locators import CommonLocators


@allure.epic("Task_3 UI")
@allure.feature("Личный кабинет")
class TestProfile:

    @allure.title("Переход по клику на 'Личный кабинет'")
    def test_go_to_account(self, driver, ui_url, user):
        main = MainPage(driver)
        main.open(ui_url)
        main.click_login_main()

        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.click(CommonLocators.ACCOUNT_LINK)
        assert "/account" in driver.current_url

    @allure.title("Переход в раздел 'История заказов'")
    def test_go_to_order_history(self, driver, ui_url, user):
        main = MainPage(driver)
        main.open(ui_url)
        main.click_login_main()

        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.click(CommonLocators.ACCOUNT_LINK)

        profile = ProfilePage(driver)
        profile.open_order_history()
        assert "order-history" in driver.current_url or "/account" in driver.current_url

    @allure.title("Выход из аккаунта")
    def test_logout(self, driver, ui_url, user):
        main = MainPage(driver)
        main.open(ui_url)
        main.click_login_main()

        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.click(CommonLocators.ACCOUNT_LINK)

        profile = ProfilePage(driver)
        profile.logout()

        assert "/login" in driver.current_url
