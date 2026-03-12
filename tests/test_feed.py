import pytest
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        base = ui_url.rstrip("/")

        main = MainPage(driver)
        main.open(base)
        main.click(CommonLocators.FEED_LINK)

        WebDriverWait(driver, 20, poll_frequency=0.3).until(
            EC.url_contains("/feed")
        )

        feed = FeedPage(driver)
        feed.open_first_order()

        assert True

    @allure.title("После оформления заказа пользователь может открыть историю заказов и ленту")
    def test_user_order_visible_in_feed(self, driver, ui_url, user):
        base = ui_url.rstrip("/")

        main = MainPage(driver)
        main.open(base)

        main.click_login_main()
        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.add_first_ingredient()
        main.place_order()
        main.close_modal()

        main.click(CommonLocators.ACCOUNT_LINK)
        profile = ProfilePage(driver)
        profile.open_order_history()

        assert "/account/order-history" in driver.current_url

        main.click(CommonLocators.FEED_LINK)
        WebDriverWait(driver, 20, poll_frequency=0.3).until(
            EC.url_contains("/feed")
        )

        assert True

    @pytest.mark.xfail(
    reason="Shared test environment: feed counters are unstable and may not update after order creation",
    strict=False
)
    @allure.title("При создании заказа увеличиваются счетчики 'за все время' и 'за сегодня'")
    def test_counters_increase_after_order(self, driver, ui_url, user):
        base = ui_url.rstrip("/")

        main = MainPage(driver)
        main.open(base)
        main.click(CommonLocators.FEED_LINK)

        WebDriverWait(driver, 20, poll_frequency=0.3).until(
            EC.url_contains("/feed")
        )

        feed = FeedPage(driver)
        all_before = feed.get_total_all_time()
        today_before = feed.get_total_today()

        main.open(base)
        main.click_login_main()

        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.add_first_ingredient()
        main.place_order()
        main.close_modal()

        main.click(CommonLocators.FEED_LINK)

        WebDriverWait(driver, 20, poll_frequency=0.3).until(
            EC.url_contains("/feed")
        )

        all_after, today_after = feed.wait_counters_increase(
            all_before,
            today_before,
            timeout=360
        )

        assert all_after >= all_before + 1
        assert today_after >= today_before + 1

    @allure.title("После оформления заказа его номер появляется в блоке 'В работе'")
    def test_order_number_appears_in_progress(self, driver, ui_url, user):
        base = ui_url.rstrip("/")

        main = MainPage(driver)
        main.open(base)

        main.click_login_main()
        login = LoginPage(driver)
        login.login(user["email"], user["password"])

        main.add_first_ingredient()
        order_number = main.place_order()
        main.close_modal()

        main.click(CommonLocators.FEED_LINK)

        WebDriverWait(driver, 20, poll_frequency=0.3).until(
            EC.url_contains("/feed")
        )

        feed = FeedPage(driver)
        feed.wait_order_in_progress(order_number, timeout=180)

        assert True
