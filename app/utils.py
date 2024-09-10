import logging
import re
import os

def clean_text(text, lower=False):
    """
    Cleans the input text by trimming whitespace and normalizing spaces.
    Optionally converts text to lowercase.
    """
    if not text:
        return text
    text = text.strip()  # Trim leading/trailing whitespace
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    if lower:
        text = text.lower()
    return text

def normalize_price(price):
    """
    Normalizes the price format by ensuring it is in a consistent format (e.g., "$39.99").
    """
    if not price:
        return "N/A"

    # Remove any non-numeric or non-dollar characters, keeping only the price
    price = re.sub(r'[^\d\.]', '', price)

    try:
        float(price)  # This will raise a ValueError if price is not a valid number
    except ValueError:
        return "N/A"

    return f"${price}"

def validate_url(url):
    """
    Validates the given URL to ensure it's a well-formed Packt Publishing URL.
    """
    packt_url_pattern = r'^https?:\/\/www\.packtpub\.com\/[a-zA-Z0-9\-_\/]+$'
    return bool(re.match(packt_url_pattern, url))

def validate_book_data(book_data):
    """
    Validates the book data to ensure that all required fields are present and correctly formatted.
    """
    required_fields = [
        "title", "author", "original_price", "discounted_price", "rating",
        "num_ratings", "publication_date", "pages", "edition",
        "key_benefits", "description", "what_you_will_learn"
    ]

    for field in required_fields:
        if field not in book_data or not book_data[field]:
            raise ValueError(f"Missing or empty required field: {field}")

    # Validate prices
    book_data['original_price'] = normalize_price(book_data.get('original_price', 'N/A'))
    book_data['discounted_price'] = normalize_price(book_data.get('discounted_price', 'N/A'))

    # Validate ratings (assuming ratings should be numeric)
    try:
        book_data['rating'] = float(book_data['rating'])
    except (ValueError, TypeError):
        raise ValueError(f"Invalid rating: {book_data['rating']}")

    # Clean text fields
    for field in ["title", "author", "description", "edition"]:
        if field in book_data:
            book_data[field] = clean_text(book_data[field])

    return True

def clean_and_validate_book_data(book_data):
    try:
        # Clean the data
        book_data['title'] = clean_text(book_data.get('title', 'Title not found'))

        # Clean and format author(s)
        author = book_data.get('author', 'Author not found')
        author = author.replace('By,', '').replace(',,', ',').strip()
        authors = [a.strip() for a in author.split(',') if a.strip()]
        book_data['author'] = ', '.join(authors)

        # Normalize prices
        book_data['original_price'] = normalize_price(book_data.get('original_price', 'N/A'))
        book_data['discounted_price'] = normalize_price(book_data.get('discounted_price', 'N/A'))

        # Convert rating to float
        rating_str = book_data.get('rating', '0').replace('out of 5 stars', '').strip()
        book_data['rating'] = float(rating_str) if rating_str and rating_str != "Rating not found" else None

        # Convert num_ratings to integer
        num_ratings_str = book_data.get('num_ratings', '0').strip('()')
        book_data['num_ratings'] = int(
            re.sub(r'\D', '', num_ratings_str)) if num_ratings_str and num_ratings_str != "0" else 0

        # Convert pages to integer
        pages_str = book_data.get('pages', '0')
        book_data['pages'] = int(
            re.sub(r'\D', '', pages_str)) if pages_str and pages_str != "Pages not specified" else None

        # Ensure key_benefits and what_you_will_learn are lists
        book_data['key_benefits'] = book_data.get('key_benefits', []) if isinstance(book_data.get('key_benefits'),
                                                                                    list) else [
            book_data.get('key_benefits', 'No key benefits found')]
        book_data['what_you_will_learn'] = book_data.get('what_you_will_learn', []) if isinstance(
            book_data.get('what_you_will_learn'), list) else [
            book_data.get('what_you_will_learn', 'No information found')]

        # Validate the data
        validate_book_data(book_data)

        return book_data

    except ValueError as e:
        # Log the validation error
        logging.error(f"Validation Error: {str(e)}")
        return None