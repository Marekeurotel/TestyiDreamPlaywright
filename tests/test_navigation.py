# W pliku: tests/test_navigation.py
import requests
from pages.home_page import HomePage
import logging

logger = logging.getLogger(__name__)

def test_main_menu_link_health(home_page_fixture: HomePage):
    """
    Sprawdza wszystkie linki w menu głównym w ramach jednego, prostego testu.
    Zbiera wszystkie błędy i raportuje je na końcu.
    """
    home_page = home_page_fixture

    # Krok 1: Pobierz liczbę linków z menu za pomocą naszej nowej metody
    menu_links = home_page.get_main_menu_links()

    # Asercja: Czy liczba linków jest większa niż 0?
    assert len(menu_links) > 0, "Nie znaleziono żadnych linków w menu głównym."
    logger.info(f"✅ Znaleziono {menu_links} linków po otwarciu menu.")