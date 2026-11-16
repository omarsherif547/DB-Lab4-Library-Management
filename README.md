
# Library Management System

A web-based Library Management System developed as part of the Introduction to Database Systems laboratory project.

The system is built using Python Flask and MySQL. It provides an interface for managing books and authors, searching the library catalogue, tracking book loans, and generating reports using SQL queries.

---

## 1. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| MySQL | Relational database management |
| MySQL Workbench | Database creation and SQL execution |
| PyMySQL | Python–MySQL connection |
| HTML5 | Web page structure |
| CSS3 | Website styling and layout |
| JavaScript | Client-side functionality and validation |
| Jinja2 | Dynamic HTML templates |
| bcrypt | Password hashing |
| Flask-Session | User session management |
| CacheLib | File-based session storage |
| python-dotenv | Environment configuration |

---

## 2. Project Features

### A. User Authentication

- User registration.
- User login and logout.
- Email validation (Gmail addresses).
- Password hashing using bcrypt.
- Session-based authentication.
- Protection of pages against unauthorized access.

### B. Author Management

- Add new authors.
- View all registered authors.
- Edit author information.
- Delete authors.
- Upload author profile photos.
- Support for replacing and removing uploaded photos.

### C. Book Management

- Add new books.
- View the library collection.
- Edit book information.
- Delete books.
- Upload book cover images.
- Support for replacing and removing uploaded covers.
- Prevent duplicate book titles and author names.

### D. Lab 4 Database Features

#### F2.1 – Search Books (WHERE)

Search for books using:
- Book title keyword (LIKE).
- Minimum price.
- Maximum price (BETWEEN when both prices are supplied).
- Category selection.

Search results are sorted by price in ascending order.

**Bonus:** Prepared statements using SQL placeholders (%s) are implemented to protect against SQL injection.

#### F2.2 – Complete Catalogue (JOIN)

Displays all books with their related information:

- Book ID.
- Book title.
- Author name.
- Publisher name.
- Category name.
- Price.
- Publication year.

Uses INNER JOIN to connect BOOK, AUTHOR, PUBLISHER and CATEGORY.

#### F2.3 – Library Reports (GROUP BY, HAVING)

Provides three reports:

1. Number of books and average price for each category.
2. Authors who have written at least two books.
3. Total, smallest and largest book prices in the library.

#### F2.4 – Loans Reports (JOIN, LEFT JOIN)

Provides three reports:

1. Books currently borrowed and not yet returned, including book titles and member names.
2. Members who have never borrowed a book.
3. Books that have never been borrowed.

A NULL return_date indicates that a book has not yet been returned.

#### F2.5 – Most Borrowed (GROUP BY, ORDER BY, LIMIT)

Displays:

1. The three books with the highest number of loans.
2. The member with the highest number of loans.

Results are ranked by borrowing frequency.

#### F2.6 – Authors and Books (LEFT JOIN, JOIN)

Provides two reports:

1. Every author and the number of books they have written, including authors with zero books.
2. Books whose author and publisher come from the same country.

---

## 3. Database Structure

The project uses the following six main library tables:

### AUTHOR
Stores author information.

| Column | Description |
|---|---|
| author_id | Primary Key |
| name | Author name |
| country | Author's country |
| photo_filename | Author profile photo |

### PUBLISHER
Stores publisher information.

| Column | Description |
|---|---|
| publisher_id | Primary Key |
| name | Publisher name |
| country | Publisher's country |

### CATEGORY
Stores book categories.

| Column | Description |
|---|---|
| category_id | Primary Key |
| name | Category name |

### BOOK
Stores book information.

| Column | Description |
|---|---|
| book_id | Primary Key |
| title | Book title |
| price | Book price |
| publish_year | Publication year |
| author_id | Foreign Key |
| publisher_id | Foreign Key |
| category_id | Foreign Key |
| cover_filename | Book cover image |

### MEMBER
Stores library member information.

| Column | Description |
|---|---|
| member_id | Primary Key |
| name | Member name |
| email | Member email |
| join_date | Registration date |

### LOAN
Stores book borrowing records.

| Column | Description |
|---|---|
| loan_id | Primary Key |
| book_id | Foreign Key |
| member_id | Foreign Key |
| loan_date | Borrowing date |
| return_date | Return date (NULL if not returned) |

### Database Relationships

- BOOK.author_id references AUTHOR.author_id.
- BOOK.publisher_id references PUBLISHER.publisher_id.
- BOOK.category_id references CATEGORY.category_id.
- LOAN.book_id references BOOK.book_id.
- LOAN.member_id references MEMBER.member_id.

**Referential Integrity:**
- Deleting an author automatically deletes their associated books.
- Deleting a book automatically deletes its associated loan records.

The application also uses a separate `users` table for website registration and authentication.

---

## 4. Sample Database Records

The provided seed data includes:

| Table | Number of Records |
|---|---:|
| AUTHOR | 5 |
| PUBLISHER | 3 |
| CATEGORY | 3 |
| BOOK | 10 |
| MEMBER | 5 |
| LOAN | 13 |

The sample data covers the required database scenarios, including:

- Authors from the same country.
- An author with no books.
- An author with multiple books.
- A book priced between 15 and 20.
- A book that has never been borrowed.
- A member who has never borrowed a book.
- A loan that has not been returned.

---

## 5. Project Folder Structure

```text
Lab3-2304021/
│
├── README.md
│
├── problem2_DDL.sql
├── problem2_DML.sql
├── problem2_Queries.sql
│
└── lab3-website/
    │
    ├── app.py
    ├── requirements.txt
    ├── .env
    ├── .env.example
    │
    ├── Database/
    │
    ├── static/
    │   ├── style.css
    │   ├── theme.js
    │   ├── validation.js
    │   └── uploads/
    │
    ├── templates/
    │   ├── add_author.html
    │   ├── add_book.html
    │   ├── edit_author.html
    │   ├── edit_book.html
    │   ├── library.html
    │   ├── search_books.html
    │   ├── catalogue.html
    │   ├── reports.html
    │   ├── loans.html
    │   ├── most_borrowed.html
    │   ├── authors_books.html
    │   ├── login.html
    │   └── register.html
    │
    ├── session_cache/
    │
    └── .venv/
```

**Note:** The `.venv`, `.env`, and `session_cache` folders are local environment/session data and should not be uploaded to GitHub.

---

## 6. Installation Requirements

Before running the project, install:

1. Python.
2. MySQL Server.
3. MySQL Workbench.
4. Visual Studio Code (recommended).

---

## 7. Installation and Setup

### Step 1 – Open the Project

Open the project folder in Visual Studio Code.

Open the terminal and navigate to the website directory:

```powershell
cd lab3-website
```

### Step 2 – Create a Virtual Environment

Run:

```powershell
py -m venv .venv
```

### Step 3 – Install Dependencies

Install the required Python packages:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 4 – Configure Environment Variables

If you do not already have a `.env` file, create one by copying `.env.example`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure the following values:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=registration
SECRET_KEY=YOUR_SECRET_KEY
```

Replace the example values with your actual MySQL credentials.

Generate a secure secret key using:

```powershell
py -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into `SECRET_KEY`.

**Important:** Never upload your actual `.env` file or database password to GitHub.

### Step 5 – Create and Populate the Database

Open MySQL Workbench and connect to your local MySQL instance.

Execute the SQL scripts in the following order:

**1. Create the required database tables:**

```text
problem2_DDL.sql
```

**2. Insert the sample data:**

```text
problem2_DML.sql
```

If the website's original `users` table has not been created yet, also execute the existing authentication database schema from the `Database` folder before starting the website.

**3. Verify the database:**

```sql
USE registration;

SELECT * FROM AUTHOR;
SELECT * FROM PUBLISHER;
SELECT * FROM CATEGORY;
SELECT * FROM BOOK;
SELECT * FROM `MEMBER`;
SELECT * FROM LOAN;
```

Make sure the records have been inserted successfully.

Do not execute the seed-data script repeatedly without clearing the existing records, because duplicate primary keys will cause errors.

### Step 6 – Run the Website

Return to the VS Code terminal.

Make sure you are inside the `lab3-website` folder.

Run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Flask will start the local development server.

### Step 7 – Open the Website

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

Register a new account or log in using an existing account.

You can now access the Library Management Dashboard.

---

## 8. Image Upload Management

The application supports uploading author photos and book cover images.

**Supported formats:**
- JPG
- JPEG
- PNG
- WEBP

Maximum upload size: 5 MB.

Uploaded images are stored in:

```text
static/uploads/
```

The image filenames are stored in their corresponding database records.

The application manages image replacement and deletion so that old uploaded images can be removed when they are no longer needed.

The `session_cache/` folder is used for Flask session storage and is not used for image uploads.

---

## 9. Security and Validation

The application implements several security and validation measures:

- Password hashing using bcrypt.
- Parameterized SQL queries using PyMySQL.
- Environment variables for database credentials.
- Session-based authentication.
- Protection of authenticated pages.
- Required-field validation.
- Email format validation.
- Price validation.
- Image file extension validation.
- Secure filenames for uploaded images.
- Database foreign key constraints.
- Unique constraints for author names and book titles.

---

## 10. SQL Queries File

All SQL queries for the Lab 4 website requirements are documented in:

```text
problem2_Queries.sql
```

The file contains the SQL queries corresponding to:

- F2.1 – Search Books.
- F2.2 – Complete Catalogue.
- F2.3 – Library Reports.
- F2.4 – Loans Reports.
- F2.5 – Most Borrowed.
- F2.6 – Authors and Books.

Each section is identified by its corresponding F2 requirement.

The queries can be executed separately in MySQL Workbench to verify the results.

---

## 11. Important Notes

- MySQL Server must be running before starting the Flask application.
- The database name must match `DB_NAME` in `.env`.
- The `users` table must exist for registration and login.
- Uploaded images are stored locally in `static/uploads/`.
- Flask session files are stored separately in `session_cache/`.
- The virtual environment must be activated or its Python executable must be used when running the application.
- The Flask debug server is intended for local development, not production deployment.

---

## 12. Conclusion

The Library Management System combines database management concepts with a web-based interface.

It demonstrates the practical implementation of SQL operations, relational database relationships, JOIN operations, aggregation, GROUP BY, HAVING, LEFT JOIN, ORDER BY, LIMIT, and prepared statements.

The project also integrates user authentication, data validation, image uploads, and CRUD operations into a single application.

**Project:** Library Management System  
**Course:** Introduction to Database Systems  
**Database:** MySQL  
**Backend:** Python Flask