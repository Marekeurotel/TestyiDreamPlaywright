# tests/test_social_media_buttons.py
import pytest
import logging
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import Page, expect
from tests.conftest import home_page_fixture
from pages.home_page import HomePage

logger = logging.getLogger(__name__)


def _handle_youtube_consent(popup_page: Page, expected_url: str) -> str:
    """
    Obsługuje stronę zgody YouTube (consent.youtube.com).
    Próbuje zaakceptować zgodę i nawigować do docelowego URL.
    Zwraca finalny URL po obsłudze.
    """
    # Czekamy aż strona się w pełni załaduje
    popup_page.wait_for_load_state("domcontentloaded", timeout=15000)
    logger.info(f"YouTube popup URL po załadowaniu: {popup_page.url}")

    if "consent.youtube.com" not in popup_page.url:
        logger.info("Brak strony consent YouTube — bezpośrednie przekierowanie.")
        return popup_page.url

    logger.info("Strona consent YouTube wykryta. Próbuję zaakceptować...")

    # Rozbudowana lista selektorów — od najbardziej specyficznych do ogólnych
    accept_selectors = [
        # Specyficzne selektory Google/YouTube consent
        "button[jsname='VgvcLd']",
        # Selektory bazujące na tekście (PL)
        "button:has-text('Akceptuję wszystko')",
        "button:has-text('Zaakceptuj wszystko')",
        # Selektory bazujące na tekście (EN)
        "button:has-text('Accept all')",
        "button:has-text('I agree')",
        # Selektor formularza consent
        "form[action*='consent'] button[type='submit']",
        # Aria-label
        "button[aria-label*='Akceptuj']",
        "button[aria-label*='Accept']",
    ]

    clicked = False
    for selector in accept_selectors:
        try:
            btn = popup_page.locator(selector).first
            if btn.is_visible(timeout=2000):
                btn.click(timeout=5000)
                logger.info(f"✅ Kliknięto przycisk consent: {selector}")
                clicked = True
                break
        except Exception:
            continue

    if not clicked:
        logger.warning("Nie znaleziono żadnego przycisku consent. Próbuję submit formularza...")
        try:
            # Ostatnia deska ratunku: submit dowolnego formularza consent
            form = popup_page.locator("form[action*='consent']").first
            if form.is_visible(timeout=2000):
                # Kliknij pierwszy przycisk w formularzu
                submit_btn = form.locator("button").first
                if submit_btn.is_visible(timeout=2000):
                    submit_btn.click(timeout=5000)
                    logger.info("✅ Kliknięto przycisk w formularzu consent.")
                    clicked = True
        except Exception as e:
            logger.warning(f"Submit formularza też się nie powiódł: {e}")

    if clicked:
        # Czekamy na przekierowanie po zaakceptowaniu
        try:
            popup_page.wait_for_url(
                lambda url: "consent.youtube.com" not in url,
                timeout=15000
            )
            logger.info(f"✅ Przekierowano po consent na: {popup_page.url}")
        except Exception as e:
            logger.warning(f"Timeout czekając na przekierowanie po consent: {e}")

    return popup_page.url


def _validate_youtube_url(current_url: str, expected_url: str) -> bool:
    """
    Sprawdza poprawność URL YouTube — obsługuje zarówno bezpośredni URL
    jak i stronę consent z parametrem 'continue' zawierającym docelowy URL.
    """
    # Przypadek 1: Bezpośredni URL
    if current_url.startswith(expected_url):
        return True

    # Przypadek 2: Nadal na consent — sprawdzamy parametr 'continue'
    if "consent.youtube.com" in current_url:
        parsed = urlparse(current_url)
        params = parse_qs(parsed.query)
        continue_url = params.get("continue", [""])[0]
        if expected_url.rstrip("/") in continue_url:
            logger.info(
                f"URL jest na consent, ale parametr 'continue' wskazuje na poprawny cel: {continue_url}"
            )
            return True

    return False


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

    # --- SPECJALNA LOGIKA DLA YOUTUBE ---
    if button_type == 'youtube':
        current_url = _handle_youtube_consent(popup_page, expected_url_template)

        # Elastyczna asercja — akceptuje bezpośredni URL lub consent z poprawnym 'continue'
        assert _validate_youtube_url(current_url, expected_url_template), (
            f"Odnośnik do YouTube jest niepoprawny. "
            f"Oczekiwano URL zaczynającego się od '{expected_url_template}' "
            f"(lub consent z parametrem 'continue' wskazującym na ten URL), "
            f"otrzymano '{current_url}'."
        )
        logger.info(f"✅ Link do YouTube jest poprawny: {current_url}")
        popup_page.close()
        return
    # --- KONIEC LOGIKI DLA YOUTUBE ---

    current_url = popup_page.url
    logger.info(f"Otwarty URL dla {button_type}: {current_url}")

    assert current_url.startswith(expected_url_template), (
        f"Odnośnik do {button_type} jest niepoprawny. "
        f"Oczekiwano startu z '{expected_url_template}', otrzymano '{current_url}'."
    )

    # Ważne: Zamykamy nowo otwarte okno/kartę po zakończeniu testu.
    popup_page.close()
    logger.info(f"✅ Link do {button_type} jest poprawny i okno zostało zamknięte.")