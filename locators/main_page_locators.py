from selenium.webdriver.common.by import By


class MainPageLocators:
    # Кнопки
    LOGIN_MAIN_BUTTON = (By.XPATH, "//button[normalize-space()='Войти в аккаунт']")
    PLACE_ORDER_BUTTON = (By.XPATH, "//button[normalize-space()='Оформить заказ']")

    # Первый ингредиент (карточка)
    FIRST_INGREDIENT = (By.XPATH, "(//a[contains(@class,'BurgerIngredient_ingredient')])[1]")

    # Счётчик на карточке ингредиента
    FIRST_INGREDIENT_COUNTER_IN_CARD = (By.XPATH, ".//p[contains(@class,'counter_counter')]")

    # Зона конструктора (куда бросаем)
    CONSTRUCTOR_DROP_AREA = (By.XPATH, "//*[contains(@class,'BurgerConstructor_basket')]")

    # Любой элемент конструктора (появляется после добавления ингредиента)
    CONSTRUCTOR_ITEM = (By.XPATH, "//*[contains(@class,'BurgerConstructor_constructorElement')]")

    # Номер заказа в модалке
    ORDER_NUMBER_IN_MODAL = (By.XPATH, "//*[contains(@class,'Modal_modal')]//h2")

    # Алиас под старые импорты/ожидания
    ORDER_BUTTON = PLACE_ORDER_BUTTON
    ORDER_NUMBER = ORDER_NUMBER_IN_MODAL
