#
# OSTATECZNA, GWARANTOWANA I NIEZAWODNA WERSJA PLIKU: pages/home_page.py
#
import logging
import pytest
from playwright.sync_api import Page, expect, TimeoutError
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.social_media_buttons = {
            'instagram': "a[href*='instagram.com/idream_pl']",
            'facebook': "a[href*='facebook.com/iDreamPolska']",
            'tiktok': "a[href*='tiktok.com/@idream_pl']",
            'youtube': "a[href*='youtube.com/user/iDreamPL']"
        }

        self.main_menu_triggers = self.page.locator("div.main-menu__item")
        self.submenu_content_holder = self.page.locator("div.submenu-holder")

    def click_social_media_button(self, button_type: str) -> Page:
        # This method is correct.
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
        """
        OSTATECZNA, NIEZAWODNA WERSJA:
        Precyzyjnie symuluje najechanie, a następnie czeka na pojawienie się
        KONKRETNEJ treści powiązanej z tym najechaniem, eliminując race conditions.
        """
        logger.info("Starting definitive link extraction with race condition elimination...")

        try:
            expect(self.page.locator("div.homepage-banners")).to_be_visible(timeout=15000)
            logger.info("Homepage banners are visible. Page is ready for interaction.")
        except TimeoutError:
            self.page.screenshot(path="error_banners_not_found.png")
            pytest.fail("Strona nie załadowała banerów. Nie można kontynuować.")

        unique_links = {}
        all_triggers = self.main_menu_triggers.all()
        logger.info(f"Found {len(all_triggers)} menu triggers to scan.")

        for trigger in all_triggers:
            # We must get the category text first, as it's our key for waiting.
            category_link = trigger.locator("a").first
            category_text = (category_link.text_content() or "Unknown").strip()

            if "has-submenu" not in (trigger.get_attribute("class") or ""):
                logger.info(f"--- Skipping category '{category_text}' (no submenu). ---")
                continue

            try:
                logger.info(f"--- Processing category: '{category_text}' ---")

                # KROK 1: Najeżdżamy na trigger
                trigger.hover()

                # KROK 2 (KLUCZOWY): CZEKAMY NA BEZPOŚREDNI EFEKT NASZEJ AKCJI
                # Czekamy, aż w kontenerze pojawi się nagłówek z tekstem kategorii.
                # To jest nasz 100% niezawodny sygnał, że treść została podmieniona.
                specific_submenu_title = self.submenu_content_holder.get_by_role(
                    "heading", name=category_text, exact=True
                )
                expect(specific_submenu_title).to_be_visible(timeout=5000)
                logger.info(f"Content for '{category_text}' confirmed visible in submenu holder.")

                # KROK 3: Teraz bezpiecznie zbieramy linki z w pełni załadowanego kontenera
                links_in_holder = self.submenu_content_holder.get_by_role("link").all()

                for link_locator in links_in_holder:
                    text = (link_locator.text_content() or "").strip()
                    href = link_locator.get_attribute("href")
                    if text and href and href not in unique_links:
                        if href.startswith('/'):
                            href = f"https://idream.pl{href}"
                        unique_links[href] = {'text': text, 'href': href}

                logger.info(f"Collected {len(links_in_holder)} links from '{category_text}' submenu.")

            except TimeoutError:
                logger.warning(f"Timeout: Content for '{category_text}' did not appear after hover.")
                self.page.screenshot(path=f"error_hover_{category_text}.png")
            except Exception as e:
                logger.error(f"An unexpected error occurred processing '{category_text}': {e}")

        links_data = list(unique_links.values())
        if not links_data:
            self.page.screenshot(path="error_no_links_found_at_all.png")
        logger.info(f"Total unique links found across all menus: {len(links_data)}")
        return links_data