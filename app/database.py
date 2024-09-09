# database.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

class SupabaseDB:
    def __init__(self):
        load_dotenv()
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        logging.info("Connected to Supabase")

    def is_connected(self):
        try:
            self.supabase.table('books').select('*').limit(1).execute()
            return True
        except Exception as e:
            logging.error(f"Connection test failed: {str(e)}")
            return False

    def create_book(self, book_data):
        try:
            result = self.supabase.table('books').insert(book_data).execute()
            logging.info(f"Book inserted: {book_data['title']}")
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            logging.error(f"An error occurred while inserting: {str(e)}")
            return None

    def get_book_by_title(self, title):
        try:
            result = self.supabase.table('books').select('*').eq('title', title).execute()
            if result.data:
                logging.info(f"Book found: {title}")
                return result.data[0]
            else:
                logging.warning(f"No book found with title: {title}")
                return None
        except Exception as e:
            logging.error(f"An error occurred while fetching the book: {str(e)}")
            return None

    def update_book(self, id, updated_data):
        try:
            result = self.supabase.table('books').update(updated_data).eq('id', id).execute()
            if result.data:
                logging.info(f"Book with id '{id}' updated successfully")
                return 1
            else:
                logging.warning(f"No book found or updated with id '{id}'")
                return 0
        except Exception as e:
            logging.error(f"An error occurred while updating: {str(e)}")
            return None

    def delete_book(self, id):
        try:
            result = self.supabase.table('books').delete().eq('id', id).execute()
            if result.data:
                logging.info(f"Book with id '{id}' deleted successfully")
                return 1
            else:
                logging.warning(f"No book found or deleted with id '{id}'")
                return 0
        except Exception as e:
            logging.error(f"An error occurred while deleting: {str(e)}")
            return None

    def search_books(self, query=None, limit=None):
        try:
            table = self.supabase.table('books')
            if query:
                table = table.or_(f"title.ilike.%{query}%,author.ilike.%{query}%,description.ilike.%{query}%")
            if limit:
                table = table.limit(limit)
            result = table.execute()
            return result.data
        except Exception as e:
            logging.error(f"An error occurred while searching: {str(e)}")
            return []

    def count_books(self):
        try:
            result = self.supabase.table('books').select('*', count='exact').execute()
            return result.count
        except Exception as e:
            logging.error(f"An error occurred while counting books: {str(e)}")
            return 0
