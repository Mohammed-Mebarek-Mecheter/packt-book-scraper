import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import logging
from contextlib import asynccontextmanager

class BookScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def get_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        if self.headless:
            options.add_argument("--headless")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Hide webdriver property
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        try:
            yield driver
        finally:
            driver.quit()

    async def scrape_book_details(self, book_url, max_retries=3):
        for attempt in range(max_retries):
            try:
                async with self.get_driver() as driver:
                    driver.set_page_load_timeout(30)
                    await asyncio.sleep(2)
                    driver.get(book_url)
                    await asyncio.sleep(5)
                    book_details = await self._extract_book_details(driver)
                    return book_details
            except WebDriverException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {book_url}: {str(e)}")
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to scrape {book_url} after {max_retries} attempts")
                    return None
                await asyncio.sleep(2)

    async def _extract_book_details(self, driver):
        book_details = {}

        # Extract Title
        book_details['title'] = self._safe_get_text(driver, (By.CLASS_NAME, 'product-title'))

        # Extract Author
        authors = self._safe_get_elements(driver, (By.XPATH, "//div[contains(@class, 'authors desktop')]/span[not(@class)]"))
        book_details['author'] = ", ".join([author.text.strip() for author in authors]) if authors else "Author not found"

        # Extract Prices
        price_element = self._safe_get_element(driver, (By.CLASS_NAME, 'product-details-price'))
        if price_element:
            book_details['original_price'] = self._safe_get_text(price_element, (By.TAG_NAME, 'del'))
            book_details['discounted_price'] = self._safe_get_text(price_element, (By.XPATH, ".//span[contains(@class, 'fw-600')]"))
        else:
            book_details['original_price'] = book_details['discounted_price'] = "Price not found"

        # Extract Rating and Number of Ratings
        book_details['rating'] = self._safe_get_text(driver, (By.CLASS_NAME, 'star-rating-total-rating-medium'))
        book_details['num_ratings'] = self._safe_get_text(driver, (By.CLASS_NAME, 'star-rating-total-count'))

        return book_details

    def _safe_get_element(self, driver, locator, timeout=10):
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            self.logger.warning(f"Element not found: {locator}")
            return None

    def _safe_get_elements(self, driver, locator, timeout=10):
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            self.logger.warning(f"Elements not found: {locator}")
            return []

    def _safe_get_text(self, driver, locator, timeout=10):
        element = self._safe_get_element(driver, locator, timeout)
        return element.text if element else "Not found"

    async def scrape_multiple_books(self, book_urls):
        tasks = [self.scrape_book_details(url) for url in book_urls]
        return await asyncio.gather(*tasks)
