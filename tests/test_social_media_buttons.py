# tests/test_social_media_buttons.py
import pytest
import logging
from playwright.sync_api import Page, expect
from tests.conftest import home_page_fixture
from pages.home_page import HomePage

logger = logging.getLogger(__name__)

# Możemy użyć parametryzacji Pytesta, aby uniknąć powtarzania kodu dla każdego linku
@pytest.mark.parametrize("button_type, expected_url_template", [
    ('instagram', "https://www.instagram.com/idream_pl/"),
    ('facebook', "https://www.facebook.com/iDreamPolska/"),
    ('tiktok', "https://www.tiktok.com/@idream_pl"),
    # Dla YouTube nadal musisz zdecydować, czy oczekujesz dynamicznego URL-a
    # czy uda się dotrzeć do statycznego. Ustawiamy go z nowym, bardziej prawdopodobnym URL.
    ('youtube', "https://www.youtube.com/user/iDreamPL"), # Proponowany rzeczywisty URL kanału iDream
])
def test_social_media_links(home_page_fixture: HomePage, button_type: str, expected_url_template: str):
    logger.info(f"Test: sprawdzanie linku dla {button_type}.")

    popup_page: Page = home_page_fixture.click_social_media_button(button_type)

    # --- NOWA, SPECJALNA LOGIKA DLA YOUTUBE ---
    if button_type == 'youtube':
        try:
            logger.info("YouTube detected. Handling consent page if present...")
            # Znajdujemy przycisk "Akceptuj wszystko" (lub podobny) na stronie zgody
            accept_button = popup_page.get_by_role(
                "button", name="Akceptuj wszystko"
            ).first

            # Czekamy krótko, bo może go nie być, jeśli zgody zostały już zapisane
            expect(accept_button).to_be_visible(timeout=5000)
            accept_button.click()

            # Po kliknięciu czekamy, aż strona przeładuje się na docelowy URL
            logger.info("Consent button clicked. Waiting for navigation to the final URL...")
            popup_page.wait_for_url(f"**/{expected_url_template}/**", timeout=10000)

        except Exception as e:
            logger.warning(f"Could not handle YouTube consent page (it might not have appeared): {e}")
    # --- KONIEC LOGIKI DLA YOUTUBE ---

    current_url = popup_page.url
    logger.info(f"Otwarty URL dla {button_type}: {current_url}")

    assert current_url.startswith(expected_url_template), (
        f"Odnośnik do {button_type} jest niepoprawny. Oczekiwano startu z '{expected_url_template}', otrzymano '{current_url}'."
    )

    # Ważne: Zamykamy nowo otwarte okno/kartę po zakończeniu testu.
    popup_page.close()
    logger.info(f"✅ Link do {button_type} jest poprawny i okno zostało zamknięte.")