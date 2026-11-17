-- Day 4: NDJSON in Postgres and "latest row per key". All data is made up.
-- Load: \copy needs one json per line; the staging trick below uses a text column.

CREATE TABLE raw_deals (
    id      bigserial PRIMARY KEY,      -- load order, used as a tie-break
    payload jsonb NOT NULL
);

CREATE TEMP TABLE stage (line text);
\copy stage (line) FROM 'deals.ndjson'
INSERT INTO raw_deals (payload) SELECT line::jsonb FROM stage ORDER BY ctid;

-- Q1: how many rows?                       -> 12
SELECT count(*) FROM raw_deals;

-- Q2: how many distinct deals?             -> 4
SELECT count(DISTINCT payload->>'deal_id') FROM raw_deals;

-- Q3: latest stage per deal (window function). Newest last_modified wins; if two
-- versions have the same last_modified the one loaded later (higher id) wins.
SELECT deal_id, stage
FROM (
    SELECT payload->>'deal_id' AS deal_id,
           payload->>'stage'   AS stage,
           ROW_NUMBER() OVER (
               PARTITION BY payload->>'deal_id'
               ORDER BY (payload->>'last_modified')::timestamptz DESC, id DESC
           ) AS rn
    FROM raw_deals
) t
WHERE rn = 1
ORDER BY deal_id;

-- Q4: value of each deal at its latest version. A version has several lines, all
-- with the same last_modified, so keep every row of the newest version (rank 1)
-- and sum price * qty over them.
SELECT deal_id, sum(price * qty) AS deal_value
FROM (
    SELECT payload->>'deal_id'                AS deal_id,
           (payload->>'price')::numeric       AS price,
           (payload->>'qty')::numeric         AS qty,
           DENSE_RANK() OVER (
               PARTITION BY payload->>'deal_id'
               ORDER BY (payload->>'last_modified')::timestamptz DESC
           ) AS rnk
    FROM raw_deals
) t
WHERE rnk = 1
GROUP BY deal_id
ORDER BY deal_id;

-- Q5 (right): how many deals are Closed Won? -> 2 (D-1001, D-1003)
SELECT count(*) FROM (
    SELECT payload->>'stage' AS stage,
           ROW_NUMBER() OVER (
               PARTITION BY payload->>'deal_id'
               ORDER BY (payload->>'last_modified')::timestamptz DESC, id DESC
           ) AS rn
    FROM raw_deals
) t
WHERE rn = 1 AND stage = 'Closed Won';

-- Q5 (wrong, on purpose): count rows with stage Closed Won -> 4, not 2.
SELECT count(*) FROM raw_deals WHERE payload->>'stage' = 'Closed Won';

-- Same as Q3 with DISTINCT ON (Postgres only):
-- SELECT DISTINCT ON (payload->>'deal_id') payload->>'deal_id' AS deal_id, payload->>'stage' AS stage
-- FROM raw_deals
-- ORDER BY payload->>'deal_id', (payload->>'last_modified')::timestamptz DESC, id DESC;
