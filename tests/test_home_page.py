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
