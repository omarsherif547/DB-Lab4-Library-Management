
-- ==========================================
-- LAB 4 - PART II
-- PROBLEM 2 - SEED DATA
-- DATABASE: REGISTRATION
-- ==========================================

USE registration;


-- ==========================================
-- 1. AUTHORS
-- ==========================================

INSERT INTO AUTHOR (author_id, name, country)
VALUES
(1, 'Ahmed Khaled Tawfik', 'Egypt'),
(2, 'Naguib Mahfouz', 'Egypt'),
(3, 'William Shakespeare', 'England'),
(4, 'Ahmed Mourad', 'Egypt'),
(5, 'Jane Austen', 'England');


-- ==========================================
-- 2. PUBLISHERS
-- ==========================================

INSERT INTO PUBLISHER (publisher_id, name, country)
VALUES
(1, 'Egyptian General Book Organization', 'Egypt'),
(2, 'Penguin Random House', 'USA'),
(3, 'Oxford University Press', 'England');


-- ==========================================
-- 3. CATEGORIES
-- ==========================================

INSERT INTO CATEGORY (category_id, name)
VALUES
(1, 'Fiction'),
(2, 'Drama'),
(3, 'Mystery');


-- ==========================================
-- 4. BOOKS
-- ==========================================

INSERT INTO BOOK
(book_id, title, price, publish_year,
 author_id, publisher_id, category_id)
VALUES
(1, 'Utopia', 150.00, 2008, 1, 1, 1),
(2, 'The Blue Elephant', 200.00, 2012, 4, 1, 3),
(3, 'Palace Walk', 180.00, 1956, 2, 1, 1),
(4, 'The Thief and the Dogs', 160.00, 1961, 2, 1, 1),
(5, 'Hamlet', 120.00, 1603, 3, 3, 2),
(6, 'Macbeth', 130.00, 1606, 3, 3, 2),
(7, 'The Second World', 145.00, 2008, 1, 2, 1),
(8, '1919', 170.00, 2014, 4, 2, 3),
(9, 'Sample Short Novel', 18.50, 2020, 1, 1, 1),
(10, 'The Tempest', 18.00, 1611, 3, 3, 2);


-- ==========================================
-- 5. MEMBERS
-- ==========================================

INSERT INTO `MEMBER`
(member_id, name, email, join_date)
VALUES
(1, 'Mariam Ali', 'mariam.ali@example.com', '2026-01-10'),
(2, 'Omar Hassan', 'omar.hassan@example.com', '2026-01-15'),
(3, 'Salma Mostafa', 'salma.mostafa@example.com', '2026-02-01'),
(4, 'Youssef Adel', 'youssef.adel@example.com', '2026-02-12'),
(5, 'Nour Ibrahim', 'nour.ibrahim@example.com', '2026-03-05');


-- ==========================================
-- 6. LOANS
-- ==========================================

INSERT INTO LOAN
(loan_id, book_id, member_id, loan_date, return_date)
VALUES
(1, 1, 1, '2026-03-01', '2026-03-10'),
(2, 1, 2, '2026-03-12', '2026-03-20'),
(3, 1, 3, '2026-04-01', NULL),
(4, 2, 1, '2026-03-05', '2026-03-15'),
(5, 2, 2, '2026-04-02', '2026-04-12'),
(6, 3, 2, '2026-03-08', '2026-03-18'),
(7, 3, 3, '2026-04-05', '2026-04-15'),
(8, 4, 4, '2026-03-11', '2026-03-21'),
(9, 5, 1, '2026-03-14', '2026-03-24'),
(10, 6, 2, '2026-03-16', '2026-03-26'),
(11, 7, 4, '2026-04-08', '2026-04-18'),
(12, 8, 1, '2026-04-10', '2026-04-20'),
(13, 4, 1, '2026-04-22', '2026-05-02');


-- ==========================================
-- END OF SEED DATA
-- ==========================================
