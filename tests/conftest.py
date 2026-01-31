import os
import random
import string
import pytest
import allure

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from api.client import StellarApiClient


def random_string(n=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))


def make_user():
    email = f"sergey_{random_string(6)}@mail.ru"
    password = f"Qwerty_{random_string(6)}1"
    name = f"Sergey_{random_string(5)}"
    return email, password, name


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--headless", action="store_true")

    parser.addoption(
        "--ui_url",
        action="store",
        default=os.getenv("UI_URL", "https://stellarburgers.education-services.ru/")
    )

    parser.addoption(
        "--api_url",
        action="store",
        default=os.getenv("API_URL", "https://stellarburgers.education-services.ru")
    )


@pytest.fixture
def ui_url(request):
    url = request.config.getoption("--ui_url")
    if not url.endswith("/"):
        url += "/"
    return url


@pytest.fixture
def api_url(request):
    return request.config.getoption("--api_url")


@pytest.fixture
def api_client(api_url):
    return StellarApiClient(api_url)


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")

    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--incognito")
        options.add_argument("--disable-gpu")

        if headless:
            options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)

    else:
        raise ValueError("Только chrome или firefox")

    driver.set_page_load_timeout(30)
    yield driver
    driver.quit()


@pytest.fixture
def user(api_client):
    email, password, name = make_user()

    reg = api_client.register_user(email, password, name)
    assert reg.get("success") is True, f"Не удалось создать пользователя: {reg}"

    access_token = reg["accessToken"]

    yield {"email": email, "password": password, "name": name, "access_token": access_token}

    with allure.step("Удаление тестового пользователя"):
        api_client.delete_user(access_token)