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
| Read Docker docs, Get started parts 1 to 3 | To do |
| Start Postgres with `./cookbook/scripts/run_pgvector.sh`; read the script and explain every flag | To do |
| Find the container (`docker ps`), its logs (`docker logs pgvector`) and its port (`lsof -i :5532`) | To do |
| Connect with `psql -h localhost -p 5532 -U ai` (password ai); create a database and a table; insert two rows | To do |
| Stop and start the container: is the table still there, and why? Remove the container and start again: why is it different? | To do |
| Open `deploy/compose.yaml`; list the services, their images and their ports | To do |

**Demo:** Show the running container, connect with psql, show your table, explain what happens to data on stop vs remove.

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
   - _To do_
2. Why did your data survive a stop but not a remove (or did it)? What is a volume?
   - _To do_
3. Two services in compose.yaml want the same port. What happens?
   - _To do_

**Done when:** You can start, inspect, connect to and stop Postgres without looking anything up.

---

## Day 3: PostgreSQL basics (date)

### Checklist

| Task | Status |
|---|---|
| Read Postgres docs, Tutorial chapters 2 and 3 | To do |
| Create `deals(deal_id, stage, amount, created_at, brand)` and `dealers(dealer_id, name, region)`, plus a `dealer_id` on deals | To do |
| Insert 15 to 20 rows by hand, with some NULL amounts and one deal with no dealer | To do |
| Queries: deals per stage; total amount per brand; deals with no dealer (left join); average amount ignoring NULLs; top 3 brands by amount | To do |
| Run one query inside a transaction, then ROLLBACK, and show nothing changed | To do |

**Demo:** Run each query and explain its result.

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
   - _To do_
2. How does AVG treat NULL? How would you count NULLs as zero instead?
   - _To do_
3. What would an index on `created_at` help with?
   - _To do_

**Done when:** Every query is written by you and explained.

---

## Day 4: JSON in Postgres, and latest row per key (date)

### Checklist

| Task | Status |
|---|---|
| Read Postgres docs, Window Functions tutorial (3.5) | To do |
| Write `deals.ndjson` by hand with made-up data: the same deal several times with different `last_modified`, and one quote as three rows (one per product line) | To do |
| Load it into `raw_deals(payload jsonb)` with `\copy` or a small Python script you write | To do |
| Query: how many rows? how many distinct deals? latest stage per deal (window function)? value of each deal at its latest version (sum of price x qty over its lines)? how many deals are Closed Won? | To do |
| Answer it wrongly on purpose (count Closed Won rows) and write down why the numbers differ | To do |

**Demo:** Show the file, the raw table, and the right and wrong answers side by side.

### What I learned

_To do, in my own words._

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
   - _To do_
3. If two versions of a deal have exactly the same `last_modified`, which one does your query pick? Is that safe?
   - _To do_

**Done when:** You can write the latest-per-key query from memory and explain why it is needed.

---

## Day 5: HTTP and APIs (date)

### Checklist

| Task | Status |
|---|---|
| Read GitHub REST docs: Using pagination, Rate limits | To do |
| With curl, list issues of a public repo (for example `psf/requests`, `state=all&per_page=5`); with `curl -i` find the rate-limit headers and the Link header | To do |
| Add `since=2026-09-01T00:00:00Z`: what changed? | To do |
| Write a Python function (httpx or requests) that fetches all pages for a `since` date, follows the Link header, and retries with a growing wait on 429 or 5xx | To do |
| Write tests for the paging logic by hand, using a fake response | To do |

**Demo:** Run the function for one week of issues; show how many pages it fetched and the rate-limit headers.

### What I learned

_To do, in my own words._

### 3 surprises

1. _To do_
2. _To do_
3. _To do_

### 1 open question

_To do_

### Explain back (answer in my own words)

1. What does a 429 mean and what should a client do? What about 401?
   - _To do_
2. How does your code know there is another page?
   - _To do_
3. Why is `since` useful when you pull the same source every day?
   - _To do_

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
| Write a `run_sql(query)` tool over your Day 4 data: one SELECT only, refuses anything else, caps rows; connect as a read-only database user you create | To do |
| Give it to an agent whose instructions describe `raw_deals`; ask: how many deals are Closed Won? what is the total value of open deals? | To do |
| Compare with your Day 4 answers; if it counts rows instead of deals, change the instructions or tool description and record what worked | To do |
| Tests by hand for the guard: a DELETE, two statements in one string, an allowed SELECT | To do |

**Demo:** Show the tool calls in the trace, the right answer, and the guard refusing a write.

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
   - _To do_
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

