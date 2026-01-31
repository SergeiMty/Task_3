import allure
from pages.main_page import MainPage
from pages.login_page import LoginPage
from locators.common_locators import CommonLocators


@allure.epic("Task_3 UI")
@allure.feature("Основной функционал")
class TestConstructor:

    @allure.title("Переход по клику на 'Конструктор'")
    def test_go_to_constructor(self, driver, ui_url):
        main = MainPage(driver)
        main.open(f"{ui_url}/feed")
        main.click(CommonLocators.CONSTRUCTOR_LINK)
        assert ui_url.rstrip("/") == driver.current_url.rstrip("/")

    @allure.title("Переход по клику на 'Лента заказов'")
    def test_go_to_feed(self, driver, ui_url):
        main = MainPage(driver)
        main.open(ui_url)
        main.click(CommonLocators.FEED_LINK)
        assert "/feed" in driver.current_url

    @allure.title("Клик по ингредиенту открывает модалку с деталями")
    def test_open_ingredient_modal(self, driver, ui_url):
        main = MainPage(driver)
        main.open(ui_url)
        main.open_first_ingredient_details()
        main.wait_for_visible(CommonLocators.MODAL)
        assert main.driver.find_element(*CommonLocators.MODAL).is_displayed()

    @allure.title("Модалка ингредиента закрывается по крестику")
    def test_close_ingredient_modal(self, driver, ui_url):
        main = MainPage(driver)
        main.open(ui_url)
        main.open_first_ingredient_details()
        main.wait_for_visible(CommonLocators.MODAL)
        main.close_modal()
        main.wait_for_invisible(CommonLocators.MODAL)
        assert True

    @allure.title("При добавлении ингредиента увеличивается счетчик")
    def test_ingredient_counter_increases(self, driver, ui_url):
        main = MainPage(driver)
        main.open(ui_url)

        before = main.get_first_ingredient_counter()
        main.add_first_ingredient()
        after = main.get_first_ingredient_counter()

        assert after == before + 1

    @allure.title("Залогиненный пользователь может оформить заказ")
    def test_authorized_user_can_place_order(self, driver, ui_url, user):
        main = MainPage(driver)
        main.open(ui_url)

        main.click_login_main()
        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.add_first_ingredient()
        main.place_order()

        main.wait_for_visible(CommonLocators.MODAL)
        number = main.get_order_number()
        assert number.isdigit()
