import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class LoginPage(BasePage):

    LOGIN_URL = "https://idream.pl/profil.html"

    def __init__(self, page: Page):
        super().__init__(page)
        # Locators
        self.email_input = self.page.locator("#login_main_login")
        self.password_input = self.page.locator("#psw_main_login")
        self.login_button = self.page.locator("form[name='main_login_form'] div[class='buttons-container clearfix'] button[name='dispatch[auth.login]']")
        self.success_message = self.page.locator("text=Użytkownik został poprawnie zalogowany")

    def navigate_to_login_page(self):
        """Nawiguje bezpośrednio do strony profilu/logowania."""
        logger.info(f"Navigating directly to the login page: {self.LOGIN_URL}...")
        self.page.goto(self.LOGIN_URL)
        # Czekamy na załadowanie strony i widoczność pola email
        expect(self.email_input).to_be_visible(timeout=10000)
        logger.info("Login page is loaded and ready.")

    def login(self, email: str, password: str):
        """Wypełnia formularz logowania i klika przycisk 'Zaloguj się'."""
        logger.info(f"Attempting to log in as {email}...")
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.safe_click(self.login_button)

    def assert_login_is_successful(self):
        """Sprawdza, czy po zalogowaniu pojawił się komunikat o sukcesie."""
        logger.info("Verifying login success message...")
        expect(self.success_message).to_be_visible(timeout=10000)
        logger.info("✅ Login successful!")