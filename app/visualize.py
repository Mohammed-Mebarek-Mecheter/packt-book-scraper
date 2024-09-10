# visualize.py
import streamlit as st
import pandas as pd
import plotly.express as px

def visualize_data_page(supabase_conn):

    if supabase_conn:
        try:
            results = supabase_conn.table('books').select('*').execute()
            df = pd.DataFrame(results.data)

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

            else:
                st.info("No data available for visualization. Please scrape some books first.")
        except Exception as e:
            st.error(f"Error retrieving data for visualization: {str(e)}")
    else:
        st.error("Database connection is not available. Please check your Supabase connection.")