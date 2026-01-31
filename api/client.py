import requests


class StellarApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def register_user(self, email: str, password: str, name: str) -> dict:
        url = f"{self.base_url}/api/auth/register"
        payload = {"email": email, "password": password, "name": name}
        return requests.post(url, json=payload).json()

    def login_user(self, email: str, password: str) -> dict:
        url = f"{self.base_url}/api/auth/login"
        payload = {"email": email, "password": password}
        return requests.post(url, json=payload).json()

    def delete_user(self, access_token: str) -> requests.Response:
        url = f"{self.base_url}/api/auth/user"
        headers = {"Authorization": access_token}
        return requests.delete(url, headers=headers)

    def get_ingredients(self) -> dict:
        url = f"{self.base_url}/api/ingredients"
        return requests.get(url).json()

    def create_order(self, ingredient_ids: list[str], access_token: str | None = None) -> dict:
        url = f"{self.base_url}/api/orders"
        headers = {}
        if access_token:
            headers["Authorization"] = access_token
        payload = {"ingredients": ingredient_ids}
        return requests.post(url, json=payload, headers=headers).json()
