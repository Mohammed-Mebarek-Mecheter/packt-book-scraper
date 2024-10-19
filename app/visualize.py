# visualize.py
import streamlit as st
import pandas as pd
import plotly.express as px
from psycopg2.extras import RealDictCursor


def preprocess_data(df):
    # Convert discounted_price to numeric
    df['discounted_price'] = pd.to_numeric(df['discounted_price'].str.replace('$', '').str.replace(',', ''),
                                           errors='coerce')

    # Convert publication_date to datetime
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')

    # Convert rating to numeric
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    # Convert pages to numeric
    df['pages'] = pd.to_numeric(df['pages'], errors='coerce')

    return df


def visualize_data_page(db_conn):
    if db_conn:
        try:
            with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Fetch all books from the database
                cur.execute("SELECT * FROM books")
                results = cur.fetchall()

            df = pd.DataFrame(results)
            df = preprocess_data(df)

            if not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    # Price Distribution
                    fig = px.histogram(df, x="discounted_price", nbins=20, title="Distribution of Book Prices")
                    fig.update_xaxes(title="Price ($)")
                    fig.update_yaxes(title="Number of Books")
                    st.plotly_chart(fig)

                with col2:
                    # Ratings Distribution
                    fig = px.histogram(df, x="rating", nbins=10, title="Distribution of Book Ratings")
                    fig.update_xaxes(title="Rating")
                    fig.update_yaxes(title="Number of Books")
                    st.plotly_chart(fig)

                col1, col2 = st.columns(2)
                with col1:
                    # Publication Date Timeline
                    fig = px.scatter(df, x="publication_date", y="rating", title="Book Ratings Over Time")
                    fig.update_xaxes(title="Publication Date")
                    fig.update_yaxes(title="Rating")
                    st.plotly_chart(fig)

                with col2:
                    # Average Price by Rating
                    avg_price_by_rating = df.groupby('rating')['discounted_price'].mean().reset_index()
                    fig = px.bar(avg_price_by_rating, x='rating', y='discounted_price',
                                 title="Average Discounted Price by Rating")
                    fig.update_xaxes(title="Rating")
                    fig.update_yaxes(title="Average Price ($)")
                    st.plotly_chart(fig)

                # Price vs. Number of Pages
                fig = px.scatter(df, x="pages", y="discounted_price", title="Price vs. Number of Pages")
                fig.update_xaxes(title="Number of Pages")
                fig.update_yaxes(title="Price ($)")
                st.plotly_chart(fig)

            else:
                st.info("No data available for visualization. Please scrape some books first.")
        except Exception as e:
            st.error(f"Error retrieving data for visualization: {str(e)}")
    else:
        st.error("Database connection is not available. Please check your database connection.")