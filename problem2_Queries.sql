USE registration;

-- F2.2

SELECT
    B.book_id,
    B.title,
    B.price,
    B.publish_year,
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

ORDER BY B.title ASC;


-- ==========================================
-- F2.3 - REPORTS
-- ==========================================

-- F2.3 (a)

SELECT
    C.category_id,
    C.name AS category_name,
    COUNT(B.book_id) AS total_books,
    AVG(B.price) AS average_price

FROM CATEGORY C

LEFT JOIN BOOK B
    ON C.category_id = B.category_id

GROUP BY
    C.category_id,
    C.name;


-- F2.3 (b)

SELECT
    A.author_id,
    A.name AS author_name,
    COUNT(B.book_id) AS total_books

FROM AUTHOR A

INNER JOIN BOOK B
    ON A.author_id = B.author_id

GROUP BY
    A.author_id,
    A.name

HAVING COUNT(B.book_id) >= 2;


-- F2.3 (c)

SELECT
    SUM(price) AS total_price,
    MIN(price) AS smallest_price,
    MAX(price) AS largest_price

FROM BOOK;


-- ==========================================
-- F2.4 - LOANS
-- ==========================================

-- F2.4 (a)

SELECT
    L.loan_id,
    B.title AS book_title,
    M.name AS member_name,
    L.loan_date

FROM LOAN L

INNER JOIN BOOK B
    ON L.book_id = B.book_id

INNER JOIN `MEMBER` M
    ON L.member_id = M.member_id

WHERE L.return_date IS NULL;


-- F2.4 (b)

SELECT
    M.member_id,
    M.name,
    M.email

FROM `MEMBER` M

LEFT JOIN LOAN L
    ON M.member_id = L.member_id

WHERE L.loan_id IS NULL;


-- F2.4 (c)

SELECT
    B.book_id,
    B.title,
    B.price

FROM BOOK B

LEFT JOIN LOAN L
    ON B.book_id = L.book_id

WHERE L.loan_id IS NULL;


-- ==========================================
-- F2.5 - MOST BORROWED
-- ==========================================

-- F2.5 (a)

SELECT
    B.book_id,
    B.title,
    COUNT(L.loan_id) AS total_loans

FROM BOOK B

INNER JOIN LOAN L
    ON B.book_id = L.book_id

GROUP BY
    B.book_id,
    B.title

ORDER BY
    total_loans DESC,
    B.title ASC

LIMIT 3;


-- F2.5 (b)

SELECT
    M.member_id,
    M.name,
    COUNT(L.loan_id) AS total_loans

FROM `MEMBER` M

INNER JOIN LOAN L
    ON M.member_id = L.member_id

GROUP BY
    M.member_id,
    M.name

ORDER BY
    total_loans DESC,
    M.name ASC

LIMIT 1;

-- ==========================================
-- F2.6 - AUTHORS AND BOOKS
-- ==========================================

-- F2.6 (a)

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

ORDER BY A.name ASC;


-- F2.6 (b)

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

ORDER BY B.title ASC;
