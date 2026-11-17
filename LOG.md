# Learning log: Shruthi Thiagarajan

Main repo studied: https://github.com/Saturam-Inc/saturam-agent-framework (EGPT, the agent
framework and the Enterprise GPT retail product).

---

## Day 1: Setup, terminal, git and Python (2026-11-03 to 2026-11-05)

### Checklist

| Task | Status |
|---|---|
| Clone saturam-agent-framework, stay on main | Done |
| Run `./scripts/dev_setup.sh` | Done, with a Windows workaround (below) |
| Activate `.venv` | Done (`.venv\Scripts\Activate.ps1`) |
| Run `pytest product/tests/test_landing_contract.py -q` | Done: **57 passed** in 0.22s |
| Create branch `learning/<name>`, add LOG.md, commit, push | Changed: push to the org repo returned 403, so the log lives in this repo instead |
| 20-line word-count script + two pytest tests | Done: 2 tests pass (`day01_word_count/`) |
| Demo | To do |
| Explain back: three questions | To do |

### What I did, step by step

1. **Cloned** `saturam-agent-framework` to `D:\Shruthi\Projects\saturam-agent-framework` and
   stayed on `main`.
2. **Installed uv** (the Python package manager the project uses) with
   `winget install astral-sh.uv`.
3. **Ran the dev setup.** `dev_setup.sh` creates `.venv` with Python 3.12 and installs three
   packages in editable mode: `egptctl` (CLI), `egpt` (the framework, `libs/agno`) and
   `egpt-retail` (the product, `product/`). 217 packages in total.
4. **Activated the venv**: `.venv\Scripts\Activate.ps1`. The prompt shows `(.venv)`.
5. **Ran the unit test file**: `pytest product/tests/test_landing_contract.py -q`.
   Result: 57 tests ran, 57 passed.
6. **Branch and push**: created `learning/shruthi`, committed LOG.md, and the push failed
   with `403 Write access to repository not granted`. I then deleted the local branch, so
   saturam-agent-framework is back on `main` with no changes, and created this repo
   (`shruthithiagarajan/Learnings`) for my learning work.

### Problems I hit and how I fixed them

| Problem | Cause | Fix | Concept |
|---|---|---|---|
| `./scripts/dev_setup.sh` in PowerShell did nothing | PowerShell does not run `.sh` files; it opens them with the associated app | Run it through Git Bash: `& "D:\Shruthi\Tools\Git\bin\bash.exe" scripts/dev_setup.sh` | Shells: PowerShell vs bash |
| `uv : The term 'uv' is not recognized` right after installing | The terminal kept the PATH from before the install | Reload PATH: `$env:Path = [Environment]::GetEnvironmentVariable("Path","User") + ";" + [Environment]::GetEnvironmentVariable("Path","Machine")`, or restart VS Code | Environment variables, PATH |
| `Distribution not found at: file:///D:/d/Shruthi/...` | Git Bash writes paths as `/d/Shruthi/...`; Windows `uv.exe` read that as `D:\d\Shruthi\...` | Run the install step in PowerShell: `$env:VIRTUAL_ENV="$PWD\.venv"; uv pip install -e "libs\egptctl[dev]" -e "libs\agno[dev]" -e "product[dev]"` | Unix vs Windows paths |
| `docker compose ... up` failed: `dockerDesktopLinuxEngine` not found | Docker Desktop not running; VPN problems with Docker | Not fixed; ran the app without Docker (below) | Services and daemons |
| `git push`: 403 | My account has read but not write access to the org repo | Used my own repo instead | Remotes and permissions |
| `git commit` needs a name and email | git identity not set on this machine | `git config user.name` / `git config user.email` | git config |

### Commands I used

```powershell
# Terminal
cd <dir>; ls; pwd; cat <file>                # move around and read files
Get-Command python                           # which python am I running? (like `which`)
$env:Path -split ';'                         # see PATH, one entry per line

# Python
.venv\Scripts\Activate.ps1                   # activate the venv (Windows; Mac/Linux: source .venv/bin/activate)
python -m egpt_retail.entrypoints --help     # run a module with -m
pytest <file> -q                             # run tests, quiet output

# git
git clone <url>
git branch --show-current
git checkout -b <branch>                     # create and switch to a branch
git add <file>; git commit -m "<message>"
git log --oneline
git push -u origin <branch>
git remote -v                                # where push/pull go
```

### How to run the application

The app has two halves:
- **Frontend**: React + Vite in `frontend/`, served on http://localhost:3000.
- **Backend**: the retail API, `python -m egpt_retail.entrypoints api`, on port 7777.

**Option 1: frontend only (no backend).** Most screens still read built-in sample data from
browser storage.

```powershell
cd D:\Shruthi\Projects\saturam-agent-framework\frontend
npm ci              # first time only
npm run dev         # http://localhost:3000
```

**Option 2: frontend + stub API (no database).** The stub answers every API call with example
data. Verified working on 2026-11-05. Use two terminals.

```powershell
# Terminal 1: backend stub, http://127.0.0.1:7778
cd D:\Shruthi\Projects\saturam-agent-framework
.venv\Scripts\python.exe -m egpt_retail.api.stub

# Terminal 2: frontend, pointed at the stub
cd D:\Shruthi\Projects\saturam-agent-framework\frontend
$env:VITE_API_URL = "http://127.0.0.1:7778"
npm run dev
```

The stub does not serve chat (`POST /agents/playground/runs`). Typing in the Playground gives
"Could not reach the API" until the real API runs.

**Option 3: the real API (needed for chat).** Needs two things I do not have yet:
1. **Postgres with pgvector**, with two databases, `ai` and `egpt_warehouse`. Normally Docker
   provides it (`docker compose -f deploy/compose.yaml up -d postgres`, port 5532). Without
   Docker it must be a hosted Postgres.
2. **Azure OpenAI keys**: `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT`.

```powershell
cd D:\Shruthi\Projects\saturam-agent-framework
$env:EGPT_RETAIL_DB_URL = "postgresql+psycopg://USER:PASS@HOST:5432/ai"
$env:EGPT_RETAIL_WAREHOUSE_DB_URL = "postgresql+psycopg://USER:PASS@HOST:5432/egpt_warehouse"
$env:EGPT_RETAIL_MEMORY_BACKEND = "pgvector"
$env:EGPT_RETAIL_CUSTOMER_SLUG = "northwind"
$env:AZURE_OPENAI_API_KEY = "..."
$env:AZURE_OPENAI_ENDPOINT = "..."
.venv\Scripts\python.exe -m egpt_retail.entrypoints migrate             # once
.venv\Scripts\python.exe -m egpt_retail.entrypoints warehouse-migrate   # once
.venv\Scripts\python.exe -m egpt_retail.entrypoints api --port 7777     # check http://localhost:7777/health
```

Then run the frontend (`npm run dev`) without `VITE_API_URL`; it defaults to
http://localhost:7777. The API does not read a `.env` file by itself; settings must be
environment variables in the terminal that starts it.

### What I learned about the repo

- `libs/agno/egpt/` is the framework, published as the `egpt` package. It must contain no
  retail-specific code.
- `product/egpt_retail/` is the retail product. It uses the framework and holds everything
  retail.
- `frontend/` is the React UI; `deploy/` has the Dockerfile and compose files; `cookbook/`
  has runnable examples.
- `.venv/` is for development (tests, formatting); `.venvs/demo/` is for cookbooks.
- Before any PR, the project runs `./scripts/format.sh` and `./scripts/validate.sh`.

### Word-count script and tests

Files: `day01_word_count/word_count.py` (`count_lines_with_word(path, word)`, case-insensitive,
counts lines not occurrences, rejects an empty word) and `day01_word_count/test_word_count.py`.
Result: **2 passed**.

| Test | What it proves | Bug it would catch |
|---|---|---|
| `test_counts_each_line_once_even_if_word_repeats` | A line with the word twice counts once, and the match ignores case | Counting occurrences instead of lines; missing `ERROR` vs `error` |
| `test_empty_file_and_empty_word` | Empty file gives 0; empty word raises `ValueError` | `""` matching every line and inflating the count |

### Explain back (in my own words)

_To do, written without notes:_

1. What is a virtual environment, and why does this project use one?
2. What is the difference between `git merge` and `git rebase`?
3. What does each of my two tests prove, and what bug would each one catch?
   - See the table in "Word-count script and tests" above.

---

## Day 2: Servers, processes, ports and Docker (2026-11-17)

### Checklist

| Task | Status |
|---|---|
| Read Docker docs, Get started parts 1 to 3 | To do |
| Start Postgres with `./cookbook/scripts/run_pgvector.sh`; read the script and explain every flag | Done (run through Git Bash) |
| Find the container (`docker ps`), its logs (`docker logs pgvector`) and its port (`lsof -i :5532`) | Done (`netstat -ano \| findstr :5532` on Windows) |
| Connect with `psql -h localhost -p 5532 -U ai` (password ai); create a database and a table; insert two rows | Done (`docker exec -it pgvector psql -U ai -d ai`) |
| Stop and start the container: is the table still there, and why? Remove the container and start again: why is it different? | Done (see explain back) |
| Open `deploy/compose.yaml`; list the services, their images and their ports | Done (table below) |

**Demo:** Show the running container, connect with psql, show your table, explain what happens to data on stop vs remove.

### What I did, step by step

1. **Docker running.** Started Docker Desktop (it was the cause of the Day 1 compose failure),
   checked with `docker version` and `docker ps`.
2. **Read `cookbook/scripts/run_pgvector.sh`.** It is one `docker run` command:

   | Part | Meaning |
   |---|---|
   | `-d` | run in the background |
   | `-e POSTGRES_DB=ai`, `POSTGRES_USER=ai`, `POSTGRES_PASSWORD=ai` | database, user and password created on first start (dev only) |
   | `-e PGDATA=/var/lib/postgresql` | where Postgres keeps its files inside the container |
   | `-v pgvolume:/var/lib/postgresql` | named volume mounted at that path, so data lives outside the container |
   | `-p 5532:5432` | host port 5532 forwards to container port 5432 |
   | `--name pgvector` | container name for `docker logs/stop/start` |
   | `agnohq/pgvector:18` | image: Postgres 18 with the pgvector extension |

3. **Started it** with `bash cookbook/scripts/run_pgvector.sh` (Git Bash).
4. **Inspected it:** `docker ps` (container and `0.0.0.0:5532->5432/tcp`), `docker logs pgvector`
   (ready to accept connections), `docker port pgvector`, `netstat -ano | findstr :5532`
   (the Windows version of `lsof -i :5532`).
5. **Connected** inside the container (no local psql): `docker exec -it pgvector psql -U ai -d ai`,
   then created a database `day2`, a table `notes(id, body)` and inserted two rows.
6. **Stop and start:** `docker stop pgvector`, `docker ps -a` (Exited), `docker start pgvector`,
   selected from `notes` again.
7. **Remove and start again:** `docker rm -f pgvector`, `docker volume ls` (`pgvolume` still
   there), ran the script again, selected from `notes` again.

### Commands I used

```powershell
docker version; docker ps; docker ps -a
docker logs pgvector; docker port pgvector
netstat -ano | findstr :5532                 # who listens on port 5532 (Windows)
docker exec -it pgvector psql -U ai -d ai    # psql inside the container
docker stop pgvector; docker start pgvector
docker rm -f pgvector                        # remove the container, keep the volume
docker volume ls
```

```sql
CREATE DATABASE day2;
\c day2
CREATE TABLE notes (id serial PRIMARY KEY, body text);
INSERT INTO notes (body) VALUES ('first row'), ('second row');
SELECT * FROM notes;
```

### `deploy/compose.yaml`: services, images, ports

| Service | Image | Host ports |
|---|---|---|
| postgres | `agnohq/pgvector:18` | 5532 to 5432 |
| migrate | `egpt-retail:dev` (built from `deploy/Dockerfile`) | none, runs once |
| warehouse-migrate | `egpt-retail:dev` | none, runs once |
| api | `egpt-retail:dev` | 7777 to 7777 (`EGPT_RETAIL_API_PORT`) |
| consolidator | `egpt-retail:dev` | none |
| neo4j (profile `full`) | `neo4j:5` | 7474, 7687 |
| redis (profile `full`) | `redis:7-alpine` | 6379 |
| minio (profile `full`) | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | 9000, 9001 |

Compose uses its own volume `egpt-pg` (not `pgvolume`), and its postgres service runs the init
scripts in `deploy/postgres/init`, which create the `egpt_warehouse` database.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. What does `-p 5532:5432` mean? Which number is on your laptop and which is inside the container?
   - 5532 is on my laptop (the host) and 5432 is inside the container. Traffic to `localhost:5532` is forwarded to Postgres in the container.
2. Why did your data survive a stop but not a remove (or did it)? What is a volume?
   - Draft from the script: it survives both. A stopped container keeps its filesystem, and the data is in the named volume `pgvolume`, which is storage outside the container; `docker rm` does not delete named volumes, and the new container mounts the same one. It is lost only if the volume is deleted (`docker volume rm pgvolume`). Check this against what I saw in step 7 and fix this line if it differed.
3. Two services in compose.yaml want the same port. What happens?
   - Draft: only one process can hold a host port, so the second container fails to start with a "port is already allocated" error. That is why `api` has a configurable host port.

**Done when:** You can start, inspect, connect to and stop Postgres without looking anything up.

---

## Day 3: PostgreSQL basics (2026-11-17)

### Checklist

| Task | Status |
|---|---|
| Read Postgres docs, Tutorial chapters 2 and 3 | To do |
| Create `deals(deal_id, stage, amount, created_at, brand)` and `dealers(dealer_id, name, region)`, plus a `dealer_id` on deals | Done (in database `ai`, see problems) |
| Insert 15 to 20 rows by hand, with some NULL amounts and one deal with no dealer | Done: 3 dealers, 18 deals, 3 NULL amounts, 1 deal with no dealer |
| Queries: deals per stage; total amount per brand; deals with no dealer (left join); average amount ignoring NULLs; top 3 brands by amount | Done, all five (plus a HAVING query) |
| Run one query inside a transaction, then ROLLBACK, and show nothing changed | Done: DELETE 7, count 11 inside, 18 after ROLLBACK |

**Demo:** Run each query and explain its result.

### What I did, step by step

Everything in `psql` inside the container (`docker exec -it pgvector psql -U ai -d ai`). The
full SQL is in `day03_postgres_basics/queries.sql`.

1. **Created the tables.** `dealers(dealer_id PK, name, region)` and
   `deals(deal_id serial PK, stage, amount numeric, created_at date, brand, dealer_id REFERENCES dealers)`.
   `amount` and `dealer_id` allow NULL on purpose.
2. **Inserted the data:** 3 dealers and 18 deals (`INSERT 0 3`, `INSERT 0 18`). Deals 6, 10 and 17
   have a NULL amount; deal 11 has no dealer.
3. **Ran the five queries** and the extra HAVING query (results below).
4. **Transaction:** `BEGIN; DELETE ...; SELECT count(*); ROLLBACK; SELECT count(*);`
5. **Index:** created an index on `created_at` and ran `EXPLAIN`.

### Queries and results

| Query | Result |
|---|---|
| Deals per stage | Quotation 7, Closed Won 6, Negotiation 3, Closed Lost 2 (total 18) |
| Total amount per brand | Fryer 24100, Oven 20000, Mixer 19300, Grill 9600 |
| Deals with no dealer (`LEFT JOIN ... WHERE x.dealer_id IS NULL`) | deal 11, Quotation, Fryer |
| `avg(amount)` vs `avg(COALESCE(amount, 0))` | 4866.67 (15 non-NULL rows) vs 4055.56 (all 18 rows) |
| Top 3 brands by amount (`LIMIT 3`) | Fryer, Oven, Mixer |
| Brands with at least 5 deals (`HAVING count(*) >= 5`) | Fryer 5, Oven 5 |
| Transaction: `DELETE FROM deals WHERE stage = 'Quotation'` | `DELETE 7`, count 11 inside, **18 after `ROLLBACK`** |
| `EXPLAIN SELECT * FROM deals WHERE created_at >= '2026-09-15'` | `Seq Scan on deals (cost=0.00..1.23 rows=6)`, the index was not used |

### How each result works

- **Deals per stage:** `GROUP BY stage` makes one group per stage and `count(*)` counts the rows
  in each group. The four counts add up to 18.
- **Total per brand:** `sum(amount)` adds the amounts in each brand group and skips NULLs. The
  three NULL-amount deals are Fryer (6), Oven (10) and Grill (17), so those brands add up lower
  than their row counts suggest.
- **Left join:** `deals LEFT JOIN dealers` keeps every deal and fills the dealer columns with
  NULL when no dealer matches. Filtering `WHERE x.dealer_id IS NULL` then leaves only the
  unmatched deal, 11. An inner join would drop it (17 rows, I did not run this).
- **Average:** `avg` ignores NULLs, so 73000 / 15 = 4866.67. With `COALESCE(amount, 0)` the NULLs
  count as zero and the same sum is divided by 18, giving 4055.56. `count(amount)` (15) vs
  `count(*)` (18) shows the difference.
- **Top 3:** sort the brand totals descending and `LIMIT 3`. Grill (9600) is cut off.
- **HAVING:** `WHERE` filters rows before grouping; `HAVING` filters groups after, so it can use
  `count(*)`.
- **Transaction:** `BEGIN` starts one unit of work; the delete (7 Quotation rows) is only
  visible inside it; `ROLLBACK` throws it away, so the count is back to 18. `COMMIT` would have
  made it permanent.
- **Index and EXPLAIN:** with 18 rows Postgres reads the whole table (Seq Scan) because that is
  cheaper than using the index. The index would pay off on a large table.

### Problems I hit

| Problem | Cause | Fix | Concept |
|---|---|---|---|
| The tables ended up in the project database `ai`, not in `day3` | I typed `\c` with no database name, so psql reconnected to the same database (`You are now connected to database "ai"`) | Use `\c day3`. To clean up `ai`: `DROP TABLE deals, dealers;` there and rerun `queries.sql` | psql meta-commands, database vs table |
| The pasted multi-line INSERT looked garbled in the terminal | Terminal paste echo | Result was still correct (`INSERT 0 18`, counts match) | Always check the row count after an insert |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. Why does the left join return the deal without a dealer, and the inner join does not?
   - A left join keeps every row of the left table (`deals`) and fills the right table's columns with NULL when nothing matches, so deal 11 appears. An inner join keeps only rows with a match on both sides, and `NULL = anything` is never true, so deal 11 is dropped.
2. How does AVG treat NULL? How would you count NULLs as zero instead?
   - `avg` ignores NULLs: it divided by 15, not 18, giving 4866.67. `avg(COALESCE(amount, 0))` counts them as zero and gave 4055.56.
3. What would an index on `created_at` help with?
   - Queries that filter or sort by date, like `WHERE created_at >= ...` or date ranges: Postgres can jump to matching rows instead of reading the whole table. My `EXPLAIN` still showed a Seq Scan because the table has only 18 rows. It does not help other columns and slows inserts slightly.

**Done when:** Every query is written by you and explained.

---

## Day 4: JSON in Postgres, and latest row per key (2026-11-17)

### Checklist

| Task | Status |
|---|---|
| Read Postgres docs, Window Functions tutorial (3.5) | To do |
| Write `deals.ndjson` by hand with made-up data: the same deal several times with different `last_modified`, and one quote as three rows (one per product line) | Written, see `day04_latest_per_key/` (not yet run on Postgres) |
| Load it into `raw_deals(payload jsonb)` with `\copy` or a small Python script you write | Written, see `day04_latest_per_key/` (not yet run on Postgres) |
| Query: how many rows? how many distinct deals? latest stage per deal (window function)? value of each deal at its latest version (sum of price x qty over its lines)? how many deals are Closed Won? | Written, see `day04_latest_per_key/` (not yet run on Postgres) |
| Answer it wrongly on purpose (count Closed Won rows) and write down why the numbers differ | Written, see `day04_latest_per_key/` (not yet run on Postgres) |

**Demo:** Show the file, the raw table, and the right and wrong answers side by side.

### Code and results

Files in `day04_latest_per_key/`: `deals.ndjson` (12 made-up lines, 4 deals), `queries.sql`
(Postgres: `raw_deals`, row and deal counts, latest stage with `ROW_NUMBER`, deal value with
`DENSE_RANK`, right and wrong Closed Won count), `reference.py` (same answers in plain Python),
`test_reference.py` (**5 passed**, including the window query run on sqlite).

| Question | Right answer |
|---|---|
| Rows / distinct deals | 12 / 4 |
| Latest stage | D-1001 Closed Won, D-1002 Quotation, D-1003 Closed Won, D-1004 Closed Lost |
| Deal value at latest version | D-1001 7800, D-1002 9000, D-1003 15000, D-1004 9600 |
| Deals Closed Won (right) vs Closed Won rows (wrong) | 2 vs 4 |

The `queries.sql` file has not been run on a real Postgres here (no Postgres in this
environment); the same logic is checked by the Python reference and by the sqlite test.

### What I learned (study notes)

**JSON vs NDJSON.** Standard JSON wraps all records in one `[ ]` array with commas between
objects and may be pretty-printed over many lines. NDJSON has no outer brackets and no commas:
one complete JSON object per line, and an object must stay on one line.

```json
[ {"deal_id": "D-1001", "price": 1200}, {"deal_id": "D-1002", "price": 5400} ]
```
```
{"deal_id": "D-1001", "price": 1200}
{"deal_id": "D-1002", "price": 5400}
```

Why EnterpriseGPT uses NDJSON: a pull just appends lines (no reopening the file to fix the
closing `]`), and `\copy` or Python can stream millions of lines one at a time without loading
the whole file into memory. Raw landing tables use a `jsonb` column so a record never fails to
load even if a field changes.

**`->` vs `->>` and casting.** For `{"deal_id": "D-1001", "price": 1200, "customer": {"name": "Acme"}, "last_modified": "2026-09-05T08:30:00Z"}`:

| Syntax | Returns | Output |
|---|---|---|
| `payload -> 'customer'` | jsonb | `{"name": "Acme"}` |
| `payload -> 'deal_id'` | jsonb | `"D-1001"` (with JSON quotes) |
| `payload ->> 'deal_id'` | text | `D-1001` |
| `payload -> 'customer' ->> 'name'` | text | `Acme` |
| `(payload ->> 'price')::numeric` | numeric | `1200` |
| `(payload ->> 'last_modified')::timestamptz` | timestamptz | `2026-09-05 08:30:00+00` |

Rules: use `->` for middle steps and `->>` only for the last step (once it is text you cannot
drill further); put parentheses around `(payload ->> 'key')` before `::` because `::` binds
tighter than `->>`; a key with a space is fine inside single quotes
(`payload -> 'customer' -> 'customer name' ->> 'name'`); a missing key gives NULL, not an error.
`->>` always returns text, so cast it to `numeric` before doing maths and to `timestamptz`
before sorting by date.

**Latest row per key.** A source sends the same deal again each time it changes, so counting
rows counts versions, not deals. Think of piles of receipts: `PARTITION BY deal_id` makes one
pile per deal, `ORDER BY last_modified DESC` puts the newest on top, `ROW_NUMBER()` numbers
each pile (1 = newest), and `WHERE rn = 1` keeps the top card. `DISTINCT ON (deal_id)` is the
Postgres-only shortcut for the same thing: sort each deal newest first and keep the first row.
`ROW_NUMBER` does not collapse rows the way `GROUP BY` does. When one version has several
lines with the same `last_modified`, use `DENSE_RANK` so all lines of the newest version stay.

### Problems I hit and how I fixed them

| Problem | Cause | Fix | Concept |
|---|---|---|---|
| `invalid command \Shruthi` after typing `docker cp ...` | I ran a Windows/Docker command inside the psql prompt (`ai=#`) | `\q` to leave psql, run `docker cp` in PowerShell | Which shell am I in |
| `docker cp` itself worked: `Successfully copied 1.46kB ... to pgvector:/tmp/deals.ndjson` | n/a | n/a | `\copy` runs inside the container, so the file must be in the container |
| `ERROR: syntax error at or near "INSERT"` and `raw_deals` had 0 rows | Pasted `\copy` together with the SQL after it; psql ran them as one command (`COPY stage (line) FROM STDIN INSERT INTO ...`) | Run `\copy` alone on its own line, then run the INSERT and the rest | psql meta-commands end at the newline, not at `;` |
| The tables went into `ai` instead of `day4` | Same mistake as Day 3: not switching with `\c day4` | `\c day4` (lowercase), check the prompt says `day4=#`, clear the leftovers from `ai` with `DROP TABLE IF EXISTS raw_deals, stage;` | psql commands are case-sensitive: `\C` is not `\c` |
| `CREATE DATABASE day4` said it already exists | It was created in an earlier attempt | Just `\c day4` | Check before creating |
| `python -m pytest`: "Python was not found" (Microsoft Store shortcut) | The Windows alias is used when no venv is active | Use a venv python or activate one | PATH and App execution aliases |
| `D:\Shruthi\projects\saturam-agent-framework\.venv\Scripts\python.exe` not recognized | That path does not exist on my machine (Day 1 setup was in another place) | Found `D:\Shruthi\Projects\local-postgres\.venv\Scripts\python.exe` with `Get-ChildItem -Recurse -Filter python.exe` | Finding files, absolute paths |
| `No module named pip`, then `No module named pytest` in that venv | The venv was created without pip (typical of uv) | `python -m ensurepip --upgrade` then `python -m pip install pytest`, or `uv pip install pytest` | Virtual environments |

### Status at the time of this entry

- Done: `deals.ndjson` copied into the container; concepts studied; the load mistakes above
  found and understood.
- Still to do and record here: the load into `raw_deals` in `day4` (`COPY 12`, 12 rows), the five
  queries with their results (expected 12 and 4; latest stages; values 7800, 9000, 15000, 9600;
  Closed Won deals 2 vs rows 4), and the pytest run (the venv still needs pytest installed).
  The checklist rows above keep the status "not yet run on Postgres" until then.

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. Walk through your window-function query clause by clause.
   - _To do_
2. Why is counting rows wrong here? Give two different reasons rows repeat.
   - Draft from my data: (a) a deal is sent again each time it changes (D-1001 appears at Quotation and again at Closed Won); (b) one version has several product lines (D-1001 has two lines per version). Counting Closed Won rows gives 4, the real number of deals is 2.
3. If two versions of a deal have exactly the same `last_modified`, which one does your query pick? Is that safe?
   - Draft: the one with the higher `id` (loaded later), because of `ORDER BY ... , id DESC` (D-1004 shows this: Closed Lost wins). It is deterministic but only safe if load order means "newer"; a stricter rule needs another version field.

**Done when:** You can write the latest-per-key query from memory and explain why it is needed.

---

## Day 5: HTTP and APIs (2026-11-17)

### Checklist

| Task | Status |
|---|---|
| Read GitHub REST docs: Using pagination, Rate limits | To do |
| With curl, list issues of a public repo (for example `psf/requests`, `state=all&per_page=5`); with `curl -i` find the rate-limit headers and the Link header | To do |
| Add `since=2026-09-01T00:00:00Z`: what changed? | To do |
| Write a Python function (httpx or requests) that fetches all pages for a `since` date, follows the Link header, and retries with a growing wait on 429 or 5xx | Done, standard library only: `day05_paging/github_issues.py` |
| Run the function for one week of issues; show pages fetched and rate-limit headers | Done: 16 issues in 6 pages; rate-limit headers not shown (see below) |
| Write tests for the paging logic by hand, using a fake response | Done: 5 tests pass |

**Demo:** Run the function for one week of issues; show how many pages it fetched and the rate-limit headers.

### Code and results

`day05_paging/github_issues.py`: `next_url` reads `rel="next"` from the Link header;
`get_with_retry` retries 429 and 5xx with waits of 1, 2, 4 ... seconds (or the `Retry-After`
value) and fails straight away on 401/403/404; `fetch_issues_since(repo, since)` loops until
there is no next link. The HTTP call is injected so tests use fake responses. The token comes
from `GITHUB_TOKEN`, never from code. `test_github_issues.py`: **5 passed**.

### Demo run (`day05_paging/demo.py`)

I ran the function for one week of `psf/requests` issues: `since=2026-11-10T00:00:00Z`, `per_page=3`,
on 2026-11-17. Output:

```
issues: 16 pages fetched: 6
7650 open 2026-11-16T06:57:05Z Add test coverage for SHA-1 Digest authentication and query
7649 open 2026-11-16T20:32:35Z [Bug] RequestsCookieJar - multiple_domains() returns incorre
7648 open 2026-11-17T06:12:06Z HTTPDigestAuth fails to select auth when qop contains a comm
rate limit headers:
```

| What the output shows | Explanation |
|---|---|
| `issues: 16`, `pages fetched: 6` | With 3 per page, 16 issues need 6 pages: five full pages of 3 and a last page with 1. The loop stopped because the last response had no `rel="next"` link. |
| Issue numbers 7650, 7649, 7648 | The endpoint sorts by created date, newest first (the default), so the numbers go down. |
| `updated_at` is not in order (11-16, 11-16, 11-17) | `since` filters by **updated** time but the sort is by **created** time, so an older issue that was updated recently still appears. |
| All three `open` | `state=all` asks for open and closed, and the three newest happen to be open. |
| Empty "rate limit headers" | The script requested `https://github.com` (the website), which does not send `x-ratelimit-*` headers. Those headers come on API responses (`api.github.com`). To show them, read them from an issues response (`curl.exe -i ...` or `fetch` returns headers), or call `https://api.github.com/rate_limit`. This part of the demo still has to be redone. |

Note that this endpoint also returns pull requests (items with a `pull_request` key), so "issues"
here can include PRs.

Status: the paging, the Link-header loop and the retry code are demonstrated by this run and by
the 5 unit tests. Not recorded yet: the two curl steps (headers from `curl.exe -i`, and what
changed when adding `since`), a rate-limit header printout, and my own pytest output.

### What I learned (study notes)

**curl.** `curl` sends an HTTP request from the terminal and shows the response, like a browser
without a screen. It is quick for testing an API without writing a script, and it shows raw
headers (status, `Link`, `X-RateLimit-*`) that a browser hides.

| Flag | Name | What it does |
|---|---|---|
| `-i` | include | print the response headers and the body |
| `-I` | head | send a HEAD request, print only the headers |
| `-H` | header | send a custom header, e.g. `-H "Authorization: Bearer <token>"` |
| `-X` | request | choose the method (GET, POST, DELETE); GET is the default |

In Windows PowerShell, `curl` is a shortcut for `Invoke-WebRequest`, which behaves differently
and fails on flags like `-i`. Typing `curl.exe` runs the real curl (`C:\Windows\System32\curl.exe`).

**What an API looks like.** An API is a structured way for one program to ask another for data
or actions over HTTP. Instead of a web page it returns structured text, usually JSON. Every call
has a request and a response.

```http
GET https://api.example.com/weather?city=Bengaluru&units=metric HTTP/1.1
Authorization: Bearer <token>
Accept: application/json
```
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Remaining: 99

{"city": "Bengaluru", "temperature_c": 24.5, "condition": "Partly Cloudy", "humidity_percent": 68}
```

- Request: the method (`GET` reads, `POST` creates), the URL with query parameters (the filters),
  and headers (who I am, what format I want).
- Response: the status line (`200 OK`), headers (metadata such as `Content-Type` and the rate-limit
  counters), and the JSON body that the code parses with `response.json()`.

**Testing error handling (401, 429, 500) without running the app.**

1. *Real status codes with curl.* A test service such as httpbin returns whatever status is in the
   URL (my note had lost the paths, the corrected commands are):
   ```powershell
   curl.exe -I "https://httpbin.org/status/401"   # unauthorized
   curl.exe -I "https://httpbin.org/status/429"   # too many requests
   curl.exe -I "https://httpbin.org/status/500"   # server error
   curl.exe -I -H "Authorization: Bearer fake_invalid_token" "https://api.github.com/user"   # real 401 from GitHub
   ```
2. *A fake `fetch` in the unit test (best practice).* My `fetch_issues_since(..., fetch=http_fetch)`
   takes the HTTP call as a parameter (dependency injection), so a test passes a fake that returns
   429 first and 200 next. It runs in milliseconds with no internet and no waiting on real rate
   limits. That is what `test_github_issues.py` does with a scripted list of responses.
3. *If the code calls a library directly:* `httpx.MockTransport(handler)` for httpx, or
   `unittest.mock.patch` (or the `responses` / `respx` libraries) for requests and urllib.

**Checking an API key on its own.** Test the key with one small request instead of running the
whole app. With the key in `.env` (never in code or git), either use `curl.exe` against
`https://api.anthropic.com/v1/messages` with the headers `x-api-key`, `anthropic-version` and
`content-type: application/json` and a tiny body (`max_tokens` 10, one short user message), or run
a short Python script that reads the key from the environment (loaded from `.env`) so it does not
land in the terminal history. Reading the result:

| Result | Meaning |
|---|---|
| 200 with an assistant reply | key is valid and the account can make requests |
| 401 `authentication_error` | typo, extra spaces or quotes in `.env`, or a revoked key |
| 400 about the credit balance | key is valid but the account needs credits |
| 429 | key works but the rate limit was hit |

### Corrections I made when writing these notes up

| In my study notes | Fixed here | Why |
|---|---|---|
| `curl.exe -I "https://httpbin.org"` listed three times for 401, 429 and 500 | `.../status/401`, `/status/429`, `/status/500` | The status code goes in the URL path; without it all three are the same request |
| `https://github.com` used to test GitHub rate-limit headers and a fake token | `https://api.github.com/...` | github.com is the website; the API and its `X-RateLimit-*` headers are on api.github.com (same cause as the empty header list in my demo run) |
| `https://anthropic.com` for the key test | `https://api.anthropic.com/v1/messages` | The Messages API lives on `api.anthropic.com`; the model name in the request should be whatever the project is configured to use |
| Example `fake_fetch(url, headers=None)` returns `(200, {}, [ {...} ])` | A fake must return the same shape as `http_fetch`: `(status, headers, body_text)`, and the body is a JSON **string** (`json.dumps([...])`) | `fetch_issues_since` calls `json.loads(body)`, so a Python list as the body would fail |

### Study notes status

The study notes are done. The explanations of the three explain-back questions are drafts to
re-read. Hands-on results still to record are listed in the "Status" line above (curl runs, the
rate-limit header printout, my own pytest run).

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. What does a 429 mean and what should a client do? What about 401?
   - Draft: 429 = too many requests; wait (the `Retry-After` value or a growing delay) and retry. 401 = not authenticated; retrying cannot help, so fix the token. My code retries 429/5xx and raises on 401.
2. How does your code know there is another page?
   - The response has a `Link` header with a `rel="next"` URL; when it is missing, that was the last page.
3. Why is `since` useful when you pull the same source every day?
   - Each day only items changed after the last watermark are fetched, so less data, fewer requests and less rate-limit use.

**Done when:** Your function and its tests are your own and you can explain the retry logic.

> **Week 1 check:** short SQL test on the Day 4 data, and a 15-minute explain-back of two days chosen by the reviewer.

---

## Day 6: How EnterpriseGPT is built (date)

### Checklist

| Task | Status |
|---|---|
| Read CLAUDE.md, CONTRIBUTING.md and ARCHITECTURE.md, and the prompt engineering guide of your model provider | To do |
| One sentence for each folder: `libs/agno/egpt`, `product/egpt_retail`, `frontend`, `cookbook`, `deploy`, `scripts` | To do |
| In `libs/agno/egpt/agent/`, find where an agent sends its messages to the model; write down the file and function | To do |
| Draw the data flow on one page in your own words; mark where a model runs and where it must not | To do |

**Demo:** Present your folder map and drawing in 10 minutes.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. What belongs in `libs/agno/egpt/` and what in `product/`? Why keep them apart?
   - _To do_
2. What is a token, and why does a long conversation cost more?
   - _To do_
3. Why must a KPI number never come from a model's answer?
   - _To do_

**Done when:** You can find your way around the repository and explain the flow without notes.

---

## Day 7: Your first agent (date)

### Checklist

| Task | Status |
|---|---|
| Read `cookbook/00_quickstart/README.md`, `cookbook/02_agents/README.md` and the Pydantic Models docs | To do |
| Set up the quickstart; run `agent_with_structured_output.py` and `agent_with_typed_input_output.py` (switch the model class if your key is for another provider; note what else changed). Key goes in `.env`, never in code | To do |
| Turn on debug output and read one full run: messages sent, model response, tokens used | To do |
| Write your own agent that takes one Day 4 deal as JSON and returns a typed summary (deal id, latest stage, value, one-line note) through `output_schema` | To do |
| Test parsing and validation by hand with a fixed made-up response; tests never call the model | To do |

**Demo:** Run your agent on three deals and walk through one debug trace.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. What does `output_schema` change in what the model is asked to do? What happens if the model returns something invalid?
   - _To do_
2. Where does your key come from at run time? Why not in the code?
   - _To do_
3. Why should tests not call the model?
   - _To do_

**Done when:** Your agent and its tests are your own and you can explain the trace.

---

## Day 8: Tools: letting the agent act (date)

### Checklist

| Task | Status |
|---|---|
| Read `cookbook/00_quickstart/agent_with_tools.py` and `cookbook/02_agents/04_tools/` | To do |
| Write a `run_sql(query)` tool over your Day 4 data: one SELECT only, refuses anything else, caps rows; connect as a read-only database user you create | Guard written: `day08_sql_guard/sql_guard.py`; tool wiring and read-only DB user still to do |
| Give it to an agent whose instructions describe `raw_deals`; ask: how many deals are Closed Won? what is the total value of open deals? | To do |
| Compare with your Day 4 answers; if it counts rows instead of deals, change the instructions or tool description and record what worked | To do |
| Tests by hand for the guard: a DELETE, two statements in one string, an allowed SELECT | Done: 10 tests pass |

**Demo:** Show the tool calls in the trace, the right answer, and the guard refusing a write.

### Code and results

`day08_sql_guard/sql_guard.py` `check_select(query, max_rows)`: strips one trailing `;`,
rejects comments and a second statement, requires `SELECT`/`WITH`, rejects write and risky
keywords (outside string literals), rejects `INTO` and `FOR UPDATE`, and wraps the query as
`SELECT * FROM (...) LIMIT n` so the cap holds whatever LIMIT the model wrote.
`test_sql_guard.py`: **10 passed** (DELETE, two statements, data-modifying CTE, `SELECT INTO`,
comment, UPDATE, empty, an allowed select, keywords inside a string).

Not done: giving the guard to an agent (needs a model key) and the read-only database user
(needs Postgres). The guard is only layer one; the read-only user is layer two. The project
has its own guard in `product/egpt_retail/app/sql_guard.py` (sqlglot based) to compare with.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. Walk through one tool call: who decides to call it, who runs it, and what does the model see?
   - _To do_
2. Why a read-only database user as well as your guard?
   - Draft: the guard checks text and a clever query may slip through; the database role enforces "no writes" itself, whatever the text says.
3. The agent gave a wrong number. How do you find out why?
   - _To do_

**Done when:** The agent answers both questions correctly from the tool, and the guard tests pass.

---

## Day 9: Knowledge and memory (date)

### Checklist

| Task | Status |
|---|---|
| Read `cookbook/07_knowledge/01_getting_started/` (`01_basic_rag.py`, `02_agentic_rag.py`), `cookbook/00_quickstart/agent_with_memory.py`, `agent_with_storage.py` and `cookbook/11_memory/01_agent_with_memory.py` | To do |
| Run basic and agentic RAG against the project's pgvector with the embedder your mentor names; note chunks stored and chunks retrieved for one question | To do |
| Write a markdown glossary of 8 to 10 definitions for your deals data (open, won, deal value...) and load it as knowledge for your Day 8 agent | To do |
| Ask questions that need both a definition and the data; check the agent uses the definition | To do |
| Add storage so a conversation survives a restart; show a second session remembers the first | To do |

**Demo:** Show a question answered from the glossary and the data, with the retrieved chunks.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. What is an embedding? What does chunk size change?
   - _To do_
2. When should a fact go in knowledge, in memory, or in the instructions?
   - _To do_
3. The agent answered from the glossary, but the glossary was wrong. How would you catch that?
   - _To do_

**Done when:** Your agent uses the glossary correctly and you can explain what was retrieved and why.

---

## Day 10: Teams, workflows and a person in the loop (date)

### Checklist

| Task | Status |
|---|---|
| Read `cookbook/00_quickstart/multi_agent_team.py`, `sequential_workflow.py`, `human_in_the_loop.py` and `cookbook/04_workflows/01_basic_workflows/` | To do |
| Build a two-step workflow: step 1 your Day 8 agent answers a question; step 2 a writer agent turns it into a short weekly note | To do |
| Add an approval: the note is saved to a file only after a person approves it | To do |
| Run the same question through a team; note what changed in cost, number of steps and control | To do |

**Demo:** Run the workflow, approve once and reject once.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. Why is a workflow easier to test than a team?
   - _To do_
2. Where did you put the approval, and what happens when it is rejected?
   - _To do_
3. Why is creating an agent inside a loop a problem?
   - _To do_

**Done when:** The workflow runs, the approval works both ways, and you can explain the trade-off with a team.

> **Week 2 check:** 20-minute explain-back of Day 8 to 10 code, and a short quiz on tools, retrieval and memory.

---

## Day 11: Data in: contracts, raw and clean (date)

### Checklist

| Task | Status |
|---|---|
| Read `LANDING_CONTRACT.md` and `LOAD_CONTRACT.md`; learn watermarks and append-only storage | To do |
| Start Postgres: `docker compose -f deploy/compose.yaml up -d postgres` | To do |
| Run `.venv/bin/python cookbook/94_retail/C01_landing_contract.py` | To do |
| Run `R04_landing_to_silver.py` with `EGPT_RETAIL_WAREHOUSE_DB_URL=postgresql+psycopg://ai:ai@localhost:5532/egpt_warehouse` | To do |
| Pick one fixture record; find it in its file under `contracts/_fixtures/landing/`, in `landing.raw_row`, and in its silver table; find the SQL file in `warehouse/sql/conform/` that moved it | To do |

**Demo:** Show the same record in all three places and the SQL that moved it.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. What happens if the same file is loaded twice? Show where the code prevents duplicates.
   - _To do_
2. What is a defect in this pipeline, and what happens to a bad row?
   - _To do_
3. Why must a watermark move only after the write succeeds?
   - _To do_

**Done when:** You can trace a record without help.

---

## Day 12: Meaning: the semantic layer and KPIs (date)

### Checklist

| Task | Status |
|---|---|
| Read Neo4j Getting started with Cypher, `docs/plan/domain-knowledge-layers.md` and `cookbook/94_retail/README.md` | To do |
| Run `K03_ontology.py`, `K04_metadata_harvest.py`, `K05_semantic_graph.py`, then `K11_kpi_registry_and_feasibility.py` (see each file's header for what it needs; use `.venvs/demo`) | To do |
| In the Neo4j browser write three Cypher queries over what K05 wrote: list the entities; show the attributes of one; show how two entities join | To do |
| For one KPI from K11 write down its formula, the entities it uses, and why it is feasible or not | To do |

**Demo:** Show your three queries and explain your KPI.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. What does the semantic layer know that the clean tables do not?
   - _To do_
2. What makes a KPI not feasible?
   - _To do_
3. Why does an agent suggest KPIs but never compute them?
   - _To do_

**Done when:** You can explain the path from a clean table to a KPI on a dashboard.

---

## Day 13: Quality and how we ship (date)

### Checklist

| Task | Status |
|---|---|
| Read `cookbook/09_evals/README.md`, `accuracy/accuracy_with_given_answer.py`, `accuracy/accuracy_with_tools.py`; the PR template; `cookbook/08_learning/`; `deploy/Dockerfile`, `deploy/compose.yaml`, overview of `deploy/AZURE_CUTOVER.md` | To do |
| Write an evaluation set of 10 questions with expected answers over your deals data; run it against your Day 8 and 9 agent with an accuracy eval; record the score | To do |
| Open a practice PR from your learning branch using the template; `./scripts/format.sh` and `./scripts/validate.sh` must pass; your buddy reviews it | To do |

**Demo:** Show the eval results and your PR with its review.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. Your eval scored 7 out of 10. What do you look at first?
   - _To do_
2. Why does an agent acting as judge need its own checks?
   - _To do_
3. What does `validate.sh` catch that your tests do not?
   - _To do_

**Done when:** Your eval runs and you can explain each failure; your PR passes format and validate.

---

## Days 14 and 15: Capstone, ask your data (date)

### Checklist

| Task | Status |
|---|---|
| Pull: reuse the Day 5 function to pull issues of one public repo changed since a watermark; write each pull as an NDJSON file, refusing to overwrite an existing name; store the watermark in Postgres and advance it only after the file is written | To do |
| Raw and clean: load files into `raw.github_issue` (file path, line number, pulled at, record key, payload jsonb); loading the same file twice inserts nothing; create view `clean.issue` with one row per issue, latest version, typed columns | To do |
| Checks: one row per issue in clean; distinct raw keys equal clean rows; no issue closed before it was created; make one fail on purpose with a bad record | To do |
| KPIs in SQL, no model: issues closed per week and median days to close, last 8 weeks | To do |
| Agent: read-only SQL tool over `clean` plus a knowledge base of the KPI definitions; every number must come from the tool | To do |
| Evaluation: 10 questions with expected answers; run it and report the score | To do |
| README and TEST_LOG in the cookbook style | To do |

**Demo:** 30 minutes live, end to end: pull, files, raw, clean, checks, KPIs, agent, evaluation; then questions on any line. Learning log: what I know now that I did not three weeks ago.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. How does your load stay safe to re-run?
   - _To do_
2. Why does the KPI need the clean layer? What would change if an issue were reopened?
   - _To do_
3. Show one question the agent got wrong and explain why.
   - _To do_

**Done when:** A second run pulls only new or changed issues; the load re-runs without duplicates; the checks fail on bad data; the agent's numbers come from the tool; the evaluation score is reported and explained.

