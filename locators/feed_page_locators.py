from selenium.webdriver.common.by import By


class FeedPageLocators:
    # Секция со списком заказов (лента)
    IN_WORK_SECTION = (By.XPATH, "//ul[contains(@class,'OrderFeed_orderList')]")

    # Первый заказ в списке
    FIRST_ORDER = (By.XPATH, "(//*[contains(@class,'OrderHistoryItem')])[1]")

    # Счётчики
    TOTAL_ALL_TIME = (
        By.XPATH,
        "//p[contains(text(),'Выполнено за все время')]/following-sibling::p"
    )
    TOTAL_TODAY = (
        By.XPATH,
        "//p[contains(text(),'Выполнено за сегодня')]/following-sibling::p"
    )

    # Номер заказа в модалке (после клика по заказу)
    ORDER_NUMBER_IN_MODAL = (By.XPATH, "//*[contains(@class,'Modal_modal')]//h2")




