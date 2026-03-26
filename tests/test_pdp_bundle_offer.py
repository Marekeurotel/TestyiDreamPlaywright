import pytest
import logging
from playwright.sync_api import Page, expect
from pages.product_page import ProductPage

logger = logging.getLogger(__name__)

# Parametryzacja testu dla 3 różnych stron PDP (tu można dodawać kolejne URL-e).
# Zgodnie z Twoją prośbą, można łatwo rozbudować tę listę.
PRODUCT_URLS = [
    "https://idream.pl/iphone/apple-iphone-15/apple-iphone-15-128gb-niebieski.html",
    "https://idrim.ovh/iphone/apple-iphone-15/apple-iphone-15-128gb-niebieski.html",
    "https://idream.pl/ipad/ipad-air/apple-ipad-air-13-m2-128gb-wi-fi-cellular-6.gen-gwiezdna-szarosc-2024.html"
]

@pytest.mark.parametrize("product_url", PRODUCT_URLS)
def test_pdp_bundle_offer_presence(page: Page, product_url: str):
    """
    TC_PDP_BUNDLE_001: Sprawdza obecność oferty zestawu na stronie PDP produktu.
    Weryfikuje:
      1. Widoczność kontenera zestawu (div.ab__bt_box)
      2. Widoczność i klikalność przycisku "Dodaj zestaw do koszyka"
    Test UPADA jeśli sekcja zestawu nie istnieje na stronie (zgodnie z wymogiem).
    """
    logger.info(f"Test PDP Bundle dla URL: {product_url}")
    product_page = ProductPage(page)

    # 1. Przejdź na stronę i obsłuż popupy (cookies, BHR itp.)
    product_page.open_specific_product_and_handle_popups(product_url)

    # Upewniamy się, że strona została w całości załadowana
    # (sekcja bundle często ładuje się chwilę po wczytaniu DOM-u docelowego - np. jako AJAX)
    page.wait_for_load_state("networkidle", timeout=30000)

    # Lekkie przewinięcie, żeby aktywować lazy-loading dla sekcji niżej na stronie.
    page.evaluate("window.scrollTo(0, 1000)")
    page.wait_for_timeout(1000)

    # 2. Definicja lokatorów
    # UWAGA: Klasa CSS to "ab__bt_box" (dwa podkreślenia), potwierdzone inspekcją DOM.
    bundle_box_locator = page.locator("div.ab__bt_box")

    # Lokator na przycisk "Dodaj zestaw do koszyka" wewnątrz sekcji bundle.
    # Z inspekcji DOM: jest to div z klasą "cm-ab__bt-submit" zawierający tekst przycisku.
    bundle_add_btn_locator = page.locator("div.cm-ab__bt-submit")

    # 3. Krok asercji - Sekcja .ab__bt_box MUSI być widoczna.
    # Jeśli nie jest, test natychmiast upada (zgodnie z wymogiem użytkownika).
    logger.info("Sprawdzam widoczność sekcji ab__bt_box...")
    expect(bundle_box_locator).to_be_visible(timeout=10000)
    logger.info("✅ Sekcja ab__bt_box jest widoczna.")

    # Przewijamy do tej sekcji, żeby Playwright "widział" przycisk w viewporcie
    bundle_box_locator.scroll_into_view_if_needed()

    # 4. Krok asercji - Przycisk w sekcji bundle MUSI być widoczny
    logger.info("Sprawdzam obecność przycisku 'Dodaj zestaw do koszyka' w sekcji zestawu...")
    expect(bundle_add_btn_locator).to_be_visible(timeout=5000)

    # Weryfikacja czy przycisk nie jest wyszarzony/zablokowany (enabled check)
    expect(bundle_add_btn_locator).to_be_enabled(timeout=5000)

    # Sprawdzenie, czy tekst przycisku zawiera "Dodaj zestaw do koszyka"
    expect(bundle_add_btn_locator).to_contain_text("Dodaj zestaw do koszyka")

    logger.info(f"✅ Przycisk 'Dodaj zestaw do koszyka' widoczny i aktywny dla {product_url}")
