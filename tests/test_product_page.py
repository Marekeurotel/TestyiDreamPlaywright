import logging
from pages.product_page import ProductPage

logger = logging.getLogger(__name__)


def test_product_details_displayed(product_page_fixture: ProductPage):
    """
    Sprawdzenie, czy szczegóły produktu są wyświetlane poprawnie
    na stronie produktu.
    """
    home_page = product_page_fixture  # Zmieniamy nazwę dla czytelności
    logger.info("Test: weryfikacja wyświetlania szczegółów produktu.")

    # 1. KROK BRAKUJĄCY: Otwórz stronę produktu!
    home_page.open_product_page()  # <--- TUTAJ JEST BRAKUJĄCE WYWOŁANIE

    # 2. Wywołaj logikę weryfikacji.
    home_page.verify_product_details_displayed()