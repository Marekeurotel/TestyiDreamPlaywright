# tests/test_security.py
import pytest
import logging
from playwright.sync_api import Page
from pages.home_page import HomePage
from tests.conftest import home_page_fixture  # Upewnij się, że masz tę fixturę

logger = logging.getLogger(__name__)


@pytest.mark.skip(
    reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
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
        with pytest.warns(None):  # Pytest ignoruje ostrzeżenia w tej pętli, co pozwala na kontynuację
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


@pytest.mark.skip(reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
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
        with pytest.warns(None):
            try:
                with home_page_fixture.page.expect_event("dialog", timeout=3000):
                    home_page_fixture.perform_search(payload)

                # Jeśli alert się pojawił, test kończy się niepowodzeniem
                pytest.fail(f"❌ PODATNOŚĆ XSS: Wykryto alert JavaScript dla payload: {payload}")

            except TimeoutError:
                # Brak alertu jest oczekiwanym rezultatem
                if home_page_fixture.is_blocked_by_waf():
                    logger.info(f"✅ DOBRY WYNIK: Payload '{payload}' zablokowany przez WAF")
                else:
                    page_source = home_page_fixture.get_page_content()
                    assert payload not in page_source, f"❌ PODATNOŚĆ XSS: Payload może być wykonalny: {payload}"

                    escaped_checks = ["&lt;script&gt;", "&quot;", "&#x27;", "&amp;"]
                    found_escaping = any(check in page_source for check in escaped_checks)

                    if found_escaping:
                        logger.info(f"✅ Znaleziono poprawne escapowanie dla payload: {payload}")
                    elif any(char in payload for char in ['<', '>', '"', "'"]):
                        pytest.fail(f"⚠️  Brak widocznego escapowania dla payload: {payload}")

                logger.info(f"✅ Payload '{payload}' - brak wykrytych podatności XSS")


@pytest.mark.skip(
    reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
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
        with pytest.warns(None):
            home_page_fixture.perform_search(payload)
            page_source = home_page_fixture.get_page_content()

            if home_page_fixture.is_blocked_by_waf():
                logger.info(f"✅ WAF zablokował bypass attempt: {payload}")
            else:
                pytest.fail(f"❌ KRYTYCZNA PODATNOŚĆ: Możliwy bypass WAF: {payload}")

                # Dodatkowe weryfikacje, jeśli bypass się powiódł
                dangerous_indicators = [
                    "You have an error in your SQL syntax",
                    "mysql_fetch_array()",
                    "root:x:",
                    payload
                ]

                for indicator in dangerous_indicators:
                    if indicator.lower() in page_source.lower():
                        pytest.fail(
                            f"❌ KRYTYCZNA PODATNOŚĆ: Bypass WAF skuteczny dla '{payload}' - wykryto: {indicator}")


@pytest.mark.skip(
    reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
def test_csrf_protection_presence(home_page_fixture: HomePage):
    """
    Testuje obecność tokenów CSRF.
    """
    logger.info("Test: obecność tokenów CSRF")

    csrf_indicators = [
        'name="csrf_token"',
        'name="_token"',
        'name="authenticity_token"',
        'name="csrfmiddlewaretoken"',
        'name="token"',
        'x-csrf-token'
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


@pytest.mark.skip(
    reason="Testy bezpieczeństwa działają i poprawnie wykrywają WAF. Uruchamiaj je tylko w razie potrzeby.")
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
        with pytest.warns(None):
            home_page_fixture.perform_search(payload)
            page_source = home_page_fixture.get_page_content()

            if home_page_fixture.is_blocked_by_waf():
                logger.info(f"✅ WAF zablokował payload walidacji: {payload}")
                continue

            for indicator in system_indicators:
                assert indicator not in page_source, f"❌ Możliwy wyciek plików systemowych przy payload: {payload}"

            if "{{7*7}}" in payload or "${7*7}" in payload:
                assert "49" not in page_source, "❌ Możliwa podatność na injection"

            logger.info(f"✅ Payload '{payload}' - brak wykrytych podatności walidacji")