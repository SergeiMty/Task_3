from selenium.webdriver.common.by import By


class CommonLocators:
    # Навигация в шапке
    ACCOUNT_LINK = (By.XPATH, "//p[normalize-space()='Личный Кабинет']/ancestor::a")
    CONSTRUCTOR_LINK = (By.XPATH, "//p[normalize-space()='Конструктор']/ancestor::a")
    FEED_LINK = (By.XPATH, "//p[normalize-space()='Лента Заказов']/ancestor::a")

    # Модалка (берём именно контейнер модалки, не overlay)
    MODAL = (By.CSS_SELECTOR, "section[class*='Modal_modal__'], div[class*='Modal_modal__']")
    MODAL_CLOSE_BUTTON = (By.CSS_SELECTOR, "button[class*='Modal_modal__close']")




