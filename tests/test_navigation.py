# W pliku: tests/test_navigation.py
import pytest
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

    # Krok 1: Pobierz wszystkie linki z menu za pomocą naszej metody z Page Objectu
    menu_links = home_page.get_main_menu_links()
    assert menu_links, "Nie znaleziono żadnych linków w menu głównym."

    failures = []  # Lista do zbierania błędów

    # Krok 2: Sprawdź każdy link w pętli
    for link in menu_links:
        link_text = link['text']
        href = link['href']

        logger.info(f"Checking link: '{link_text}' -> {href}")

        if not href:
            failures.append(f"Link '{link_text}' ma pusty atrybut href.")
            continue  # Przejdź do następnego linku

        try:
            response = requests.get(href, timeout=10, allow_redirects=True)
            if response.status_code >= 400:
                failures.append(
                    f"Link '{link_text}' ({href}) zwrócił błąd statusu: {response.status_code}"
                )
        except requests.RequestException as e:
            failures.append(
                f"Nie udało się połączyć z linkiem '{link_text}' ({href}). Błąd: {e}"
            )

    # Krok 3: Sprawdź, czy lista błędów jest pusta. Jeśli nie, zakończ test niepowodzeniem.
    assert not failures, f"Znaleziono uszkodzone linki w menu głównym:\n" + "\n".join(failures)