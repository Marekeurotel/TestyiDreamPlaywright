# tests/test_home_page.py
import logging
from playwright.sync_api import expect
from pages.home_page import HomePage
from tests.conftest import home_page_fixture # Importujemy fixturę (niepotrzebne jeśli w tym samym pliku, ale dla jasności)

logger = logging.getLogger(__name__)

def test_home_page_title(home_page_fixture):
    logger.info("Test: sprawdzenie tytułu strony głównej.")
    expect(home_page_fixture.page).to_have_title("iDream Apple Sklep internetowy - Apple Premium Reseller Polska")
    logger.info("✅ Tytuł strony głównej jest poprawny.")


def test_social_media_links(home_page_fixture: HomePage):
    """
    Testuje wszystkie przyciski mediów społecznościowych, iterując po ich typach
    pobranych bezpośrednio z Page Objectu.
    """
    logger.info("Test: sprawdzanie linków do wszystkich mediów społecznościowych.")

    # 1. Pobieramy listę kluczy (typów mediów) z zdefiniowanego słownika w HomePage.
    # Używamy kluczy ze słownika 'social_media_buttons'.
    social_media_types = home_page_fixture.social_media_buttons.keys()

    errors = []

    for media_type in social_media_types:
        logger.info(f"--- Testowanie medium: {media_type} ---")

        try:
            # A) Pobierz oczekiwany URL (wywołuje get_social_media_expected_url z HomePage)
            expected_url = home_page_fixture.get_social_media_expected_url(media_type)

            # B) Kliknij przycisk i poczekaj na nowe okno/kartę (wywołuje click_social_media_button)
            popup_page = home_page_fixture.click_social_media_button(media_type)

            # C) Weryfikacja URL
            # Używamy to_have_url z opcją 'containing', ponieważ URL może mieć
            # drobne różnice (np. z/bez 'www', kończący się '/', inny protokół).
            expect(popup_page).to_have_url(expected_url, timeout=10000)

            logger.info(f"✅ Link do {media_type} prowadzi poprawnie.")
            popup_page.close()

        except Exception as e:
            # Zbieranie błędów, aby test nie przerywał się po pierwszym niepowodzeniu
            error_msg = f"❌ BŁĄD podczas testowania {media_type}. Oczekiwany URL: {expected_url}. Błąd: {e}"
            errors.append(error_msg)
            logger.error(error_msg)

            # Dodatkowa próba zamknięcia popupu, by nie zakłócał następnej iteracji
            try:
                if 'popup_page' in locals() and not popup_page.is_closed():
                    popup_page.close()
            except Exception:
                pass

                # 2. Globalna asercja
    assert not errors, "\n\n" + "Następujące linki mediów społecznościowych zawiodły:\n" + "\n".join(errors)