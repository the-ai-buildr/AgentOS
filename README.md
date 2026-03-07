# AgentOS Docker Template

Deploy a multi-agent system to production with Docker.

[What is AgentOS?](https://docs.agno.com/agent-os/introduction) · [Agno Docs](https://docs.agno.com) · [Discord](https://agno.com/discord)

---

## What's Included

| Agent | Pattern | Description |
|-------|---------|-------------|
| **Agno Assist** | Learning + Tools | Your AI-powered second brain |
| Knowledge Agent | RAG | Answers questions from a knowledge base |
| Neo Orchestrator Team | Team of Teams | Routes work across communication, planning, tools, dev, research, and content roles |

**Agno Assist** (Personal Agent that Learns) is your AI-powered second brain. It researches, captures, organizes, connects, and retrieves your personal knowledge - so nothing useful is ever lost.

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone and configure
```sh
git clone https://github.com/agno-agi/agentos-docker-template.git agentos-docker
cd agentos-docker
cp example.env .env
# Add your OPENAI_API_KEY to .env
```

### 2. Start locally
```sh
docker compose up -d --build
```

- **API**: http://localhost:8080
- **Docs**: http://localhost:8080/docs
- **Database**: internal-only (container network)

### 3. Connect to control plane

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" → "Local"
3. Enter `http://localhost:8080`

---

## Run locally with Docker

Run the full stack (API + Postgres) on your machine with Docker.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running

### 1. Configure environment

From the repo root, create a `.env` file with at least:

```bash
# Required for agents
OPENAI_API_KEY=sk-...   # or OPENROUTER_API_KEY for OpenRouter models

# Database (defaults shown; optional if you use these values)
DB_USER=ai
DB_PASS=ai
DB_DATABASE=ai

# Optional: disable remote MCP if the default server is unreachable from the container
# MCP_DISABLED=1
```

### 2. Start the stack

```bash
docker compose up -d --build
```

This builds the API image and starts:

- **agentos-api** – AgentOS API (FastAPI)
- **agentos-db** – PostgreSQL with pgvector

### 3. Use the API

| What        | URL                        |
|-------------|----------------------------|
| API         | http://localhost:8080      |
| OpenAPI docs| http://localhost:8080/docs |
| Health      | http://localhost:8080/health |

PostgreSQL is internal-only in Docker Compose (not published to host).

### 4. Useful commands

```bash
# View API logs (follow)
docker compose logs -f agentos-api

# View DB logs
docker compose logs -f agentos-db

# Stop everything
docker compose down

# Stop and remove volumes (resets DB and stored data)
docker compose down -v
```

### 5. Optional: connect to Agno OS (control plane)

1. Open [os.agno.com](https://os.agno.com)
2. Click **Add OS** → **Local**
3. Enter a **public URL** (the control plane cannot reach `localhost`). For local runs: use a tunnel (e.g. `ngrok http 8000`), then paste the HTTPS URL. For deployed runs: use your server URL.

---

## The Agents

### Agno Assist (Personal Agent that Learns)

Your AI-powered second brain. Agno Assist researches, captures, organizes, connects, and retrieves your personal knowledge - so nothing useful is ever lost.

**What Agno Assist stores:**

| Type | Examples |
|------|----------|
| **Notes** | Ideas, decisions, snippets, learnings |
| **Bookmarks** | URLs with context - why you saved it |
| **People** | Contacts - who they are, how you know them |
| **Meetings** | Notes, decisions, action items |
| **Projects** | Goals, status, related items |
| **Research** | Findings from web search, saved for later |

**Try it:**
```
Note: decided to use Postgres for the new project - better JSON support
Bookmark https://www.ashpreetbedi.com/articles/lm-technical-design - great intro
Research event sourcing patterns and save the key findings
What notes do I have?
What do I know about event sourcing?
```

**How it works:**
- **DuckDB** stores your actual data (notes, bookmarks, people, etc.)
- **Learning system** remembers schemas and research findings
- **DuckDuckGo search** powers web research and discovery

**Data persistence:** Agno Assist stores structured data in DuckDB at `/data/agno_assist.db`. This persists across container restarts.

### Knowledge Agent

Answers questions using a vector knowledge base (RAG pattern).

**Try it:**
```
What is Agno?
How do I create my first agent?
What documents are in your knowledge base?
```

**Load documents:**
```sh
docker exec -it agentos-api python -m src.agents.knowledge_agent
```

### Tools + MCP (via Neo Team)

Tool execution is now handled by Neo team members (`tools_agent`, `plane_agent`, and `pulse_agent`) instead of a standalone MCP agent.

Configure one or more MCP servers with `MCP_SERVER_URLS` (comma or newline-separated URLs).
The MCP setup is intentionally simple and env-driven in `src/tools/mcp_tools.py`.

#### Plane MCP with this minimal setup

For self-hosted Plane, this project supports Plane MCP via stdio (`uvx plane-mcp-server stdio`) when Plane env vars are set:

```env
MCP_DISABLED=0
MCP_SERVER_URLS=none
PLANE_BASE_URL=https://plane.theaibuildr.com
PLANE_API_KEY=<plane-api-key>
PLANE_WORKSPACE_SLUG=<workspace-slug>
```

You can also keep other MCP URLs in `MCP_SERVER_URLS` (comma/newline list) if needed.

---

## Project Structure
```
├── src/
│   ├── agents/             # Standalone agents (assist, knowledge, slack)
│   ├── teams/              # Neo orchestrator + sub-teams
│   ├── tools/              # MCP tool loading/config
│   ├── runtime/            # AgentOS bootstrap/composition root
│   ├── config/             # Runtime settings
│   └── schedules/          # Scheduler registrations
├── app/
│   ├── main.py             # AgentOS entry point
│   └── config.yaml         # Quick prompts config
├── db/
│   ├── session.py          # Database session
│   └── url.py              # Connection URL builder
├── scripts/                # Helper scripts
├── compose.yaml            # Docker Compose config
├── Dockerfile
└── pyproject.toml          # Dependencies
```

---

## Common Tasks

### Add your own agent

1. Create `src/agents/my_agent.py`:
```python
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from db.session import get_postgres_db

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    db=get_postgres_db(),
    instructions="You are a helpful assistant.",
)
```

2. Register in `src/runtime/bootstrap.py`:
```python
from src.agents.my_agent import my_agent

agent_os = AgentOS(
    name="AgentOS",
    agents=[agno_assist, knowledge_agent, my_agent],
    ...
)
```

3. Restart: `docker compose restart`

### Add tools to an agent

Agno includes 100+ tool integrations. See the [full list](https://docs.agno.com/tools/toolkits).
```python
from agno.tools.slack import SlackTools
from agno.tools.google_calendar import GoogleCalendarTools

my_agent = Agent(
    ...
    tools=[
        SlackTools(),
        GoogleCalendarTools(),
    ],
)
```

### Add dependencies

1. Edit `pyproject.toml`
2. Regenerate requirements: `./scripts/generate_requirements.sh`
3. Rebuild: `docker compose up -d --build`

### Use a different model provider

1. Add your API key to `.env` (e.g., `ANTHROPIC_API_KEY`)
2. Update agents to use the new provider:
```python
from agno.models.anthropic import Claude

model=Claude(id="claude-sonnet-4-5")
```
3. Add dependency: `anthropic` in `pyproject.toml`

---

## Local Development

For development without Docker:
```sh
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
./scripts/venv_setup.sh
source .venv/bin/activate

# Start PostgreSQL (required)
docker compose up -d agentos-db

# Run the app
python -m app.main
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |
| `DATA_DIR` | No | `/data` | Directory for DuckDB storage |
| `RUNTIME_ENV` | No | `prd` | Set to `dev` for auto-reload |
| `MCP_SERVER_URLS` | No | `https://docs.agno.com/mcp` | MCP endpoints for Neo tool-execution agents (comma or newline separated). Set to `none` or use `MCP_DISABLED=1` to disable remote MCP (e.g. when running in Docker and the default URL is unreachable). |
| `MCP_DISABLED` | No | - | Set to `1`, `true`, or `yes` to disable MCP tools for Neo tool-execution agents (avoids "Failed to initialize MCP toolkit" when the remote server is unreachable). |
| `AGNO_ASSIST_MCP_SERVER_URLS` | No | - | Optional MCP endpoints for Agno Assist (comma or newline separated) |
| `PLANE_BASE_URL` | No | - | Base URL of your Plane instance (e.g. `https://plane.theaibuildr.com`) for Plane stdio MCP |
| `PLANE_API_KEY` | No | - | Plane API key used by Plane stdio MCP |
| `PLANE_WORKSPACE_SLUG` | No | - | Plane workspace slug used by Plane stdio MCP |
| `IMAGE_NAME` | No | `agentos-api` | Image name for the API service (set in Coolify to the image you build) |
| `IMAGE_TAG` | No | `latest` | Image tag (set in Coolify if you use a specific tag) |
| `HOST_PORT` | No | `8080` | Host port for the API (maps to container port `8000`; set in Coolify to another port, e.g. `18080`, if needed) |

---

## Troubleshooting

- **API seems to hang on startup** – The API waits for Postgres, then runs DB init at import. Compose now starts the API only after the DB is *healthy*. If it still hangs: check `docker compose logs -f agentos-api`; ensure `.env` DB credentials match and run `make clean && make up`; or set `WAIT_FOR_DB_TIMEOUT=30`.
- **API container restart loop / "password authentication failed for user \"ai\""** – The API can’t log in to Postgres. Usually the `pgdata` volume was created with different `DB_USER`/`DB_PASS`/`DB_DATABASE` (or no `.env`). Fix: ensure `.env` has `DB_USER`, `DB_PASS`, and `DB_DATABASE`, then reset the DB so Postgres re-inits with those values:
  ```bash
  docker compose down -v
  docker compose up -d --build
  ```
  Or: `make clean && make up`.

- **"Failed to initialize MCP toolkit"** – The Agno MCP client cannot reach configured MCP server(s). In Docker or restricted networks, set `MCP_DISABLED=1` (or `MCP_SERVER_URLS=none`) so Neo tool-execution agents run without remote MCP.
- **WebSocket error: (, '')** – Usually harmless: the client (e.g. OS UI) closed the workflow WebSocket (e.g. switching tabs or agents). No action needed unless workflows consistently fail to run.

---

## Deploying with Coolify

Coolify builds the image in a helper container and tags it with its own name. To avoid "pull access denied for agno-agentos", set these in your Coolify deployment environment so Compose uses the image that was just built instead of pulling from a registry:

- **IMAGE_NAME** – Set to the full image name Coolify uses for this service (e.g. your Coolify registry URL and path, or the generated image name in the build step).
- **IMAGE_TAG** – Optional; set if Coolify uses a tag other than `latest`.
- **HOST_PORT** – If deploy fails with "Bind for 0.0.0.0:8000 failed: port is already allocated", set **HOST_PORT** to a free port (e.g. `18080`) in Coolify's environment variables so the API binds to that port instead.

After setting these, redeploy so `docker compose up -d` uses the built image.

### Plane MCP on Coolify (self-hosted)

Set these env vars:

- `MCP_DISABLED=0`
- `MCP_SERVER_URLS=none` (or keep other non-Plane MCP URLs here)
- `PLANE_BASE_URL=https://plane.theaibuildr.com`
- `PLANE_API_KEY=<your-plane-api-key>`
- `PLANE_WORKSPACE_SLUG=Agent-ws`

The app will auto-add Plane MCP through stdio when these are present.

---

## Extending Agno Assist

Agno Assist is designed to be extended. Connect it to your existing tools:

### Communication
```python
from agno.tools.slack import SlackTools
from agno.tools.gmail import GmailTools

tools=[
    ...
    SlackTools(),    # Capture decisions from Slack
    GmailTools(),    # Track important emails
]
```

### Productivity
```python
from agno.tools.google_calendar import GoogleCalendarTools
from agno.tools.linear import LinearTools

tools=[
    ...
    GoogleCalendarTools(),  # Meeting context
    LinearTools(),          # Project tracking
]
```

### Research
```python
from agno.tools.yfinance import YFinanceTools
from agno.tools.github import GithubTools

tools=[
    ...
    YFinanceTools(),  # Financial data
    GithubTools(),    # Code and repos
]
```

See the [Agno Tools documentation](https://docs.agno.com/tools/toolkits) for the full list of available integrations.

---

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Tools & Integrations](https://docs.agno.com/tools/toolkits)
- [Discord Community](https://agno.com/discord)
