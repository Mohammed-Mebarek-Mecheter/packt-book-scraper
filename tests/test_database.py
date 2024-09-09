from app.database import MongoDB

if __name__ == "__main__":
    mongo_db = MongoDB()

    # Example book data
    book_data = {
        "title": "Building LLM Powered Applications",
        "author": "Valentina Alto",
        "original_price": "$39.99",
        "discounted_price": "$27.98",
        "rating": "5",
        "num_ratings": "(1 Ratings)",
        "publication_date": "May 2024",
        "pages": "342 pages",
        "edition": "1st Edition",
        "key_benefits": ["Embed LLMs into real-world applications", "Use LangChain to orchestrate LLMs and their components"],
        "description": "A book about creating intelligent apps with LLMs.",
        "what_you_will_learn": ["Explore the core components of LLM architecture", "Understand the unique features of LLMs"]
    }

    # Create book
    inserted_id = mongo_db.create_book(book_data)
    print(f"Inserted Book ID: {inserted_id}")

    # Read book
    fetched_book = mongo_db.get_book_by_title("Building LLM Powered Applications")
    print(f"Fetched Book: {fetched_book}")

    # Update book
    updated_count = mongo_db.update_book("Building LLM Powered Applications", {"discounted_price": "$25.99"})
    print(f"Updated Book Count: {updated_count}")

    # Delete book
    deleted_count = mongo_db.delete_book("Building LLM Powered Applications")
    print(f"Deleted Book Count: {deleted_count}")

    # Close connection
    mongo_db.close()
