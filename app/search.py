# search.py
import streamlit as st
import pandas as pd
import base64
import os

def search_books_page(supabase_conn):
    search_term = st.text_input("Enter book title, author, or keyword:")

    if supabase_conn:
        try:
            if search_term:
                results = supabase_conn.table('books').select(
                    'title', 'author', 'original_price', 'discounted_price', 'rating', 'num_ratings', 'publication_date', 'pages', 'edition'
                ).or_(
                    f"title.ilike.%{search_term}%,author.ilike.%{search_term}%,description.ilike.%{search_term}%"
                ).execute()
            else:
                results = supabase_conn.table('books').select(
                    'title', 'author', 'original_price', 'discounted_price', 'rating', 'num_ratings', 'publication_date', 'pages', 'edition'
                ).execute()

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

                # Fetch all columns for export
                all_columns_results = supabase_conn.table('books').select('*').execute()
                all_columns_df = pd.DataFrame(all_columns_results.data)

                # Export options
                st.subheader("Export Results")
                export_format = st.selectbox("Select Export Format", ["CSV", "JSON"], key="export_format")

                if st.button("Export"):
                    if export_format == "CSV":
                        csv = all_columns_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="search_results.csv">Download CSV File</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    elif export_format == "JSON":
                        json = all_columns_df.to_json(orient='records')
                        b64 = base64.b64encode(json.encode()).decode()
                        href = f'<a href="data:file/json;base64,{b64}" download="search_results.json">Download JSON File</a>'
                        st.markdown(href, unsafe_allow_html=True)
            else:
                st.info("No matches found.")
        except Exception as e:
            st.error(f"Error querying the database: {str(e)}")
    else:
        st.error("Database connection is not available. Please check your Supabase connection.")

