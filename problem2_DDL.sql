CREATE DATABASE IF NOT EXISTS registration;
USE registration;


-- ==========================================
-- PRESERVE WEBSITE USERS
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
    user_id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    registration_date TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE (email)
) ENGINE=InnoDB;


-- ==========================================
-- REMOVE OLD LIBRARY TABLES
-- ==========================================

DROP TABLE IF EXISTS LOAN;
DROP TABLE IF EXISTS BOOK;
DROP TABLE IF EXISTS `MEMBER`;
DROP TABLE IF EXISTS CATEGORY;
DROP TABLE IF EXISTS PUBLISHER;
DROP TABLE IF EXISTS AUTHOR;


-- ==========================================
-- 1. AUTHOR TABLE
-- ==========================================

CREATE TABLE AUTHOR (
    author_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    photo_filename VARCHAR(255) NULL,

    PRIMARY KEY (author_id),
    UNIQUE (name)
) ENGINE=InnoDB;


-- ==========================================
-- 2. PUBLISHER TABLE
-- ==========================================

CREATE TABLE PUBLISHER (
    publisher_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,

    PRIMARY KEY (publisher_id),
    UNIQUE (name)
) ENGINE=InnoDB;


-- ==========================================
-- 3. CATEGORY TABLE
-- ==========================================

CREATE TABLE CATEGORY (
    category_id INT NOT NULL,
    name VARCHAR(60) NOT NULL,

    PRIMARY KEY (category_id),
    UNIQUE (name)
) ENGINE=InnoDB;


-- ==========================================
-- 4. BOOK TABLE
-- ==========================================

CREATE TABLE BOOK (
    book_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    publish_year INT NOT NULL,

    author_id INT NOT NULL,
    publisher_id INT NOT NULL,
    category_id INT NOT NULL,

    cover_filename VARCHAR(255) NULL,

    PRIMARY KEY (book_id),
    UNIQUE (title),

    FOREIGN KEY (author_id)
        REFERENCES AUTHOR(author_id)
        ON DELETE CASCADE,

    FOREIGN KEY (publisher_id)
        REFERENCES PUBLISHER(publisher_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (category_id)
        REFERENCES CATEGORY(category_id)
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- ==========================================
-- 5. MEMBER TABLE
-- ==========================================

CREATE TABLE `MEMBER` (
    member_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    join_date DATE NOT NULL,

    PRIMARY KEY (member_id),
    UNIQUE (email)
) ENGINE=InnoDB;


-- ==========================================
-- 6. LOAN TABLE
-- ==========================================

CREATE TABLE LOAN (
    loan_id INT NOT NULL,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE NULL,

    PRIMARY KEY (loan_id),

    FOREIGN KEY (book_id)
        REFERENCES BOOK(book_id)
        ON DELETE CASCADE,

    FOREIGN KEY (member_id)
        REFERENCES `MEMBER`(member_id)
        ON DELETE RESTRICT
) ENGINE=InnoDB;

