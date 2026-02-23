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
    ('youtube', "https://www.youtube.com/user/iDreamPL"),
])
def test_social_media_links(home_page_fixture: HomePage, button_type: str, expected_url_template: str):
    logger.info(f"Test: sprawdzanie linku dla {button_type}.")

    popup_page: Page = home_page_fixture.click_social_media_button(button_type)

    # --- NOWA, SPECJALNA LOGIKA DLA YOUTUBE ---
    if button_type == 'youtube':
        try:
            logger.info("YouTube detected. Checking for consent page...")
            if "consent.youtube.com" in popup_page.url:
                logger.info("YouTube consent page detected. Attempting to accept...")
                
                # Rozbudowana lista selektorów z raportu analizy
                accept_selectors = [
                    "button[aria-label*='Akceptuję' i]",
                    "button:has-text('Akceptuję wszystko')",
                    "button:has-text('Accept all')",
                    "form[action*='consent.youtube.com'] button[type='submit']"
                ]
                
                found = False
                for selector in accept_selectors:
                    btn = popup_page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        logger.info(f"Clicked YouTube consent button: {selector}")
                        found = True
                        break
                
                if not found:
                    logger.warning("Could not find any known YouTube consent button. Trying Escape key.")
                    popup_page.keyboard.press("Escape")
                
                # Czekamy na załadowanie docelowej strony
                logger.info("Waiting for navigation to the final YouTube URL...")
                popup_page.wait_for_url(f"**/{expected_url_template}**", timeout=15000)
            else:
                logger.info("YouTube consent page not detected. Continuing...")

        except Exception as e:
            logger.warning(f"Error while handling YouTube consent: {e}")
    # --- KONIEC LOGIKI DLA YOUTUBE ---

    current_url = popup_page.url
    logger.info(f"Otwarty URL dla {button_type}: {current_url}")

    assert current_url.startswith(expected_url_template), (
        f"Odnośnik do {button_type} jest niepoprawny. Oczekiwano startu z '{expected_url_template}', otrzymano '{current_url}'."
    )

    # Ważne: Zamykamy nowo otwarte okno/kartę po zakończeniu testu.
    popup_page.close()
    logger.info(f"✅ Link do {button_type} jest poprawny i okno zostało zamknięte.")