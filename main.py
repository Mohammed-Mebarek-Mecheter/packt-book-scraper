# main.py
import base64
import streamlit as st
from st_supabase_connection import SupabaseConnection
import asyncio
import pandas as pd
import logging
import os
from app.scraper import BookScraper
from app.utils import clean_and_validate_book_data, validate_url
import plotly.express as px
from streamlit_lottie import st_lottie
import json

# Set up logging
log_dir = "data/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, "scraper.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Supabase connection
st.set_page_config(page_title="Packt Book Scraper", page_icon="📚", layout="wide")

# Initialize Supabase connection with error handling
try:
    supabase_conn = st.connection('supabase', type=SupabaseConnection)
except Exception as e:
    st.error(f"Failed to connect to Supabase: {str(e)}")
    supabase_conn = None


@st.cache_resource
def init_scraper():
    return BookScraper()


async def scrape_books(urls, supabase_conn):
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
                    # Check if the book already exists in Supabase
                    if supabase_conn:
                        try:
                            existing_book_response = supabase_conn.table('books').select('*').eq('url', url).execute()
                            existing_book = existing_book_response.data

                            if existing_book:
                                # Update existing book
                                update_response = supabase_conn.table('books').update(cleaned_result).eq('url',
                                                                                                         url).execute()
                                if update_response.error is None:  # Check for successful update
                                    logging.info(f"Book '{cleaned_result['title']}' updated in Supabase")
                                    st.info(f"Book '{cleaned_result['title']}' updated in Supabase")
                                else:
                                    logging.error(
                                        f"Failed to update book '{cleaned_result['title']}' in Supabase: {update_response.error}")
                                    st.error(
                                        f"Failed to update book '{cleaned_result['title']}' in Supabase. Error: {update_response.error}")
                            else:
                                # Insert new book
                                insert_response = supabase_conn.table('books').insert(cleaned_result).execute()
                                if insert_response.error is None:  # Check for successful insertion
                                    logging.info(f"Book '{cleaned_result['title']}' stored in Supabase")
                                    st.success(f"Book '{cleaned_result['title']}' stored in Supabase")
                                else:
                                    logging.error(
                                        f"Failed to store book '{cleaned_result['title']}' in Supabase: {insert_response.error}")
                                    st.error(
                                        f"Failed to store book '{cleaned_result['title']}' in Supabase. Error: {insert_response.error}")
                        except Exception as e:
                            logging.error(
                                f"Failed to store/update book '{cleaned_result['title']}' in Supabase: {str(e)}")
                            st.error(
                                f"Failed to store/update book '{cleaned_result['title']}' in Supabase. Error: {str(e)}")
        else:
            logging.warning(f"Invalid URL: {url}")
    return results


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


def main():
    st.title("📚 Packt Book Scraper")
    st.write("Enter Packt book URLs to scrape and manage the data.")

    load_css()

    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Scrape Books", "Search Books", "Visualize Data"])

    sidebar_lottie_animations()  # Display sidebar Lottie animations

    if page == "Scrape Books":
        scrape_books_page()
    elif page == "Search Books":
        search_books_page()
    elif page == "Visualize Data":
        visualize_data_page()


def scrape_books_page():
    st.header("Scrape Books")

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
            results = asyncio.run(scrape_books(urls, supabase_conn))
            total_urls = len(urls)

            for i, result in enumerate(results):
                st.write(result)

                progress = (i + 1) / total_urls
                progress_bar.progress(progress)
                status_text.text(f"Scraping {i + 1}/{total_urls} URLs")

        st.success("Scraping completed!")
        status_text.text("Scraping finished.")


def search_books_page():
    st.header("Search Books")
    search_term = st.text_input("Enter book title, author, or keyword:")

    if supabase_conn:
        try:
            if search_term:
                results = supabase_conn.table('books').select('*').or_(
                    f"title.ilike.%{search_term}%,author.ilike.%{search_term}%,description.ilike.%{search_term}%"
                ).execute()
            else:
                results = supabase_conn.table('books').select('*').execute()

            matches = results.data if results else []

            if matches:
                st.write(f"Found {len(matches)} matching books:")
                df = pd.DataFrame(matches)

                # Display using Streamlit's built-in table
                st.dataframe(
                    df,
                    column_config={
                        "title": st.column_config.TextColumn("Title", width="medium"),
                        "author": st.column_config.TextColumn("Author", width="medium"),
                        "original_price": st.column_config.TextColumn("Original Price", width="small"),
                        "discounted_price": st.column_config.TextColumn("Discounted Price", width="small"),
                        "rating": st.column_config.NumberColumn("Rating", format="%.1f", width="small"),
                        "num_ratings": st.column_config.NumberColumn("Number of Ratings", width="small"),
                        "publication_date": st.column_config.DateColumn("Publication Date", width="medium"),
                        "pages": st.column_config.NumberColumn("Pages", width="small"),
                        "edition": st.column_config.TextColumn("Edition", width="small"),
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # Export options
                st.subheader("Export Results")
                export_format = st.selectbox("Select Export Format", ["CSV", "JSON"], key="export_format")

                # Define the export_data function
                def export_data(df, format):
                    if format == "CSV":
                        csv = df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="scraped_books.csv">Download CSV File</a>'
                        return href
                    elif format == "JSON":
                        json = df.to_json(orient='records')
                        b64 = base64.b64encode(json.encode()).decode()
                        href = f'<a href="data:file/json;base64,{b64}" download="scraped_books.json">Download JSON File</a>'
                        return href

                # In the search_books_page function, replace the existing export code with:
                if st.button("Export"):
                    if export_format == "CSV":
                        download_link = export_data(df, "CSV")
                        st.markdown(download_link, unsafe_allow_html=True)
                    elif export_format == "JSON":
                        download_link = export_data(df, "JSON")
                        st.markdown(download_link, unsafe_allow_html=True)
            else:
                st.info("No matches found.")
        except Exception as e:
            st.error(f"Error querying the database: {str(e)}")
    else:
        st.error("Database connection is not available. Please check your Supabase connection.")


def visualize_data_page():
    st.header("Data Visualization")

    if supabase_conn:
        try:
            results = supabase_conn.table('books').select('*').execute()
            df = pd.DataFrame(results.data)

            if not df.empty:
                # Price Distribution
                st.subheader("Price Distribution")
                fig = px.histogram(df, x="discounted_price", nbins=20, title="Distribution of Book Prices")
                st.plotly_chart(fig)

                # Top Authors
                st.subheader("Top Authors")
                top_authors = df['author'].value_counts().head(10)
                fig = px.bar(top_authors, x=top_authors.index, y=top_authors.values,
                             title="Top 10 Authors by Number of Books")
                st.plotly_chart(fig)

                # Ratings Distribution
                st.subheader("Ratings Distribution")
                fig = px.histogram(df, x="rating", nbins=10, title="Distribution of Book Ratings")
                st.plotly_chart(fig)

            else:
                st.info("No data available for visualization. Please scrape some books first.")
        except Exception as e:
            st.error(f"Error retrieving data for visualization: {str(e)}")
    else:
        st.error("Database connection is not available. Please check your Supabase connection.")

if __name__ == "__main__":
    main()