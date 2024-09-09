
# **Packt Book Scraper**

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
│
├── data/
│   ├── scraped_books.json # Exported JSON data
│   └── logs/             # Directory for storing log files
│       └── scraper.log   # Log file to capture events and errors
│
├── main.py               # Main Streamlit app script
├── .env                  # Environment variables file for sensitive information like SupaBase Project Key
├── requirements.txt      # Python dependencies for the project
├── README.md             # Project description, setup instructions, and usage guide
└── .gitignore            # Git ignore file to exclude unnecessary files from version control
```

## **Setup Instructions**

### **1. Prerequisites**
- Python 3.11+
- A SupaBase account and project key ([sign up here](https://supabase.com/))

### **2. Clone the Repository**

```bash
git clone https://github.com/Mohammed-Mebarek-Mecheter/packt_book_scraper.git
cd packt_book_scraper
```

### **3. Create a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### **4. Install Required Packages**

```bash
pip install -r requirements.txt
```

### **5. Set Up Environment Variables**

Create a `.env` file in the root of the project and add your SupaBase Project Key:

```
SupaBase_PROJECT_KEY=your_SupaBase_project_key_here
```

### **6. Run the Application**

```bash
streamlit run app/main.py
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

## **Contributing Guidelines**

### **1. Fork the Repository**

If you'd like to contribute, start by forking the repository on GitHub:

- Click the "Fork" button at the top right of the repository page.

### **2. Create a Feature Branch**

Create a new branch for your feature or bug fix:

```bash
git checkout -b feature-name
```

### **3. Make Your Changes**

Add your changes to the branch. Ensure that your code adheres to the project's coding standards.

### **4. Test Your Changes**

Run tests to ensure your changes don't break existing functionality. You can use the provided test scripts in the `tests/` directory.

### **5. Commit and Push Your Changes**

Commit your changes with a meaningful commit message:

```bash
git commit -m "Add feature XYZ"
git push origin feature-name
```

### **6. Submit a Pull Request**

Go to the original repository on GitHub and submit a pull request from your forked repository. Be sure to provide a SupaBaseiled description of the changes and the problem you're solving.

