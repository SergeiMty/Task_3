from selenium.webdriver.common.by import By


class CommonLocators:
    ACCOUNT_LINK = (By.XPATH, "//p[normalize-space()='Личный Кабинет']/ancestor::a")
    CONSTRUCTOR_LINK = (By.XPATH, "//p[normalize-space()='Конструктор']/ancestor::a")
    FEED_LINK = (By.XPATH, "//p[normalize-space()='Лента Заказов']/ancestor::a")

    MODAL = (By.XPATH, "//*[contains(@class,'Modal_modal')]")
    MODAL_CLOSE_BUTTON = (By.XPATH, "//*[contains(@class,'Modal_modal__close')]")


