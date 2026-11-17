-- Day 3: PostgreSQL basics. All data is made up.
-- Run with: docker exec -it pgvector psql -U ai -d ai
-- Note: when I ran this I typed a bare \c, so everything was created in database "ai",
-- not in day3. Use \c day3 (below) to keep exercise tables out of the project database.

CREATE DATABASE day3;
\c day3

CREATE TABLE dealers (
    dealer_id integer PRIMARY KEY,
    name      text NOT NULL,
    region    text NOT NULL
);

CREATE TABLE deals (
    deal_id    serial PRIMARY KEY,
    stage      text NOT NULL,
    amount     numeric,                 -- NULL allowed on purpose
    created_at date NOT NULL,
    brand      text NOT NULL,
    dealer_id  integer REFERENCES dealers (dealer_id)   -- NULL allowed: deal with no dealer
);

INSERT INTO dealers VALUES
 (1, 'Apex Traders', 'North'), (2, 'Birch Retail', 'South'), (3, 'Cedar Supply', 'East');

INSERT INTO deals (stage, amount, created_at, brand, dealer_id) VALUES
 ('Quotation',   1200, '2026-09-01', 'Fryer', 1),
 ('Quotation',   5400, '2026-09-02', 'Oven',  1),
 ('Closed Won',  7800, '2026-09-05', 'Oven',  1),
 ('Negotiation',  800, '2026-09-03', 'Mixer', 2),
 ('Closed Won', 15000, '2026-09-06', 'Mixer', 2),
 ('Quotation',   NULL, '2026-09-07', 'Fryer', 2),
 ('Closed Lost', 9600, '2026-09-04', 'Fryer', 3),
 ('Quotation',   2400, '2026-09-08', 'Grill', 3),
 ('Closed Won',  3300, '2026-09-09', 'Grill', 3),
 ('Negotiation', NULL, '2026-09-10', 'Oven',  1),
 ('Quotation',   4500, '2026-09-11', 'Fryer', NULL),
 ('Closed Won',  6100, '2026-09-12', 'Oven',  2),
 ('Closed Lost', 2000, '2026-09-13', 'Mixer', 1),
 ('Negotiation', 3900, '2026-09-14', 'Grill', 2),
 ('Closed Won',  8800, '2026-09-15', 'Fryer', 3),
 ('Quotation',   1500, '2026-09-16', 'Mixer', 3),
 ('Closed Won',  NULL, '2026-09-17', 'Grill', 1),
 ('Quotation',    700, '2026-09-18', 'Oven',  2);

-- Q1: deals per stage
SELECT stage, count(*) FROM deals GROUP BY stage ORDER BY count(*) DESC;

-- Q2: total amount per brand (sum skips NULLs)
SELECT brand, sum(amount) AS total FROM deals GROUP BY brand ORDER BY total DESC;

-- Q3: deals with no dealer (left join keeps unmatched deals, dealer columns are NULL)
SELECT d.deal_id, d.stage, d.brand
FROM deals d LEFT JOIN dealers x ON x.dealer_id = d.dealer_id
WHERE x.dealer_id IS NULL;

-- Q4: average amount ignoring NULLs vs counting NULLs as zero
SELECT avg(amount) AS avg_ignoring_null,
       avg(COALESCE(amount, 0)) AS avg_nulls_as_zero,
       count(*) AS all_rows, count(amount) AS non_null_rows
FROM deals;

-- Q5: top 3 brands by amount
SELECT brand, sum(amount) AS total FROM deals GROUP BY brand ORDER BY total DESC LIMIT 3;

-- Extra: HAVING
SELECT brand, count(*) FROM deals GROUP BY brand HAVING count(*) >= 5;

-- Transaction: delete inside, then roll back
BEGIN;
DELETE FROM deals WHERE stage = 'Quotation';
SELECT count(*) FROM deals;      -- 11 inside the transaction
ROLLBACK;
SELECT count(*) FROM deals;      -- 18 again

-- Index on created_at
CREATE INDEX deals_created_at_idx ON deals (created_at);
EXPLAIN SELECT * FROM deals WHERE created_at >= '2026-09-15';
