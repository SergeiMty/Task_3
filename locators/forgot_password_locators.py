from selenium.webdriver.common.by import By


class ForgotPasswordLocators:
    EMAIL_INPUT = (By.CSS_SELECTOR, "form input[name='name']")
    RESTORE_BUTTON = (By.XPATH, "//button[normalize-space()='Восстановить']")

    PASSWORD_INPUT = (By.CSS_SELECTOR, "form input[type='password']")

    SHOW_HIDE_PASSWORD_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'input') and .//input[@type='password']]//*[contains(@class,'input__icon')]"
    )

    PASSWORD_INPUT_WRAPPER = (
        By.XPATH,
        "//div[contains(@class,'input') and .//input[@type='password']]"
    )

    # Алиасы под разные варианты названий
    RECOVER_BUTTON = RESTORE_BUTTON
    SHOW_HIDE_BUTTON = SHOW_HIDE_PASSWORD_BUTTON

