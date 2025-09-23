# tests/test_home_page.py
import logging
from playwright.sync_api import expect
from tests.conftest import home_page_fixture # Importujemy fixturę (niepotrzebne jeśli w tym samym pliku, ale dla jasności)

logger = logging.getLogger(__name__)

def test_home_page_title(home_page_fixture):
    logger.info("Test: sprawdzenie tytułu strony głównej.")
    expect(home_page_fixture.page).to_have_title("iDream Apple Sklep internetowy - Apple Premium Reseller Polska")
    logger.info("✅ Tytuł strony głównej jest poprawny.")

def test_social_media_links(home_page_fixture):
    logger.info("Test: sprawdzanie linków do mediów społecznościowych.")
    # Przykład testowania Instagrama
    expected_instagram_url = home_page_fixture.get_social_media_expected_url('instagram')
    instagram_popup = home_page_fixture.click_social_media_button('instagram')
    expect(instagram_popup).to_have_url(expected_instagram_url)
    logger.info(f"✅ Link do Instagrama prowadzi do {expected_instagram_url}.")
    instagram_popup.close() # Zamknij nowo otwartą stronę

    # Możesz dodać więcej testów dla Facebooka, TikToka, YouTube