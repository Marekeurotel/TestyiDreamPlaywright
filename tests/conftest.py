import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.product_page import ProductPage # Zostawiamy, jeśli jest używane w innych testach
from pages.login_page import LoginPage

@pytest.fixture(scope="function")
def home_page_fixture(page: Page) -> HomePage:
    home_page_instance = HomePage(page)
    home_page_instance.open_page_and_handle_initial_popups()
    yield home_page_instance

@pytest.fixture(scope="function")
def product_page_fixture(page: Page) -> ProductPage:
    product_page_instance = ProductPage(page)
    # Jeśli ProductPage też potrzebuje obsługi popupów, musisz dodać podobną metodę
    # product_page_instance.open_page_and_handle_initial_popups()
    yield product_page_instance

@pytest.fixture(scope="function")
def login_page_fixture(page: Page) -> LoginPage:
    """
    Prosta fixtura, która tylko inicjalizuje instancję LoginPage.
    Nie nawiguje na żadną stronę - to zadanie dla testu.
    """
    yield LoginPage(page)