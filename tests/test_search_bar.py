# tests/test_search_bar.py
import logging
from pages.home_page import HomePage
from tests.conftest import home_page_fixture  # Upewnij się, że importujesz fixturę

logger = logging.getLogger(__name__)


def test_search_for_iphone(home_page_fixture: HomePage):
    """
    Testuje funkcjonalność paska wyszukiwania, szukając "iPhone" i weryfikując wyniki.
    """
    logger.info("Test: wyszukiwanie produktu 'iPhone'.")

    # 1. Wyszukaj "iPhone"
    home_page_fixture.perform_search("iPhone")

    # 2. Zweryfikuj, że wyniki wyszukiwania są wyświetlane
    home_page_fixture.verify_search_results_exist()

    logger.info("Test wyszukiwania zakończony pomyślnie.")