# tests/test_product_page.py
import logging
from pages.product_page import ProductPage  # Typowanie dla lepszej czytelności

logger = logging.getLogger(__name__)

def test_product_details_displayed (product_page_fixture: ProductPage):
    """
    Sprawdzenie, czy szczegóły produktu są wyświetlane poprawnie
    na stronie produktu.
    """
    logger.info("Test: weryfikacja wyświetlania szczegółów produktu.")
    # Cała logika weryfikacji została przeniesiona do Page Objectu.
    # Wystarczy wywołać jedną metodę.
    product_page_fixture.verify_product_details_displayed()