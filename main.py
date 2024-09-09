# main.py
import asyncio
import streamlit as st
from st_supabase_connection import SupabaseConnection  # Correct import for Supabase connection
import pandas as pd
import logging
import os
from auth.auth import authenticate_user
from scheduler.task_scheduler import schedule_scraping_page
from shared import scrape_books
import plotly.express as px
import st_aggrid as ag

# Set up logging
log_dir = "data/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, "scraper.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Supabase connection using the st_supabase_connection library
def initialize_supabase():
    try:
        return st.connection("supabase", type=SupabaseConnection)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {str(e)}")
        return None

# Initialize connection
supabase_conn = initialize_supabase()

def main():
    st.title("📚 Packt Book Scraper")

    # Authenticate user (login/register/demo)
    authenticate_user(supabase_conn)

    if not st.session_state.get('authenticated'):
        return  # Do not proceed if the user is not authenticated

    # Check if the user is in demo mode
    if st.session_state.get('is_demo'):
        st.info("You are currently using the demo account. After exploring, feel free to register for a full account!")

    # Sidebar navigation
    page = st.sidebar.selectbox("Choose a page", ["Scrape Books", "Search Books", "Visualize Data", "Schedule Scraping", "Account"])

    if page == "Scrape Books":
        scrape_books_page()
    elif page == "Search Books":
        search_books_page()
    elif page == "Visualize Data":
        visualize_data_page()
    elif page == "Schedule Scraping":
        schedule_scraping_page(supabase_conn)  # Pass Supabase connection
    elif page == "Account":
        account_page()

def scrape_books_page():
    st.header("Scrape Books")

    if st.session_state.get('is_demo'):
        st.warning("Scraping is disabled for the demo account. Please register to use this feature.")
        return

    url_input = st.text_area("Enter book URLs (one per line):")
    urls = [url.strip() for url in url_input.splitlines() if url.strip()]

    if st.button("Scrape Books") and urls:
        with st.spinner('Scraping in progress...'):
            results = asyncio.run(scrape_books(urls, supabase_conn))  # Correct usage of Supabase connection
            for result in results:
                st.write(result)

        st.success("Scraping completed!")

def search_books_page():
    st.header("Search Books")
    search_term = st.text_input("Enter book title, author, or keyword:")

    if supabase_conn:
        try:
            query = supabase_conn.query("*", table="books", ttl="10m")
            if search_term:
                query = query.or_(f"title.ilike.%{search_term}%,author.ilike.%{search_term}%")
            results = query.execute()
            matches = results.data if results else []

            if matches:
                st.write(f"Found {len(matches)} matching books:")
                df = pd.DataFrame(matches)

                # Display using AG Grid
                grid_options = ag.GridOptionsBuilder.from_dataframe(df)
                grid_options.configure_pagination(paginationAutoPageSize=True)
                grid_options.configure_side_bar()
                grid_options.configure_column("title", editable=True)
                ag.grid(df, grid_options.build(), allow_unsafe_jscode=True)

                # Export option
                st.subheader("Export Results")
                export_format = st.selectbox("Select Export Format", ["CSV", "JSON"])
                if st.button("Export"):
                    if export_format == "CSV":
                        df.to_csv('data/scraped_books.csv', index=False)
                        st.success("Results exported to CSV")
                    elif export_format == "JSON":
                        df.to_json('data/scraped_books.json', orient='records', indent=4)
                        st.success("Results exported to JSON")
            else:
                st.info("No matches found.")
        except Exception as e:
            st.error(f"Error querying the database: {str(e)}")

def visualize_data_page():
    st.header("Data Visualization")

    if supabase_conn:
        try:
            results = supabase_conn.query("*", table="books", ttl="10m").execute()
            df = pd.DataFrame(results.data)

            if not df.empty:
                # Price Distribution
                st.subheader("Price Distribution")
                fig = px.histogram(df, x="discounted_price", nbins=20, title="Distribution of Book Prices")
                st.plotly_chart(fig)

                # Top Authors
                st.subheader("Top Authors")
                top_authors = df['author'].value_counts().head(10)
                fig = px.bar(top_authors, x=top_authors.index, y=top_authors.values, title="Top 10 Authors by Number of Books")
                st.plotly_chart(fig)

                # Ratings Distribution
                st.subheader("Ratings Distribution")
                fig = px.histogram(df, x="rating", nbins=10, title="Distribution of Book Ratings")
                st.plotly_chart(fig)
            else:
                st.info("No data available for visualization. Please scrape some books first.")
        except Exception as e:
            st.error(f"Error retrieving data for visualization: {str(e)}")

def account_page():
    st.header("Account Settings")
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.is_demo = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
