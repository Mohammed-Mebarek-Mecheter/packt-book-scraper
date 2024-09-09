import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
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
                    book_details['url'] = book_url  # Add URL to book details
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
        book_details['title'] = self._safe_get_text(driver, (By.CLASS_NAME, 'product-title')) or "Title not found"

        # Extract Author
        authors = self._safe_get_elements(driver, (By.XPATH, "//div[contains(@class, 'authors')]/span[not(@class)]"))
        if authors:
            author_names = [author.text.strip() for author in authors]
            book_details['author'] = ", ".join(filter(None, author_names))
        else:
            book_details['author'] = "Author not found"

        # Extract Prices
        price_element = self._safe_get_element(driver, (By.CLASS_NAME, 'product-details-price'))
        if price_element:
            book_details['original_price'] = self._safe_get_text(price_element,
                                                                 (By.TAG_NAME, 'del')) or "Original price not found"
            book_details['discounted_price'] = self._safe_get_text(price_element, (
            By.XPATH, ".//span[contains(@class, 'fw-600')]")) or "Discounted price not found"
        else:
            book_details['original_price'] = book_details['discounted_price'] = "Price not found"

        # Extract Rating
        rating_element = self._safe_get_element(driver, (By.CLASS_NAME, 'star-rating-total-rating-medium'))
        book_details['rating'] = rating_element.text if rating_element else "Rating not found"

        # Extract Number of Ratings
        num_ratings_element = self._safe_get_element(driver, (By.CLASS_NAME, 'star-rating-total-count'))
        if num_ratings_element:
            num_ratings_text = num_ratings_element.text.strip('()')
            book_details['num_ratings'] = num_ratings_text if num_ratings_text else "0"
        else:
            book_details['num_ratings'] = "0"

        # Extract additional details
        meta_info = self._safe_get_element(driver, (By.CLASS_NAME, 'product-meta.product-details-information'))
        if meta_info:
            meta_items = meta_info.find_elements(By.TAG_NAME, 'span')
            for item in meta_items:
                text = item.text.strip()
                if 'pages' in text.lower():
                    book_details['pages'] = text.split()[0]
                elif 'edition' in text.lower():
                    book_details['edition'] = text
                elif any(month in text for month in
                         ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    book_details['publication_date'] = text

        # Set default values if not found
        book_details.setdefault('pages', "Pages not specified")
        book_details.setdefault('edition', "Edition not specified")
        book_details.setdefault('publication_date', "Publication date not found")

        # Extract Key Benefits
        key_benefits = self._safe_get_elements(driver, (
        By.XPATH, "//h2[contains(text(), 'Key benefits')]/following-sibling::ul[1]/li"))
        book_details['key_benefits'] = [benefit.text for benefit in key_benefits] if key_benefits else [
            "No key benefits found"]

        # Extract Description
        book_details['description'] = self._safe_get_text(driver, (
        By.XPATH, "//h2[contains(text(), 'Description')]/following-sibling::div[1]")) or "Description not found"

        # Extract What You Will Learn
        what_you_will_learn = self._safe_get_elements(driver, (
        By.XPATH, "//h2[contains(text(), 'What you will learn')]/following-sibling::ul[1]/li"))
        book_details['what_you_will_learn'] = [item.text for item in what_you_will_learn] if what_you_will_learn else [
            "No information found"]

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
        return element.text.strip() if element else "Not found"

    async def scrape_multiple_books(self, book_urls):
        tasks = [self.scrape_book_details(url) for url in book_urls]
        return await asyncio.gather(*tasks)