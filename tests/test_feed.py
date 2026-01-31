import allure
from pages.main_page import MainPage
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.feed_page import FeedPage
from locators.common_locators import CommonLocators


@allure.epic("Task_3 UI")
@allure.feature("Лента заказов")
class TestFeed:

    @allure.title("Клик по заказу в ленте открывает модалку с деталями")
    def test_open_order_modal_in_feed(self, driver, ui_url):
        feed = FeedPage(driver)
        feed.open(f"{ui_url}/feed")

        feed.open_first_order()
        feed.wait_for_visible(CommonLocators.MODAL)
        assert feed.driver.find_element(*CommonLocators.MODAL).is_displayed()

    @allure.title("Заказ пользователя из истории отображается в ленте")
    def test_user_order_visible_in_feed(self, driver, ui_url, user):
        main = MainPage(driver)
        main.open(ui_url)

        main.click_login_main()
        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.add_first_ingredient()
        main.place_order()
        main.wait_for_visible(CommonLocators.MODAL)
        order_number = main.get_order_number()
        main.close_modal()

        main.click(CommonLocators.ACCOUNT_LINK)
        profile = ProfilePage(driver)
        profile.open_order_history()

        assert profile.order_in_history_exists(order_number) is True

        main.click(CommonLocators.FEED_LINK)
        assert "/feed" in driver.current_url

        assert order_number in driver.page_source

    @allure.title("При создании заказа увеличиваются счетчики 'за все время' и 'за сегодня'")
    def test_counters_increase_after_order(self, driver, ui_url, user):
        feed = FeedPage(driver)
        feed.open(f"{ui_url}/feed")

        all_before = feed.total_all_time()
        today_before = feed.total_today()

        main = MainPage(driver)
        main.open(ui_url)
        main.click_login_main()

        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.add_first_ingredient()
        main.place_order()
        main.wait_for_visible(CommonLocators.MODAL)
        main.close_modal()

        feed.open(f"{ui_url}/feed")
        all_after = feed.total_all_time()
        today_after = feed.total_today()

        assert all_after >= all_before + 1
        assert today_after >= today_before + 1
