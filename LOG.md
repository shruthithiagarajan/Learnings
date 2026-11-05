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
