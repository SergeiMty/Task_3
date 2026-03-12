from selenium.webdriver.common.by import By


class FeedPageLocators:
    # Список заказов слева
    ORDER_LIST = (By.XPATH, "//ul[contains(@class,'OrderFeed_orderList')]")

    # Первый заказ — карточка (li). Клик по карточке обычно стабильнее, чем по вложенной ссылке.
    FIRST_ORDER_CARD = (By.XPATH, "(//ul[contains(@class,'OrderFeed_orderList')]//li)[1]")

    # Ссылка на заказ /feed/<id> (подстраховка, если карточка не кликается)
    FIRST_ORDER_LINK = (By.XPATH, "(//ul[contains(@class,'OrderFeed_orderList')]//a[contains(@href,'/feed/')])[1]")

    # Модалка/детали заказа
    MODAL_CONTAINER = (By.XPATH, "//*[contains(@class,'Modal_modal')]")
    MODAL_CLOSE_BTN = (By.XPATH, "//*[contains(@class,'Modal_modal')]//button[contains(@class,'close')]")
    ORDER_DETAILS_TITLE = (By.XPATH, "//*[normalize-space()='Детали заказа']")

    # Счётчики
    TOTAL_ALL_TIME = (
        By.XPATH,
        "//p[contains(text(),'Выполнено за все время')]/following-sibling::p"
    )
    TOTAL_TODAY = (
        By.XPATH,
        "//p[contains(text(),'Выполнено за сегодня')]/following-sibling::p"
    )

    # Правая колонка статусов
    READY_NUMBERS = (By.XPATH, "//p[normalize-space()='Готовы:']/following-sibling::ul//li")
    IN_WORK_NUMBERS = (By.XPATH, "//p[normalize-space()='В работе:']/following-sibling::ul//li")
