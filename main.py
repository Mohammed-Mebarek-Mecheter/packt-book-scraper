# main.py
import pandas as pd
import streamlit as st
import asyncio
import logging
import os
from app.scraper import BookScraper
from app.search import search_books_page
from app.visualize import visualize_data_page
from app.utils import clean_and_validate_book_data, validate_url
from streamlit_lottie import st_lottie
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
log_dir = "data/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, "scraper.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Database connection parameters
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')

# Initialize PostgreSQL connection
@st.cache_resource
def init_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            sslmode='require'
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to the database: {str(e)}")
        return None


# Set page config
st.set_page_config(page_title="Packt Book Scraper", page_icon="📚", layout="wide")

# Initialize database connection
db_conn = init_db_connection()


@st.cache_resource
def init_scraper():
    return BookScraper()


async def scrape_books(urls, db_conn):
    scraper = BookScraper(headless=True)
    results = []
    for url in urls:
        if validate_url(url):
            result = await scraper.scrape_book_details(url)
            if result:
                cleaned_result = clean_and_validate_book_data(result)
                if cleaned_result:
                    # Add the URL as a unique identifier
                    cleaned_result['url'] = url
                    results.append(cleaned_result)
                    # Check if the book already exists in the database
                    if db_conn:
                        try:
                            with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                                cur.execute("SELECT * FROM books WHERE url = %s", (url,))
                                existing_book = cur.fetchone()

                                if existing_book:
                                    # Update existing book
                                    update_query = """
                                    UPDATE books SET 
                                        title = %s, author = %s, original_price = %s, discounted_price = %s,
                                        rating = %s, num_ratings = %s, publication_date = %s, pages = %s,
                                        edition = %s, key_benefits = %s, description = %s, what_you_will_learn = %s
                                    WHERE url = %s
                                    """
                                    cur.execute(update_query, (
                                        cleaned_result['title'], cleaned_result['author'],
                                        cleaned_result['original_price'], cleaned_result['discounted_price'],
                                        cleaned_result['rating'], cleaned_result['num_ratings'],
                                        cleaned_result['publication_date'], cleaned_result['pages'],
                                        cleaned_result['edition'], json.dumps(cleaned_result['key_benefits']),
                                        cleaned_result['description'],
                                        json.dumps(cleaned_result['what_you_will_learn']),
                                        url
                                    ))
                                    db_conn.commit()
                                    logging.info(f"Book '{cleaned_result['title']}' updated in the database")
                                    st.info(f"Book '{cleaned_result['title']}' updated in the database")
                                else:
                                    # Insert new book
                                    insert_query = """
                                    INSERT INTO books (
                                        title, author, original_price, discounted_price, rating, num_ratings,
                                        publication_date, pages, edition, key_benefits, description, what_you_will_learn, url
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """
                                    cur.execute(insert_query, (
                                        cleaned_result['title'], cleaned_result['author'],
                                        cleaned_result['original_price'], cleaned_result['discounted_price'],
                                        cleaned_result['rating'], cleaned_result['num_ratings'],
                                        cleaned_result['publication_date'], cleaned_result['pages'],
                                        cleaned_result['edition'], json.dumps(cleaned_result['key_benefits']),
                                        cleaned_result['description'],
                                        json.dumps(cleaned_result['what_you_will_learn']),
                                        url
                                    ))
                                    db_conn.commit()
                                    logging.info(f"Book '{cleaned_result['title']}' stored in the database")
                                    st.success(f"Book '{cleaned_result['title']}' stored in the database")
                        except Exception as e:
                            logging.error(
                                f"Failed to store/update book '{cleaned_result['title']}' in the database: {str(e)}")
                            st.error(
                                f"Failed to store/update book '{cleaned_result['title']}' in the database. Error: {str(e)}")
        else:
            logging.warning(f"Invalid URL: {url}")
    return results


def update_export_files(db_conn):
    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM books")
            results = cur.fetchall()

        df = pd.DataFrame(results)

        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)

        # Update CSV file
        df.to_csv('data/scraped_books.csv', index=False)
        logging.info("CSV file updated successfully")

        # Update JSON file
        df.to_json('data/scraped_books.json', orient='records')
        logging.info("JSON file updated successfully")

    except Exception as e:
        logging.error(f"Failed to update export files: {str(e)}")
        st.error(f"Failed to update export files. Error: {str(e)}")

def load_css():
    """Function to load the custom CSS for styling."""
    css_file_path = "app/assets/style.css"
    try:
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {css_file_path}")


def load_lottie_file(filepath: str):
    """Function to load a Lottie animation from a JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Lottie file not found: {filepath}")
        return None


def sidebar_lottie_animations():
    """Load and display Lottie animations for GitHub, LinkedIn, and Portfolio in the sidebar."""
    # Paths to Lottie JSON files
    lottie_github_path = "app/assets/images/github.json"
    lottie_linkedin_path = "app/assets/images/linkedin.json"
    lottie_portfolio_path = "app/assets/images/profile.json"

    # Load Lottie animations
    lottie_github = load_lottie_file(lottie_github_path)
    lottie_linkedin = load_lottie_file(lottie_linkedin_path)
    lottie_portfolio = load_lottie_file(lottie_portfolio_path)

    # Sidebar Lottie Animations with Links
    with st.sidebar:
        st.markdown("### Connect with me")

        # GitHub
        col1, col2 = st.columns([1, 3])
        with col1:
            st_lottie(lottie_github, height=30, width=30, key="lottie_github_sidebar")
        with col2:
            st.markdown("<a href='https://github.com/Mohammed-Mebarek-Mecheter/' target='_blank'>GitHub</a>", unsafe_allow_html=True)

        # LinkedIn
        col1, col2 = st.columns([1, 3])
        with col1:
            st_lottie(lottie_linkedin, height=30, width=30, key="lottie_linkedin_sidebar")
        with col2:
            st.markdown("<a href='https://www.linkedin.com/in/mohammed-mecheter/' target='_blank'>LinkedIn</a>", unsafe_allow_html=True)

        # Portfolio
        col1, col2 = st.columns([1, 3])
        with col1:
            st_lottie(lottie_portfolio, height=30, width=30, key="lottie_portfolio_sidebar")
        with col2:
            st.markdown("<a href='https://mebarek.pages.dev/' target='_blank'>Portfolio</a>", unsafe_allow_html=True)


def scrape_books_page():

    # Packt Publishing link
    st.markdown(
        """
        <a href="https://www.packtpub.com/en-us" target="_blank" class="packt-link">
            <button style="background-color:#ff642b; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer;">
                Visit Packt Publishing
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    # URL Input
    url_input = st.text_area("Enter book URLs (one per line):")

    urls = []

    if url_input:
        urls = [url.strip() for url in url_input.splitlines() if url.strip()]
    else:
        st.warning("Please enter URLs.")

    # Progress feedback
    progress_bar = st.progress(0)
    status_text = st.empty()

    if st.button("Scrape Books") and urls:
        with st.spinner('Scraping in progress...'):
            results = asyncio.run(scrape_books(urls, db_conn))
            total_urls = len(urls)

            for i, result in enumerate(results):
                st.write(result)

                progress = (i + 1) / total_urls
                progress_bar.progress(progress)
                status_text.text(f"Scraping {i + 1}/{total_urls} URLs")

        st.success("Scraping completed!")
        status_text.text("Scraping finished.")

def main():
    load_css()

    # Header with icon and title
    st.markdown(
        """
        <div class="header-container">
            <span class="book-icon">📚</span>
            <h1>Packt Book Scraper</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Scrape Books", "Search Books", "Visualize Data"])

    sidebar_lottie_animations()  # Display sidebar Lottie animations

    if page == "Scrape Books":
        scrape_books_page()
    elif page == "Search Books":
        search_books_page(db_conn)
    elif page == "Visualize Data":
        visualize_data_page(db_conn)

if __name__ == "__main__":
    main()