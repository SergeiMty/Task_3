from selenium.webdriver.common.by import By


class LoginPageLocators:
    EMAIL_INPUT = (By.XPATH, "//form//input[@name='name']")
    PASSWORD_INPUT = (By.XPATH, "//form//input[@type='password']")
    LOGIN_BUTTON = (By.XPATH, "//form//button[normalize-space()='Войти']")
    FORGOT_PASSWORD_LINK = (By.XPATH, "//a[normalize-space()='Восстановить пароль']")

