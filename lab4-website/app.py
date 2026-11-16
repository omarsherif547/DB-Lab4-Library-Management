from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from cachelib import FileSystemCache
import pymysql
import bcrypt
import os
import math
from dotenv import load_dotenv
import re
from werkzeug.utils import secure_filename


# =====================================================
# 1. FLASK CONFIGURATION
# =====================================================

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY is missing from .env")

app.config["SESSION_TYPE"] = "cachelib"
app.config["SESSION_CACHELIB"] = FileSystemCache(
    cache_dir="session_cache",
    threshold=500,
)

app.config["SESSION_PERMANENT"] = False

Session(app)

# Image upload configuration
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path, "static", "uploads"
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


def delete_uploaded_file(filename):
    """Delete an uploaded image safely; ignore missing or invalid filenames."""

    if not filename or os.path.basename(filename) != filename:
        return

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except OSError:
        app.logger.exception("Could not delete uploaded file: %s", filename)


# =====================================================
# 2. MYSQL DATABASE CONNECTION
# =====================================================

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )


# =====================================================
# 3. HOME PAGE
# =====================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("library"))

    return redirect(url_for("login"))


# =====================================================
# 4. USER REGISTRATION
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html", errors=[])

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = []

    if not name:
        errors.append("Name is required")

    if not email:
        errors.append("Email is required")

    elif not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@gmail\.com",
        email,
        re.IGNORECASE
    ):
        errors.append(
            "Please enter a valid Gmail address ending in @gmail.com"
        )

    if not password:
        errors.append("Password is required")

    if not confirm_password:
        errors.append("Confirm password is required")

    if password and confirm_password and password != confirm_password:
        errors.append("Passwords do not match")

    if errors:
        return render_template("register.html", errors=errors)

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    connection = get_db()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO users (email, name, password_hash)
                VALUES (%s, %s, %s)
                """,
                (email, name, hashed_password),
            )

            user_id = cursor.lastrowid

        connection.commit()

    except pymysql.err.IntegrityError as error:

        connection.rollback()

        if error.args[0] == 1062:
            return render_template(
                "register.html",
                errors=["Email Already Exists"],
            )

        raise

    finally:
        connection.close()

    session.clear()
    session["user_id"] = user_id
    session["name"] = name

    return redirect(url_for("library"))


# =====================================================
# 5. USER LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html", errors=[])

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    errors = []

    if not email:
        errors.append("Email is required")

    if not password:
        errors.append("Password is required")

    if errors:
        return render_template("login.html", errors=errors)

    connection = get_db()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT user_id, name, password_hash
                FROM users
                WHERE email = %s
                """,
                (email,),
            )

            user = cursor.fetchone()

    finally:
        connection.close()

    if not user:
        return render_template(
            "login.html",
            errors=["Invalid email or password"],
        )

    try:
        password_correct = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )

    except (ValueError, TypeError):
        password_correct = False

    if not password_correct:
        return render_template(
            "login.html",
            errors=["Invalid email or password"],
        )

    session.clear()
    session["user_id"] = user["user_id"]
    session["name"] = user["name"]

    return redirect(url_for("library"))


# =====================================================
# 6. USER LOGOUT
# =====================================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return redirect(url_for("login"))


# =====================================================
# 7. LIBRARY: DISPLAY AUTHORS AND BOOKS
# =====================================================

@app.route("/library")
def library():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT author_id, name, country, photo_filename
                FROM AUTHOR
                ORDER BY author_id
                """
            )

            authors = cursor.fetchall()

            cursor.execute(
                """
                SELECT book_id, title, price, author_id, cover_filename
                FROM BOOK
                ORDER BY book_id
                """
            )

            books = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "library.html",
        name=session["name"],
        authors=authors,
        books=books,
    )


# =====================================================
# F2.1 - SEARCH BOOKS
# =====================================================

@app.route("/search", methods=["GET"])
def search_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []
    books = []

    keyword = request.args.get("keyword", "").strip()
    min_price_input = request.args.get("min_price", "").strip()
    max_price_input = request.args.get("max_price", "").strip()
    category_input = request.args.get("category_id", "").strip()
    search_submitted = bool(request.args)
    if search_submitted and not keyword:
        errors.append("Please enter a book title.")

    connection = get_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT category_id, name
                FROM CATEGORY
                ORDER BY name
                """
            )

            categories = cursor.fetchall()

            valid_category_ids = {
                category["category_id"]
                for category in categories
            }

            conditions = []
            params = []

            if keyword:
                conditions.append("B.title LIKE %s")
                params.append(f"%{keyword}%")

            min_price = None
            max_price = None

            if min_price_input:

                try:
                    min_price = float(min_price_input)

                    if not math.isfinite(min_price) or min_price < 0:
                        errors.append(
                            "Minimum price must be a valid non-negative number."
                        )

                except ValueError:
                    errors.append("Invalid minimum price.")

            if max_price_input:

                try:
                    max_price = float(max_price_input)

                    if not math.isfinite(max_price) or max_price < 0:
                        errors.append(
                            "Maximum price must be a valid non-negative number."
                        )

                except ValueError:
                    errors.append("Invalid maximum price.")

            if min_price is not None and max_price is not None:

                if min_price > max_price:
                    errors.append(
                        "Minimum price cannot be greater than maximum price."
                    )

                else:
                    conditions.append(
                        "B.price BETWEEN %s AND %s"
                    )

                    params.extend([min_price, max_price])

            elif min_price is not None:

                conditions.append("B.price >= %s")
                params.append(min_price)

            elif max_price is not None:

                conditions.append("B.price <= %s")
                params.append(max_price)

            if category_input:

                if (
                    not category_input.isdigit()
                    or int(category_input) not in valid_category_ids
                ):
                    errors.append("Please select a valid category.")

                else:
                    conditions.append("B.category_id = %s")
                    params.append(int(category_input))

            if not errors:

                sql = """
                    SELECT
                        B.book_id,
                        B.title,
                        B.price,
                        B.publish_year,
                        B.cover_filename,
                        A.name AS author_name,
                        P.name AS publisher_name,
                        C.name AS category_name

                    FROM BOOK B

                    INNER JOIN AUTHOR A
                        ON B.author_id = A.author_id

                    INNER JOIN PUBLISHER P
                        ON B.publisher_id = P.publisher_id

                    INNER JOIN CATEGORY C
                        ON B.category_id = C.category_id
                """

                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)

                sql += """
                    ORDER BY B.price ASC, B.title ASC
                """

                cursor.execute(sql, tuple(params))

                books = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "search_books.html",
        books=books,
        categories=categories,
        keyword=keyword,
        min_price=min_price_input,
        max_price=max_price_input,
        selected_category=category_input,
        errors=errors,
    )


# =====================================================
# F2.2 - COMPLETE BOOK CATALOGUE
# =====================================================

@app.route("/catalogue")
def catalogue():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    B.book_id,
                    B.title,
                    B.price,
                    B.publish_year,
                    B.cover_filename,
                    A.name AS author_name,
                    P.name AS publisher_name,
                    C.name AS category_name

                FROM BOOK B

                INNER JOIN AUTHOR A
                    ON B.author_id = A.author_id

                INNER JOIN PUBLISHER P
                    ON B.publisher_id = P.publisher_id

                INNER JOIN CATEGORY C
                    ON B.category_id = C.category_id

                ORDER BY B.title ASC
                """
            )

            books = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "catalogue.html",
        books=books,
        name=session["name"]
    )


# =====================================================
# 8. ADD AUTHOR
# =====================================================

@app.route("/authors/add", methods=["GET", "POST"])
def add_author():

    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []

    if request.method == "POST":

        author_id_input = request.form.get("author_id", "").strip()
        author_name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()

        photo = request.files.get("author_photo")
        has_photo = photo is not None and bool(photo.filename.strip())

        if not author_id_input.isdigit() or int(author_id_input) < 1:
            errors.append("Author ID must be a positive number.")

        if not author_name:
            errors.append("Author name is required.")

        elif len(author_name) > 100:
            errors.append("Author name cannot exceed 100 characters.")

        if not country:
            errors.append("Country is required.")

        elif len(country) > 50:
            errors.append("Country cannot exceed 50 characters.")

        safe_name = None

        if has_photo:

            if not allowed_image(photo.filename):
                errors.append(
                    "Photo must be JPG, JPEG, PNG, or WebP."
                )

            else:
                safe_name = secure_filename(photo.filename)

                if not safe_name:
                    errors.append("Invalid photo filename.")

        if not errors:

            connection = get_db()
            saved_path = None

            try:

                photo_filename = None

                if has_photo:

                    photo_filename = (
                        f"{os.urandom(8).hex()}_{safe_name}"
                    )

                    saved_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        photo_filename,
                    )

                    photo.save(saved_path)

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        INSERT INTO AUTHOR
                            (author_id, name, country, photo_filename)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            int(author_id_input),
                            author_name,
                            country,
                            photo_filename,
                        ),
                    )

                connection.commit()

                return redirect(url_for("library"))

            except pymysql.err.IntegrityError as error:

                connection.rollback()

                if saved_path and os.path.isfile(saved_path):
                    os.remove(saved_path)

                if error.args[0] == 1062:

                    error_message = str(error.args[1])

                    if "uq_author_name" in error_message:
                        errors.append("An author with this name already exists.")

                    else:
                        errors.append("This Author ID already exists.")

                else:
                    errors.append("Could not add the author.")

            except Exception:

                connection.rollback()

                if saved_path and os.path.isfile(saved_path):
                    os.remove(saved_path)

                raise

            finally:
                connection.close()

    return render_template("add_author.html", errors=errors)


# =====================================================
# 9. EDIT AUTHOR
# =====================================================


@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []
    connection = get_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM AUTHOR WHERE author_id = %s",
                (author_id,),
            )
            author = cursor.fetchone()

        if not author:
            return "Author not found", 404

        if request.method == "POST":

            name = request.form.get("name", "").strip()
            country = request.form.get("country", "").strip()

            photo = request.files.get("author_photo")
            has_photo = (
                photo is not None and bool(photo.filename.strip())
            )

            if not name:
                errors.append("Author name is required.")
            elif len(name) > 100:
                errors.append("Author name cannot exceed 100 characters.")

            if not country:
                errors.append("Country is required.")
            elif len(country) > 50:
                errors.append("Country cannot exceed 50 characters.")

            old_photo = author.get("photo_filename")
            new_photo_filename = old_photo
            safe_name = None

            if has_photo:

                if not allowed_image(photo.filename):
                    errors.append(
                        "Photo must be JPG, JPEG, PNG, or WebP."
                    )

                else:
                    safe_name = secure_filename(photo.filename)

                    if not safe_name:
                        errors.append("Invalid photo filename.")

            if not errors:

                saved_filename = None

                try:

                    if has_photo:

                        saved_filename = (
                            f"{os.urandom(8).hex()}_{safe_name}"
                        )

                        saved_path = os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            saved_filename,
                        )

                        photo.save(saved_path)

                        new_photo_filename = saved_filename

                    with connection.cursor() as cursor:

                        cursor.execute(
                            """
                            UPDATE AUTHOR
                            SET name = %s,
                                country = %s,
                                photo_filename = %s
                            WHERE author_id = %s
                            """,
                            (
                                name,
                                country,
                                new_photo_filename,
                                author_id,
                            ),
                        )

                    connection.commit()

                    if (
                        has_photo
                        and old_photo
                        and old_photo != new_photo_filename
                    ):
                        delete_uploaded_file(old_photo)

                    return redirect(url_for("library"))

                except pymysql.err.IntegrityError as error:

                    connection.rollback()

                
                    if saved_filename:
                        delete_uploaded_file(saved_filename)

                    if error.args[0] == 1062:
                        errors.append(
                            "An author with this name already exists."
                        )
                    else:
                        errors.append("Could not update the author.")

                except Exception:

                    connection.rollback()

                   
                    if saved_filename:
                        delete_uploaded_file(saved_filename)

                    raise

            
            author["name"] = name
            author["country"] = country

    finally:
        connection.close()

    return render_template(
        "edit_author.html",
        author=author,
        errors=errors,
    )


# =====================================================
# 10. DELETE AUTHOR
# =====================================================


@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()
    image_filenames = []

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT photo_filename
                FROM AUTHOR
                WHERE author_id = %s
                """,
                (author_id,)
            )

            author = cursor.fetchone()

            if author:

                if author.get("photo_filename"):
                    image_filenames.append(
                        author["photo_filename"]
                    )

                cursor.execute(
                    """
                    SELECT cover_filename
                    FROM BOOK
                    WHERE author_id = %s
                    """,
                    (author_id,)
                )

                books = cursor.fetchall()

                for book in books:
                    if book.get("cover_filename"):
                        image_filenames.append(
                            book["cover_filename"]
                        )

                cursor.execute(
                    """
                    DELETE FROM AUTHOR
                    WHERE author_id = %s
                    """,
                    (author_id,)
                )

        connection.commit()

    except pymysql.err.IntegrityError:
        connection.rollback()

        return (
            "Cannot delete this author because related records exist. "
            "Check your foreign key constraints.",
            409
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    for filename in image_filenames:
        delete_uploaded_file(filename)

    return redirect(url_for("library"))


# =====================================================
# 11. ADD BOOK - LAB 4 UPDATED
# =====================================================

@app.route("/books/add", methods=["GET", "POST"])
def add_book():

    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []
    connection = get_db()
    saved_path = None

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT author_id, name FROM AUTHOR ORDER BY name"
            )

            authors = cursor.fetchall()

            cursor.execute(
                "SELECT publisher_id, name FROM PUBLISHER ORDER BY name"
            )

            publishers = cursor.fetchall()

            cursor.execute(
                "SELECT category_id, name FROM CATEGORY ORDER BY name"
            )

            categories = cursor.fetchall()

        if request.method == "POST":

            book_id_input = request.form.get("book_id", "").strip()
            title = request.form.get("title", "").strip()
            price_input = request.form.get("price", "").strip()
            year_input = request.form.get("publish_year", "").strip()

            author_input = request.form.get("author_id", "").strip()
            publisher_input = request.form.get("publisher_id", "").strip()
            category_input = request.form.get("category_id", "").strip()

            cover = request.files.get("cover_image")
            has_cover = cover is not None and bool(cover.filename.strip())


            if not book_id_input.isdigit() or int(book_id_input) < 1:
                errors.append("Book ID must be a positive number.")


            if not title:
                errors.append("Book title is required.")

            elif len(title) > 100:
                errors.append("Book title cannot exceed 100 characters.")


            price = None

            try:
                price = float(price_input)

                if not math.isfinite(price) or price < 0:
                    errors.append("Enter a valid non-negative price.")

            except ValueError:
                errors.append("Enter a valid price.")

            publish_year = None

            if not year_input.isdigit():
                errors.append("Publication year must be a number.")

            else:
                publish_year = int(year_input)

                if publish_year < 1 or publish_year > 2100:
                    errors.append("Enter a valid publication year.")


            author_ids = {a["author_id"] for a in authors}
            publisher_ids = {p["publisher_id"] for p in publishers}
            category_ids = {c["category_id"] for c in categories}

            if not author_input.isdigit() or int(author_input) not in author_ids:
                errors.append("Please select a valid author.")

            if not publisher_input.isdigit() or int(publisher_input) not in publisher_ids:
                errors.append("Please select a valid publisher.")

            if not category_input.isdigit() or int(category_input) not in category_ids:
                errors.append("Please select a valid category.")


            safe_name = None

            if has_cover:

                if not allowed_image(cover.filename):
                    errors.append("Cover must be JPG, JPEG, PNG or WebP.")

                else:
                    safe_name = secure_filename(cover.filename)

                    if not safe_name:
                        errors.append("Invalid cover filename.")

            if not errors:

                try:

                    cover_filename = None

                    if has_cover:

                        cover_filename = (
                            f"{os.urandom(8).hex()}_{safe_name}"
                        )

                        saved_path = os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            cover_filename,
                        )

                        cover.save(saved_path)

                    with connection.cursor() as cursor:

                        cursor.execute(
                            """
                            INSERT INTO BOOK
                            (
                                book_id,
                                title,
                                price,
                                publish_year,
                                author_id,
                                publisher_id,
                                category_id,
                                cover_filename
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                int(book_id_input),
                                title,
                                price,
                                publish_year,
                                int(author_input),
                                int(publisher_input),
                                int(category_input),
                                cover_filename,
                            ),
                        )

                    connection.commit()

                    return redirect(url_for("library"))

                except pymysql.err.IntegrityError as error:

                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    if error.args[0] == 1062:
                        errors.append(
                            "Book ID or book title already exists."
                        )

                    elif error.args[0] == 1452:
                        errors.append(
                            "One of the selected records does not exist."
                        )

                    else:
                        errors.append("Could not add the book.")

                except Exception:

                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    raise

    finally:
        connection.close()

    return render_template(
        "add_book.html",
        errors=errors,
        authors=authors,
        publishers=publishers,
        categories=categories,
    )


# =====================================================
# 12. EDIT BOOK - LAB 4 UPDATED
# =====================================================

@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []
    connection = get_db()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT * FROM BOOK WHERE book_id = %s",
                (book_id,),
            )

            book = cursor.fetchone()

            if not book:
                return "Book not found", 404

            cursor.execute(
                "SELECT author_id, name FROM AUTHOR ORDER BY name"
            )

            authors = cursor.fetchall()

            cursor.execute(
                "SELECT publisher_id, name FROM PUBLISHER ORDER BY name"
            )

            publishers = cursor.fetchall()

            cursor.execute(
                "SELECT category_id, name FROM CATEGORY ORDER BY name"
            )

            categories = cursor.fetchall()

        if request.method == "POST":

            title = request.form.get("title", "").strip()
            price_input = request.form.get("price", "").strip()
            year_input = request.form.get("publish_year", "").strip()

            author_input = request.form.get("author_id", "").strip()
            publisher_input = request.form.get("publisher_id", "").strip()
            category_input = request.form.get("category_id", "").strip()

            cover = request.files.get("cover_image")
            has_cover = cover is not None and bool(cover.filename.strip())

            # Validate title

            if not title:
                errors.append("Book title is required.")

            elif len(title) > 100:
                errors.append("Book title cannot exceed 100 characters.")

            # Validate price

            price = None

            try:
                price = float(price_input)

                if not math.isfinite(price) or price < 0:
                    errors.append("Enter a valid non-negative price.")

            except ValueError:
                errors.append("Enter a valid price.")

            # Validate publication year

            publish_year = None

            if not year_input.isdigit():
                errors.append("Publication year must be a number.")

            else:
                publish_year = int(year_input)

                if publish_year < 1 or publish_year > 2100:
                    errors.append("Enter a valid publication year.")

            # Validate foreign keys

            author_ids = {a["author_id"] for a in authors}
            publisher_ids = {p["publisher_id"] for p in publishers}
            category_ids = {c["category_id"] for c in categories}

            author_id_value = None
            publisher_id_value = None
            category_id_value = None

            if author_input.isdigit() and int(author_input) in author_ids:
                author_id_value = int(author_input)

            else:
                errors.append("Select a valid author.")

            if publisher_input.isdigit() and int(publisher_input) in publisher_ids:
                publisher_id_value = int(publisher_input)

            else:
                errors.append("Select a valid publisher.")

            if category_input.isdigit() and int(category_input) in category_ids:
                category_id_value = int(category_input)

            else:
                errors.append("Select a valid category.")

            # Keep old cover unless a new one is uploaded

            cover_filename = book.get("cover_filename")
            safe_name = None

            if has_cover:

                if not allowed_image(cover.filename):
                    errors.append("Cover must be JPG, JPEG, PNG or WebP.")

                else:
                    safe_name = secure_filename(cover.filename)

                    if not safe_name:
                        errors.append("Invalid cover filename.")

                    else:
                        cover_filename = (
                            f"{os.urandom(8).hex()}_{safe_name}"
                        )

            # Update book

            if not errors:

                saved_path = None
                old_cover = book.get("cover_filename")

                try:

                    if has_cover:

                        saved_path = os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            cover_filename,
                        )

                        cover.save(saved_path)

                    with connection.cursor() as cursor:

                        cursor.execute(
                            """
                            UPDATE BOOK
                            SET title = %s,
                                price = %s,
                                publish_year = %s,
                                author_id = %s,
                                publisher_id = %s,
                                category_id = %s,
                                cover_filename = %s
                            WHERE book_id = %s
                            """,
                            (
                                title,
                                price,
                                publish_year,
                                author_id_value,
                                publisher_id_value,
                                category_id_value,
                                cover_filename,
                                book_id,
                            ),
                        )

                    connection.commit()

                    # Delete old image only after successful update

                    if (has_cover and old_cover and old_cover != cover_filename):
                        delete_uploaded_file(old_cover)

                    return redirect(url_for("library"))

                except pymysql.err.IntegrityError as error:

                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    if error.args[0] == 1062:
                        errors.append("A book with this title already exists.")

                    else:
                        errors.append("Could not update the book.")

                except Exception:

                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    raise

            # Preserve submitted values if validation fails

            book["title"] = title
            book["price"] = price_input
            book["publish_year"] = year_input
            book["author_id"] = author_input
            book["publisher_id"] = publisher_input
            book["category_id"] = category_input

    finally:
        connection.close()

    return render_template(
        "edit_book.html",
        book=book,
        authors=authors,
        publishers=publishers,
        categories=categories,
        errors=errors,
    )


# =====================================================
# 13. DELETE BOOK
# =====================================================


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()
    cover_filename = None

    try:
        with connection.cursor() as cursor:

            # Get book cover before deleting the book
            cursor.execute(
                """
                SELECT cover_filename
                FROM BOOK
                WHERE book_id = %s
                """,
                (book_id,)
            )

            book = cursor.fetchone()

            if book:
                cover_filename = book.get("cover_filename")

            # Delete book from database
            cursor.execute(
                """
                DELETE FROM BOOK
                WHERE book_id = %s
                """,
                (book_id,)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    # Delete cover after successful database deletion
    delete_uploaded_file(cover_filename)

    return redirect(url_for("library"))

# =====================================================
# F2.3 - LIBRARY REPORTS
# =====================================================

@app.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    try:
        with connection.cursor() as cursor:

            # 1. Books and average price per category

            cursor.execute("""
                SELECT
                    C.category_id,
                    C.name AS category_name,
                    COUNT(B.book_id) AS total_books,
                    AVG(B.price) AS average_price
                FROM CATEGORY C
                LEFT JOIN BOOK B
                    ON C.category_id = B.category_id
                GROUP BY C.category_id, C.name
                ORDER BY C.name
            """)

            category_reports = cursor.fetchall()

            # 2. Authors who wrote at least 2 books

            cursor.execute("""
                SELECT
                    A.author_id,
                    A.name AS author_name,
                    COUNT(B.book_id) AS total_books
                FROM AUTHOR A
                INNER JOIN BOOK B
                    ON A.author_id = B.author_id
                GROUP BY A.author_id, A.name
                HAVING COUNT(B.book_id) >= 2
                ORDER BY total_books DESC
            """)

            author_reports = cursor.fetchall()

            # 3. Total, smallest and largest book prices

            cursor.execute("""
                SELECT
                    SUM(price) AS total_price,
                    MIN(price) AS smallest_price,
                    MAX(price) AS largest_price
                FROM BOOK
            """)

            price_summary = cursor.fetchone()

    finally:
        connection.close()

    return render_template(
        "reports.html",
        category_reports=category_reports,
        author_reports=author_reports,
        price_summary=price_summary
    )


# =====================================================
# F2.4 - LOANS REPORTS
# =====================================================

@app.route("/loans")
def loans():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    try:
        with connection.cursor() as cursor:

            # A. Loans not returned yet

            cursor.execute("""
                SELECT
                    L.loan_id,
                    B.title AS book_title,
                    M.name AS member_name,
                    L.loan_date
                FROM LOAN L
                JOIN BOOK B ON L.book_id = B.book_id
                JOIN `MEMBER` M ON L.member_id = M.member_id
                WHERE L.return_date IS NULL
            """)

            active_loans = cursor.fetchall()

            # B. Members who never borrowed

            cursor.execute("""
                SELECT
                    M.member_id,
                    M.name,
                    M.email
                FROM `MEMBER` M
                LEFT JOIN LOAN L
                    ON M.member_id = L.member_id
                WHERE L.loan_id IS NULL
            """)

            members_without_loans = cursor.fetchall()

            # C. Books never borrowed

            cursor.execute("""
                SELECT
                    B.book_id,
                    B.title,
                    B.price
                FROM BOOK B
                LEFT JOIN LOAN L
                    ON B.book_id = L.book_id
                WHERE L.loan_id IS NULL
            """)

            books_never_borrowed = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "loans.html",
        active_loans=active_loans,
        members_without_loans=members_without_loans,
        books_never_borrowed=books_never_borrowed
    )


# =====================================================
# F2.5 - MOST BORROWED
# =====================================================

@app.route("/most-borrowed")
def most_borrowed():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    try:
        with connection.cursor() as cursor:

            # 1. Three books with the most loans

            cursor.execute("""
                SELECT
                    B.book_id,
                    B.title,
                    COUNT(L.loan_id) AS total_loans
                FROM BOOK B
                INNER JOIN LOAN L
                    ON B.book_id = L.book_id
                GROUP BY B.book_id, B.title
                ORDER BY total_loans DESC, B.title ASC
                LIMIT 3
            """)

            top_books = cursor.fetchall()

            # 2. Member with the most loans

            cursor.execute("""
                SELECT
                    M.member_id,
                    M.name,
                    COUNT(L.loan_id) AS total_loans
                FROM `MEMBER` M
                INNER JOIN LOAN L
                    ON M.member_id = L.member_id
                GROUP BY M.member_id, M.name
                ORDER BY total_loans DESC, M.name ASC
                LIMIT 1
            """)

            top_member = cursor.fetchone()

    finally:
        connection.close()

    return render_template(
        "most_borrowed.html",
        top_books=top_books,
        top_member=top_member
    )


# =====================================================
# F2.6 - AUTHORS AND BOOKS
# =====================================================

@app.route("/authors-books")
def authors_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    try:
        with connection.cursor() as cursor:

            # 1. Every author with number of books,
            # including authors who wrote zero books

            cursor.execute("""
                SELECT
                    A.author_id,
                    A.name AS author_name,
                    A.country,
                    COUNT(B.book_id) AS total_books
                FROM AUTHOR A
                LEFT JOIN BOOK B
                    ON A.author_id = B.author_id
                GROUP BY
                    A.author_id,
                    A.name,
                    A.country
                ORDER BY A.name ASC
            """)

            author_reports = cursor.fetchall()

            # 2. Books whose author and publisher
            # come from the same country

            cursor.execute("""
                SELECT
                    B.book_id,
                    B.title,
                    A.name AS author_name,
                    A.country AS author_country,
                    P.name AS publisher_name,
                    P.country AS publisher_country
                FROM BOOK B
                INNER JOIN AUTHOR A
                    ON B.author_id = A.author_id
                INNER JOIN PUBLISHER P
                    ON B.publisher_id = P.publisher_id
                WHERE A.country = P.country
                ORDER BY B.title ASC
            """)

            matching_books = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "authors_books.html",
        author_reports=author_reports,
        matching_books=matching_books
    )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
