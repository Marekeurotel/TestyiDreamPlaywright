# tests/test_security.py
import pytest
import logging
from pages.home_page import HomePage
from tests.conftest import home_page_fixture  # Upewnij się, że masz tę fixturę
from playwright._impl._errors import TimeoutError

logger = logging.getLogger(__name__)


pytestmark = pytest.mark.skip(reason="Testy bezpieczeństwa wyłączone do odwołania")

def test_sql_injection(home_page_fixture: HomePage):
    """
    Testuje podatność na SQL Injection, sprawdzając czy strona poprawnie blokuje atak.
    """
    logger.info("Test: podatność na SQL Injection")

    sql_payloads = [
        "' OR '1'='1",
        "1; DROP TABLE users;",
        "' UNION SELECT 1,2,3 --",
        "admin'--",
        "' OR 1=1#"
    ]

    for payload in sql_payloads:
            home_page_fixture.perform_search(payload)

            if home_page_fixture.is_blocked_by_waf():
                logger.info(f"✅ DOBRY WYNIK: Payload '{payload}' został zablokowany przez WAF")
                continue

            page_source = home_page_fixture.get_page_content()

            sql_errors = [
                "You have an error in your SQL syntax",
                "mysql_fetch_array()",
                "ORA-01756",
                "Unclosed quotation mark",
                "Syntax error",
                "Warning: mysql_",
                "PostgreSQL query failed",
                "ORA-00933",
                "Incorrect syntax near"
            ]

            for error in sql_errors:
                assert error.lower() not in page_source.lower(), f"❌ PODATNOŚĆ: Wykryto błąd SQL przy payload '{payload}': {error}"

            assert "root:" not in page_source, f"❌ PODATNOŚĆ: Możliwy wyciek danych systemowych przy payload: {payload}"

            logger.info(f"✅ Payload '{payload}' - brak wykrytych podatności")


#@pytest.mark.skip(reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
def test_xss_attack(home_page_fixture: HomePage):
    """
    Testuje podatność na XSS (Cross-Site Scripting).
    """
    logger.info("Test: podatność na XSS")

    xss_payloads = [
        "<script>alert('XSS')</script>",
        '\"><script>alert("XSS")</script>',
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')"
    ]

    for payload in xss_payloads:
        try:
            # KLUCZOWA ZMIANA: ZAWSZE OTWÓRZ STRONĘ GŁÓWNĄ PRZED KAŻDYM PAYLOADEM
            home_page_fixture.open_page_and_handle_initial_popups()

            # KROK 1: Wykonaj akcję WYSZUKIWANIA i poczekaj na załadowanie strony
            home_page_fixture.perform_search(payload)
            home_page_fixture.verify_search_results_exist()

            # KROK 2: Nasłuchuj na dialog (5 sekund wystarczy, bo strona jest już załadowana)
            with home_page_fixture.page.expect_event("dialog", timeout=5000):
                pass

            # BLOK TRY: Kod wykonuje się TYLKO, jeśli DIALOG SIĘ POJAWIŁ
            pytest.fail(f"❌ PODATNOŚĆ XSS: Wykryto alert JavaScript dla payload: {payload}")

        except TimeoutError:
            # BLOK EXCEPT TimeoutError: Kod wykonuje się, jeśli DIALOG SIĘ NIE POJAWIŁ (OCZEKIWANY WYNIK)

            if home_page_fixture.is_blocked_by_waf():
                logger.info(f"✅ DOBRY WYNIK: Payload '{payload}' zablokowany przez WAF")
            else:
                page_source = home_page_fixture.get_page_content()
                assert payload not in page_source, f"❌ PODATNOŚĆ XSS: Payload może być wykonalny: {payload}"
                logger.info(f"✅ Payload '{payload}' - brak wykrytych podatności XSS")

        except Exception as e:
            # Ten blok jest tylko dla błędów INNYCH niż TimeoutError (np. błąd lokatora)
            logger.error(f"Nieoczekiwany błąd (np. błąd lokatora) w teście XSS dla payload '{payload}': {e}")
            raise e

# @pytest.mark.skip(reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
def test_waf_bypass_attempts(home_page_fixture: HomePage):
    """Test próby ominięcia WAF - bardziej subtelne payloady."""
    logger.info("Test: WAF bypass attempts")

    bypass_payloads = [
        "1' /*comment*/ and '1'='1",
        "1' /*!UNION*/ /*!SELECT*/ 1,2,3--",
        "admin' or 1=1#",
        "test' waitfor delay '00:00:01'--",
        "<img src=x onerror=\u0061lert(1)>",
        "<svg><script>alert&#40;1&#41;</script>",
        "javascript:alert`1`",
        "<iframe srcdoc='&lt;script&gt;alert(1)&lt;/script&gt;'>"
    ]

    for payload in bypass_payloads:
        # ... perform search i get content ...

        if home_page_fixture.is_blocked_by_waf():
            logger.info(f"✅ WAF zablokował bypass attempt: {payload}")
        else:
            # WAF NIE ZABLOKOWAŁ - teraz sprawdzamy, czy doszło do PODATNOŚCI
            page_source = home_page_fixture.get_page_content().lower()
            vulnerability_found = False

            dangerous_indicators = [
                "you have an error in your sql syntax",
                "mysql_fetch_array()",
                "root:x:",
                payload.lower()  # Sprawdź, czy payload został wstrzyknięty/wykonany
            ]

            for indicator in dangerous_indicators:
                if indicator in page_source:
                    pytest.fail(
                        f"❌ KRYTYCZNA PODATNOŚĆ: Bypass WAF skuteczny dla '{payload}' - wykryto: {indicator}")
                    vulnerability_found = True
                    break

            if not vulnerability_found:
                logger.info(f"✅ Payload '{payload}' - brak wykrytych podatności (WAF bypass nie powiódł się)")


#@pytest.mark.skip(reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
def test_csrf_protection_presence(home_page_fixture: HomePage):
    """
    Testuje obecność tokenów CSRF.
    """
    logger.info("Test: obecność tokenów CSRF")

    csrf_indicators = [
        # Najpopularniejsze i uniwersalne
        'name="csrf_token"',
        'name="_token"',
        'name="authenticity_token"',
        'name="csrfmiddlewaretoken"',

        # Ogólne wskaźniki pól wejściowych dla tokenów (hidden)
        'type="hidden" name="token"',
        'type="hidden" name="security_hash"',  # Czasem używane jako token

        # Wskaźniki w nagłówkach HTTP/META (Playwright łapie tylko treść HTML)
        '<meta name="csrf-token"',

        # Specyficzny wskaźnik dla tej platformy (CS-Cart/przykładowe tokeny)
        'security_hash',
        'dispatch[session_token]'  # Wskaźnik, który może pojawić się w JS/URL
    ]

    page_source = home_page_fixture.get_page_content().lower()

    found_csrf_tokens = [indicator for indicator in csrf_indicators if indicator in page_source]

    if found_csrf_tokens:
        logger.info(f"✅ Wykryto tokeny CSRF: {found_csrf_tokens}")
    else:
        pytest.fail("⚠️  Nie wykryto tokenów CSRF - aplikacja może być podatna na CSRF")

    # Sprawdź nagłówki w meta tagu, jeśli istnieje
    try:
        response = home_page_fixture.page.locator("meta[name='csrf-token']").get_attribute("content")
        if response:
            logger.info("✅ Znaleziono CSRF token w meta tagu.")
    except Exception:
        pass  # Jeśli meta tagu nie ma, to nie jest błąd, tylko informacja


#@pytest.mark.skip(reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
def test_input_validation(home_page_fixture: HomePage):
    """Test walidacji danych wejściowych."""
    logger.info("Test: walidacja danych wejściowych")

    validation_payloads = [
        "A" * 1000,
        "../../../etc/passwd",
        "{{7*7}}",
        "${7*7}",
        "<?php echo 'test'; ?>",
        "\x00"
    ]

    system_indicators = [
        "root:x:",
        "[boot loader]",
        "127.0.0.1",
        "localhost"
    ]

    for payload in validation_payloads:
            try:
                # Wykonanie wyszukiwania z ulepszonymi timeoutami w perform_search
                home_page_fixture.perform_search(payload)
                
                # Dodatkowe oczekiwanie na pełne załadowanie treści strony przed pobraniem
                # Upewniamy się, że strona jest w pełni gotowa do analizy
                home_page_fixture.page.wait_for_load_state("domcontentloaded", timeout=30000)
                
                page_source = home_page_fixture.get_page_content()

                if home_page_fixture.is_blocked_by_waf():
                    logger.info(f"✅ WAF zablokował payload walidacji: {payload}")
                    continue

                for indicator in system_indicators:
                    assert indicator not in page_source, f"❌ Możliwy wyciek plików systemowych przy payload: {payload}"

                if "{{7*7}}" in payload or "${7*7}" in payload:
                    assert "49" not in page_source, "❌ Możliwa podatność na injection"

                logger.info(f"✅ Payload '{payload}' - brak wykrytych podatności walidacji")
                
            except TimeoutError as e:
                # Logowanie szczegółowych informacji o błędzie timeout dla diagnostyki
                logger.error(f"⏱️ TimeoutError dla payload '{payload}': {e}")
                # Zrzut ekranu dla analizy problemu
                home_page_fixture.page.screenshot(path=f"timeout_error_{payload[:20].replace('/', '_')}.png")
                raise