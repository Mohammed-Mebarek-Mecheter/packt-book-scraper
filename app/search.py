# search.py
import streamlit as st
import pandas as pd
import base64
import os
from psycopg2.extras import RealDictCursor


def search_books_page(db_conn):
    search_term = st.text_input("Enter book title, author, or keyword:")

    if db_conn:
        try:
            with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                if search_term:
                    query = """
                    SELECT title, author, original_price, discounted_price, rating, num_ratings, publication_date, pages, edition
                    FROM books
                    WHERE title ILIKE %s OR author ILIKE %s OR description ILIKE %s
                    """
                    cur.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
                else:
                    query = """
                    SELECT title, author, original_price, discounted_price, rating, num_ratings, publication_date, pages, edition
                    FROM books
                    """
                    cur.execute(query)

                matches = cur.fetchall()

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

                if st.button("Export"):
                    if export_format == "CSV":
                        csv = df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="search_results.csv">Download CSV File</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    elif export_format == "JSON":
                        json = df.to_json(orient='records')
                        b64 = base64.b64encode(json.encode()).decode()
                        href = f'<a href="data:file/json;base64,{b64}" download="search_results.json">Download JSON File</a>'
                        st.markdown(href, unsafe_allow_html=True)
            else:
                st.info("No matches found.")
        except Exception as e:
            st.error(f"Error querying the database: {str(e)}")
    else:
        st.error("Database connection is not available. Please check your database connection.")