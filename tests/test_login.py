import pytest
from pages.login_page import LoginPage

TEST_USER_EMAIL = "mszylejko2@eurotel.pl"
TEST_USER_PASSWORD = "rickandmorty"

def test_successful_login(login_page_fixture: LoginPage):
    """
    Test weryfikuje logowanie przez bezpośrednie wejście na stronę logowania.
    """
    login_page = login_page_fixture

    # Krok 1: Przejdź bezpośrednio na stronę logowania
    login_page.navigate_to_login_page()

    # Krok 2: Zaloguj się
    login_page.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)

    # Krok 3: Sprawdź, czy logowanie się powiodło
    login_page.assert_login_is_successful()