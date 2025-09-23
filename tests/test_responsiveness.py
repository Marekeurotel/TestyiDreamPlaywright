# tests/test_responsiveness.py
import pytest
import logging
from playwright.sync_api import Page, expect

# Importujemy fixturę home_page_fixture
from tests.conftest import home_page_fixture
from pages.home_page import HomePage

logger = logging.getLogger(__name__)

# Używamy parametryzacji, aby uruchomić ten sam test dla różnych widoków
@pytest.mark.parametrize("viewport_size, device_name", [
    ({"width": 1920, "height": 1080}, "desktopie"),
    ({"width": 768, "height": 1024}, "tablecie"),
    ({"width": 375, "height": 812}, "mobile"),
])
def test_page_responsiveness(page: Page, viewport_size: dict, device_name: str):
    """
    Testuje responsywność strony głównej poprzez weryfikację widoczności logo
    na różnych rozmiarach ekranu.
    :type viewport_size: object
    """
    logger.info(f"Test responsywności na {device_name} (rozmiar: {viewport_size['width']}x{viewport_size['height']}).")

    # Ustawienie rozmiaru okna przeglądarki na początku testu
    page.set_viewport_size(viewport_size)

    # Nawigacja do strony i obsługa popupów
    # Tworzymy instancję HomePage, aby nie polegać na fixture, która otwiera już stronę
    # z domyślnym rozmiarem okna.
    home_page = HomePage(page)
    home_page.open_page_and_handle_initial_popups()

    # Lokator logo z Page Objecta (z BasePage, bo logo jest na każdej stronie)
    logo_locator = home_page.page.locator(".top-logo img[alt='Logo iDream']").first

    # Asercja z Playwrighta. Oczekuje, że logo będzie widoczne w ciągu 10s.
    try:
        expect(logo_locator).to_be_visible(timeout=10000)
        logger.info(f"✅ Logo jest widoczne na {device_name}. Strona wyświetla się poprawnie.")
    except TimeoutError:
        error_message = f"❌ BŁĄD: Logo nie zostało znalezione na {device_name}. Strona nie wyświetla się poprawnie."
        logger.error(error_message)
        # Zrzut ekranu jest bardzo pomocny przy debugowaniu responsywności
        page.screenshot(path=f"screenshot_error_{device_name}.png")
        pytest.fail(error_message)