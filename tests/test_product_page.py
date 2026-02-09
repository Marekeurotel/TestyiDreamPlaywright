import logging
from playwright.sync_api import expect
from pages.home_page import HomePage
from pages.product_page import ProductPage

logger = logging.getLogger(__name__)


def test_verify_product_details_via_search(page):
    """
    TC_PROD_001: Weryfikacja wyświetlania szczegółów produktu poprzez wyszukiwarkę.
    Rozwiązuje problem niestabilnych linków i TimeoutError.
    """
    home_page = HomePage(page)
    product_page = ProductPage(page)

    # KROK 1: Otwarcie strony głównej i obsługa popupów (np. cookies)
    logger.info("Krok 1: Otwieranie strony głównej.")
    home_page.open_page_and_handle_initial_popups()

    # KROK 2: Wyszukanie frazy
    search_query = "iPad"
    logger.info(f"Krok 2: Wyszukiwanie frazy: {search_query}")
    home_page.perform_search(search_query)

    # KROK 3: Wybór pierwszego produktu z wyników
    # Używamy dynamicznego selektora dla pierwszego produktu na liście
    logger.info("Krok 3: Kliknięcie w pierwszy produkt z listy wyników.")

    # 1. Lokator celujący w kontener produktu, który zawiera link
    # Szukamy linku, który jest tytułem produktu (zazwyczaj klasa .product-title lub wewnątrz .ut2-gl__name)
    first_product_link = page.locator("a.product-title, .ut2-gl__name a, .ut2-gl__body a").first

    try:
        # Zwiększamy nieco timeout i czekamy na stan 'attached', aby upewnić się, że DOM jest gotowy
        first_product_link.wait_for(state="visible", timeout=15000)

        product_name_text = first_product_link.inner_text().strip()
        logger.info(f"Znaleziono produkt: {product_name_text}. Klikam...")

        first_product_link.click()
    except Exception as e:
        # W razie błędu robimy zrzut ekranu – to kluczowe w ISTQB do dokumentacji defektu
        page.screenshot(path="failed_search_results.png")
        logger.error(f"Nie udało się kliknąć w produkt. Screenshot zapisany jako failed_search_results.png. Błąd: {e}")
        raise

    # KROK 4: Weryfikacja szczegółów na stronie produktu
    logger.info("Krok 4: Weryfikacja szczegółów produktu.")
    # Używamy Twojej metody z ProductPage do sprawdzenia ceny, opisu i specyfikacji
    product_page.verify_product_details_displayed()

    # Dodatkowa asercja sprawdzająca czy nazwa produktu nie jest pusta
    product_name = product_page.get_product_name()
    assert len(product_name) > 0, "Nazwa produktu jest pusta!"
    logger.info(f"Test zakończony sukcesem dla produktu: {product_name}")