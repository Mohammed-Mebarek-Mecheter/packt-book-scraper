# visualize.py
import streamlit as st
import pandas as pd
import plotly.express as px
from psycopg2.extras import RealDictCursor


def visualize_data_page(db_conn):
    if db_conn:
        try:
            with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Fetch all books from the database
                cur.execute("SELECT * FROM books")
                results = cur.fetchall()

            df = pd.DataFrame(results)

            if not df.empty:
                # Price Distribution
                fig = px.histogram(df, x="discounted_price", nbins=20, title="Distribution of Book Prices")
                st.plotly_chart(fig)

                # Top Authors
                top_authors = df['author'].value_counts().head(10)
                fig = px.bar(top_authors, x=top_authors.index, y=top_authors.values,
                             title="Top 10 Authors by Number of Books")
                st.plotly_chart(fig)

                # Ratings Distribution
                fig = px.histogram(df, x="rating", nbins=10, title="Distribution of Book Ratings")
                st.plotly_chart(fig)

                # Publication Date Timeline
                df['publication_date'] = pd.to_datetime(df['publication_date'])
                fig = px.scatter(df, x="publication_date", y="rating",
                                 hover_data=["title", "author"],
                                 title="Book Ratings Over Time")
                st.plotly_chart(fig)

                # New visualization: Average Price by Rating
                avg_price_by_rating = df.groupby('rating')['discounted_price'].mean().reset_index()
                fig = px.bar(avg_price_by_rating, x='rating', y='discounted_price',
                             title="Average Discounted Price by Rating")
                st.plotly_chart(fig)

                # New visualization: Number of Books by Page Count Range
                df['page_range'] = pd.cut(df['pages'], bins=[0, 100, 200, 300, 400, 500, float('inf')],
                                          labels=['0-100', '101-200', '201-300', '301-400', '401-500', '500+'])
                books_by_page_range = df['page_range'].value_counts().sort_index()
                fig = px.bar(x=books_by_page_range.index, y=books_by_page_range.values,
                             title="Number of Books by Page Count Range")
                fig.update_xaxes(title="Page Range")
                fig.update_yaxes(title="Number of Books")
                st.plotly_chart(fig)

            else:
                st.info("No data available for visualization. Please scrape some books first.")
        except Exception as e:
            st.error(f"Error retrieving data for visualization: {str(e)}")
    else:
        st.error("Database connection is not available. Please check your database connection.")