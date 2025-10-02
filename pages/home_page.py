import logging
from playwright.sync_api import Page, expect, TimeoutError
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    # NOWE LOKATORY ZWIĄZANE Z WYSZUKIWANIEM
    SEARCH_INPUT = "input[name='q']"  # Standardowe pole wyszukiwania
    SEARCH_BUTTON = "button.ty-search-magnifier"  # Przycisk lupy
    SEARCH_RESULTS_CONTAINER = "span.ty-mainbox-title__left"  # Kontener, który się zmienia po wyszukiwaniu

    def __init__(self, page: Page):
        super().__init__(page)

        self.social_media_buttons = {
            'instagram': "a[href*='instagram.com/idream_pl']",
            'facebook': "a[href*='facebook.com/iDreamPolska']",
            'tiktok': "a[href*='tiktok.com/@idream_pl']",
            'youtube': "a[href*='youtube.com/user/iDreamPL']"
        }

        self.hamburger_icon = self.page.locator("#sw_dropdown_541 i").first
        # NOWY, POPRAWNY LOKATOR CSS dla głównych kategorii w bocznym menu:
        self.main_menu_links_locator = self.page.locator(".ut2-lfl > p > a[href]")

    # ----------------------------------------------------------------------
    # NOWE METODY DO OBSŁUGI WYSZUKIWANIA
    # ----------------------------------------------------------------------

    def perform_search(self, query: str):
        """
        Wyszukuje produkt, wpisując tekst do paska wyszukiwania i zatwierdzając.
        To naprawia błąd w test_search_bar.py.
        """
        logger.info(f"Wykonywanie wyszukiwania dla zapytania: '{query}'")
        search_input_locator = self.page.locator(self.SEARCH_INPUT)
        search_button_locator = self.page.locator(self.SEARCH_BUTTON)

        # Sprawdzenie i wpisanie tekstu
        expect(search_input_locator).to_be_visible(timeout=5000)
        search_input_locator.fill(query)

        # Kliknięcie przycisku
        search_button_locator.click()

        # Poczekaj na załadowanie nowej strony z wynikami
        self.page.wait_for_load_state("load")

    def verify_search_results_exist(self):
        """
        Weryfikuje, czy wyniki wyszukiwania są widoczne (pojawia się kontener z wynikami).
        To jest potrzebne przez test_search_bar.py.
        """
        # Po wyszukaniu strona przechodzi do widoku listy produktów.
        # Weryfikujemy, czy ten widok jest widoczny.
        products_list = self.page.locator(self.SEARCH_RESULTS_CONTAINER).get_by_text("Wyniki wyszukiwania")
        expect(products_list).to_be_visible(timeout=10000)
        logger.info("Wyniki wyszukiwania zostały poprawnie wyświetlone.")

    def click_social_media_button(self, button_type: str) -> Page:
        button_selector = self.social_media_buttons.get(button_type)
        button_locator = self.page.locator(button_selector).first
        button_locator.scroll_into_view_if_needed()
        expect(button_locator).to_be_visible(timeout=5000)
        with self.page.expect_popup() as popup_info:
            self.safe_click(button_locator)
        popup_page = popup_info.value
        popup_page.wait_for_load_state("domcontentloaded")
        return popup_page

    def get_main_menu_links(self) -> list[dict]:
        # Wracamy do zwracania listy dict, nie int
        logger.info("Test: Klika w ikonę hamburgera i zbiera główne linki menu.")

        # ... KROK 1: Kliknięcie hamburgera ...
        try:
            self.hamburger_icon.click(timeout=5000)
            logger.info("Ikona hamburgera kliknięta.")
        except Exception:
            logger.warning("Ikona hamburgera nie została znaleziona w 5s. Zakładam, że menu jest otwarte.")

        # ... KROK 2: Czekanie na widoczność menu ...
        mac_link_locator = self.page.get_by_role("link", name="Mac", exact=True).first
        try:
            expect(mac_link_locator).to_be_visible(timeout=10000)
            logger.info("Potwierdzono widoczność menu bocznego.")
        except Exception:
            logger.error("Menu boczne nie wysunęło się lub jest niewidoczne.")
            self.page.screenshot(path="error_menu_not_visible.png")
            return []

        # KROK 3: Zbieranie linków (Używamy NOWEGO, precyzyjnego lokatora)
        unique_links = {}

        # Użycie nowego lokatora, który zbiera tylko linki głównych kategorii
        all_main_category_locators = self.main_menu_links_locator.all()

        for link_locator in all_main_category_locators:
            text = (link_locator.text_content() or "").strip()
            href = link_locator.get_attribute("href")
            # Wyodrębnij tylko nazwę kategorii (Mac, iPhone, etc.)
            # Tekst ma format: "Mac\nNowoczesne laptopy..." - Bierzemy tylko pierwszą linię

            category_name = text.split('\n')[0].strip()
            # Sprawdzamy tylko, czy znaleźliśmy link z tekstem i href
            if category_name and href and href not in unique_links:
                # Normalizujemy URL
                if href.startswith('/'):
                    href = f"https://idream.pl{href}"

                unique_links[href] = {'text': category_name, 'href': href}

            # Filtrujemy, aby zbierać tylko główne linki (Mac, iPhone, iPad itd.)
            # Na podstawie HTML, główny tekst to Mac, iPhone, etc.
            if text.split('\n')[0].strip() in ["Mac", "iPhone", "iPad", "Watch", "Muzyka", "TV", "Akcesoria"]:
                # Normalizujemy URL
                if href.startswith('/'):
                    href = f"https://idream.pl{href}"
                unique_links[href] = {'text': text.split('\n')[0].strip(), 'href': href}

        links_data = list(unique_links.values())
        logger.info(f"Znaleziono {len(links_data)} głównych linków menu.")
        return links_data

    def get_social_media_expected_url(self, button_type: str) -> str:
        """
        Zwraca oczekiwany URL dla danego medium społecznościowego.
        """
        # Używamy zdefiniowanych selektorów. Musimy wydobyć sam URL z selektora.

        # 1. Pobierz selektor CSS
        selector = self.social_media_buttons.get(button_type)

        if not selector:
            raise ValueError(f"Nieznany typ przycisku społecznościowego: {button_type}")

        # 2. Wyodrębnij URL z atrybutu CSS (wszystko wewnątrz 'a[href*=...'])
        # To jest uproszczenie, bo selektor zawiera tylko część href.
        # Najlepiej jest zdefiniować oczekiwany URL jawnie.

        # PONIEWAŻ MASZ JUŻ MAPĘ LOKATORÓW, A NIE URL'I,
        # Najprościej jest dodać osobną mapę docelowych URL'i

        expected_urls = {
            'instagram': "https://www.instagram.com/idream_pl/",
            'facebook': "https://www.facebook.com/iDreamPolska/",
            'tiktok': "https://www.tiktok.com/@idream_pl",
            'youtube': "https://consent.youtube.com/m?continue=https%3A%2F%2Fwww.youtube.com%2Fuser%2FiDreamPL%3Fcbrd%3D1&gl=PL&m=0&pc=yt&cm=2&hl=pl&src=1"
        }

        # UWAGA: Upewnij się, że te URL'e są poprawne i dokładnie odpowiadają
        # temu, co otwiera Playwright (np. z 'www' lub bez 'www', ze '/' na końcu, czy bez).

        expected_url = expected_urls.get(button_type)
        if not expected_url:
            raise ValueError(f"Brak zdefiniowanego oczekiwanego URL dla: {button_type}")

        return expected_url