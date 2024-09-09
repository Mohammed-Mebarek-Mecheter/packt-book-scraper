# task_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from shared import scrape_books  # Import scrape_books from shared module
import asyncio
import streamlit as st

# Function to fetch URLs for scheduled scraping
def fetch_urls_to_scrape():
    # You can fetch URLs from the database or other sources
    urls = [
        "https://www.packtpub.com/en-us/product/mastering-tableau-2023-9781803233765",
        "https://www.packtpub.com/en-us/product/practical-mongodb-aggregations-9781835080641"
    ]
    return urls

def schedule_scraping_page(supabase_conn):
    st.write("Schedule scraping tasks")

    if st.button("Start Scheduled Scraping"):
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: asyncio.run(scheduled_scraping(supabase_conn)), 'interval', days=1)
        scheduler.start()
        st.success("Scheduled scraping started!")

def scheduled_scraping(supabase_conn):
    urls = fetch_urls_to_scrape()
    asyncio.run(scrape_books(urls, supabase_conn))  # Use scrape_books from shared.py

