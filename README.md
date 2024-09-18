~~# **Packt Book Scraper**

## **Project Description**

Packt Book Scraper is a web application built with Streamlit that allows users to scrape book Details from the Packt Publishing website. It provides a user-friendly interface for inputting book URLs, managing scraped data, and displaying the data using an interactive AG Grid table. The project uses SupaBase for storing the scraped book data and allows users to search, view, and export the stored data.

## **Features**
- **Scrape Book Details**: Extracts information such as title, author, price, rating, publication date, and more from Packt book URLs.
- **Store Scraped Data**: Saves the scraped data in a SupaBase database.
- **Interactive Data Display**: Uses AG Grid to display the scraped books in a sortable, filterable, and paginated table.
- **Search Functionality**: Allows users to search for books by title, author, or keywords.
- **Data Export**: Users can export the search results or all stored books to CSV or JSON files.

## **Project Structure**

```
packt_book_scraper/
│
├── app/
│   ├── scraper.py        # Scraper logic for extracting book Details
│   └── utils.py          # Utility functions for data cleaning, validation, etc.
│   ├── search.py
│   ├── visualize.py
│   └── assets/
│       └── style.css
├── data/
│   └── logs/             # Directory for storing log files
│       └── scraper.log   # Log file to capture events and errors
│
├── main.py               # Main Streamlit app script
├── .env                  # Environment variables file for sensitive information like SupaBase Project Key
├── requirements.txt      # Python dependencies for the project
├── README.md             # Project description, setup instructions, and usage guide
└── .gitignore            # Git ignore file to exclude unnecessary files from version control
```

## **Usage Guide**

### **1. Scrape Book Data**

- **Enter URLs**: Input one or more Packt book URLs in the text area or upload a CSV file containing URLs.
- **Scrape Books**: Click the "Scrape Books" button to start scraping. Progress will be shown with a progress bar.
- **View Results**: The scraped book Details will be displayed below the input section.

### **2. Search and Manage Books**

- **Search**: Use the search bar to find books by title, author, or keyword.
- **View All Books**: Click the "Show All Books" button to see all books stored in the database.
- **Interact with Data**: The AG Grid table allows sorting, filtering, and pagination.

### **3. Export Data**

- **Export Results**: Export the search results or all books in the database to CSV or JSON format using the export options.
