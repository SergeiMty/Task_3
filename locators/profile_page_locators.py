from selenium.webdriver.common.by import By


class ProfilePageLocators:
    PROFILE_SECTION = (By.XPATH, "//a[normalize-space()='Профиль']")
    ORDER_HISTORY_SECTION = (By.XPATH, "//a[normalize-space()='История заказов']")
    LOGOUT_BUTTON = (By.XPATH, "//button[normalize-space()='Выход']")

    ORDER_IN_HISTORY = (
        By.XPATH,
        "//*[contains(@class,'OrderHistory')]//*[contains(@class,'OrderHistoryItem')]"
    )



