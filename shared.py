# shared.py
import streamlit as st
import logging
import asyncio
from app.scraper import BookScraper
from app.utils import clean_and_validate_book_data, validate_url

# Supabase connection is initialized here for reuse across different modules
def initialize_supabase():
    try:
        return st.connection('supabase', type='SupabaseConnection')
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {str(e)}")
        return None

# Async function to scrape books and store in Supabase
async def scrape_books(urls, supabase_conn):
    scraper = BookScraper(headless=True)
    tasks = [scraper.scrape_book_details(url) for url in urls if validate_url(url)]
    results = await asyncio.gather(*tasks)

    cleaned_results = [clean_and_validate_book_data(result) for result in results if result]
    for cleaned_result in cleaned_results:
        try:
            if supabase_conn:
                supabase_conn.table('books').insert(cleaned_result).execute()
                logging.info(f"Book '{cleaned_result['title']}' stored in Supabase")
        except Exception as e:
            logging.error(f"Failed to store book in Supabase: {str(e)}")
            st.error(f"Failed to store book in Supabase: {str(e)}")
    return cleaned_results
