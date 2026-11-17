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
| 20-line word-count script + two pytest tests | To do |
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

_To do: `word_count.py`, `test_word_count.py`, and what each test checks._

### Explain back (in my own words)

_To do, written without notes:_

1. What is a virtual environment, and why does this project use one?
2. What is the difference between `git merge` and `git rebase`?
3. What does each of my two tests prove, and what bug would each one catch?

---


## Day 2: Servers, processes, ports and Docker (date)


### Checklist

| Task | Status |
|---|---|
| Read Docker docs (Get started, parts 1 to 3) | To do |
| Run `./cookbook/scripts/run_pgvector.sh` and document every flag in it | To do |
| Inspect the container (`docker ps`), logs (`docker logs pgvector`), port (`lsof -i :5532`) | To do |
| Connect with `psql -h localhost -p 5532 -U ai`, create a DB and table, insert 2 rows | To do |
| Stop and restart the container, check the data persists; remove it and restart, note the difference | To do |
| Inspect `deploy/compose.yaml`: list services, images and port mappings | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Explain `-p 5532:5432`, volumes, stop vs remove, and port conflicts._


## Day 3: PostgreSQL basics (date)


### Checklist

| Task | Status |
|---|---|
| Read Postgres docs (Tutorial, chapters 2 and 3) | To do |
| Create `deals` and `dealers` tables | To do |
| Insert 15 to 20 rows by hand (some NULL amounts, one deal with no dealer) | To do |
| Queries: deals per stage, total per brand, deals with no dealer (LEFT JOIN), average ignoring NULLs, top 3 brands | To do |
| Run a change inside BEGIN; ... ROLLBACK; and confirm nothing persisted | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Explain LEFT vs INNER JOIN, NULLs in AVG, and an index on `created_at`._


## Day 4: JSON in Postgres and latest row per key (date)


### Checklist

| Task | Status |
|---|---|
| Read Postgres docs (Window Functions, section 3.5) | To do |
| Create synthetic `deals.ndjson` with duplicate versions and multi-line quotes | To do |
| Load into `raw_deals(payload jsonb)` | To do |
| Queries: row count vs distinct deals, latest stage per deal with ROW_NUMBER(), deal value at latest version, distinct Closed Won deals | To do |
| Run the deliberately wrong Closed Won count and write down why the numbers differ | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Compare right vs wrong output; walk through the window function and tie-breaking on `last_modified`._


## Day 5: HTTP and APIs (date)


### Checklist

| Task | Status |
|---|---|
| Read GitHub REST docs (pagination, rate limits) | To do |
| `curl -i` and inspect the rate-limit and `Link` headers | To do |
| Try the `since` parameter and note what changes | To do |
| Python function that follows `Link` pages and backs off on 429 and 5xx | To do |
| Hand-written unit tests for the pagination logic using fake responses | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Explain 429 vs 401, how pagination is detected, and what `since` does._


### Week 1 checkpoint

_To do: SQL test on the Day 4 data, then a 15-minute explain-back of two chosen days._


## Day 6: How EnterpriseGPT is built (date)


### Checklist

| Task | Status |
|---|---|
| Read CLAUDE.md, CONTRIBUTING.md, ARCHITECTURE.md and the model provider's prompt guide | To do |
| One-sentence summary per top-level folder | To do |
| Find the file and function in `libs/agno/egpt/agent/` where messages go to the model | To do |
| Draw the end-to-end data flow, marking where models run and where they never run | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: 10-minute walkthrough: framework vs product, tokens, deterministic KPIs._


## Day 7: Your first agent (date)


### Checklist

| Task | Status |
|---|---|
| Read the quickstart and agents READMEs and the Pydantic Models docs | To do |
| Set up `.env` with the mentor-provided key (never commit it); run the two structured-output examples | To do |
| Turn on debug output; read the message trace and token usage | To do |
| Build an agent that returns a typed deal summary via `output_schema` | To do |
| Hand-written tests for Pydantic parsing with fixed mock responses (no live LLM) | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Explain `output_schema`, `.env` security, and why tests mock the model._


## Day 8: Tools: letting the agent act (date)


### Checklist

| Task | Status |
|---|---|
| Read `agent_with_tools.py` and `cookbook/02_agents/04_tools/` | To do |
| Create a read-only Postgres user | To do |
| Build a `@tool` `run_sql(query)` allowing one SELECT and capping rows | To do |
| Attach it to an agent with the `raw_deals` schema; ask for Closed Won count and open deal value | To do |
| Tune instructions until it dedupes and matches the Day 4 SQL | To do |
| Hand-written tests for the guard (reject DELETE, reject multiple statements, allow SELECT) | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Explain defense in depth: DB user plus code guard._


## Day 9: Knowledge and memory (date)


### Checklist

| Task | Status |
|---|---|
| Read the knowledge getting-started and memory cookbooks | To do |
| Run basic and agentic RAG on pgvector; note chunk counts and retrieved chunks | To do |
| Write a Markdown glossary of 8 to 10 terms and load it as knowledge | To do |
| Ask questions that need both the glossary and the SQL tool | To do |
| Persist session history and check recall across restarts | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Explain embeddings, chunk size, and knowledge vs memory vs instructions._


## Day 10: Teams, workflows and human-in-the-loop (date)


### Checklist

| Task | Status |
|---|---|
| Read the multi-agent team, sequential workflow and human-in-the-loop examples | To do |
| Build a 2-step workflow: SQL/knowledge agent, then a writer agent for a weekly note | To do |
| Add a human approval gate before saving the note | To do |
| Run the same task as a Team; compare cost, step count and control | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Show approve and reject paths; workflow vs team; why agents are not created in loops._


### Week 2 checkpoint

_To do: 20-minute explain-back of Days 8 to 10 and a short quiz on tools, retrieval and memory._


## Day 11: Data in: contracts, raw and clean (date)


### Checklist

| Task | Status |
|---|---|
| Read LANDING_CONTRACT.md and LOAD_CONTRACT.md | To do |
| Start Postgres: `docker compose -f deploy/compose.yaml up -d postgres` | To do |
| Run `cookbook/94_retail/C01_landing_contract.py` | To do |
| Run `cookbook/94_retail/R04_landing_to_silver.py` with `EGPT_RETAIL_WAREHOUSE_DB_URL` set | To do |

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back

_To do. Prepare: Explain raw vs landing vs silver and the last-write-wins rule._

