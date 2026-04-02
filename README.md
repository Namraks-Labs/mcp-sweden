# mcp-sweden 🇸🇪

MCP server for Swedish open data APIs. Connects AI assistants to Swedish government, statistics, media, finance, and public service data through the [Model Context Protocol](https://modelcontextprotocol.io/).

Inspired by [mcp-brasil](https://github.com/jxnxts/mcp-brasil) — uses the same convention-based auto-discovery architecture.

## Data Sources

| Priority | Feature | Description | API | Issue |
|---|---|---|---|---|
| High | `riksdag` | Parliament members, votes, documents, debates | [data.riksdagen.se](https://data.riksdagen.se) | A-31 |
| High | `scb` | Population, economy, labor, trade statistics | [api.scb.se](https://api.scb.se) | A-34 |
| Medium | `kolada` | Municipality & region KPIs and comparisons | [api.kolada.se](https://api.kolada.se) | A-32 |
| Medium | `skolverket` | School statistics, grades, curricula | [skolverket.se](https://www.skolverket.se) | A-33 |
| Medium | `sverigesradio` | Channels, programs, episodes, news, traffic | [api.sr.se](https://sverigesradio.se/oppetapi) | A-35 |
| Medium | `avanza` | Stock quotes, funds, market data, charts | [avanza.se](https://www.avanza.se) | A-36 |
| Medium | `bolagsverket` | Company search, registration, annual reports | [bolagsverket.se](https://bolagsverket.se) | A-39 |
| Medium | `sl` | Stockholm public transport — stations, departures, lines | [transport.integration.sl.se](https://transport.integration.sl.se/v1) | A-43 |
| Low | `begagnad` | Second-hand marketplace listings, prices | — | A-37 |
| Low | `solar` | Solar energy production, irradiance data | — | A-38 |

## Installation

### Option 1: `uvx` (recommended — no install needed)

If you have [uv](https://docs.astral.sh/uv/) installed:

```bash
uvx mcp-sweden
```

That's it. No virtual environment, no pip, no Python version management.

### Option 2: `pip`

```bash
pip install mcp-sweden
```

### Option 3: Smithery marketplace

```bash
npx -y @smithery/cli install mcp-sweden --client claude
```

### Option 4: From source

```bash
git clone https://github.com/Namraks-Labs/mcp-sweden.git
cd mcp-sweden
pip install -e .
```

## Setup

### Claude Code

```bash
claude mcp add mcp-sweden -- uvx mcp-sweden
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "mcp-sweden": {
      "command": "uvx",
      "args": ["mcp-sweden"]
    }
  }
}
```

### Remote server (HTTP transport)

For shared access or hosted deployment:

```bash
uvx mcp-sweden --transport http --port 8000
```

Or with Docker:

```bash
docker build -t mcp-sweden .
docker run -p 8000:8000 mcp-sweden
```

## Hosting your own instance

For users on claude.ai or teams that want a shared server, deploy with any container host:

### Railway

1. Fork this repo
2. Connect it to [Railway](https://railway.app)
3. Railway auto-detects the `Dockerfile` and deploys
4. Set port to `8000` in the service settings
5. Use the generated URL as your MCP endpoint

Railway's Hobby plan ($5/month with $5 usage credits) works well for low-traffic servers.

### Render

1. Fork this repo
2. Create a new **Web Service** on [Render](https://render.com)
3. Point it to your fork — Render detects the `Dockerfile`
4. Set the port to `8000`

Render has a free tier for web services (with cold starts after inactivity).

### Fly.io

```bash
fly launch --dockerfile Dockerfile
fly deploy
```

### Any Docker host

```bash
docker build -t mcp-sweden .
docker run -p 8000:8000 -e MCP_SWEDEN_API_TOKEN=your-secret mcp-sweden
```

Set `MCP_SWEDEN_API_TOKEN` to require a Bearer token for authentication.

## Architecture

```
src/mcp_sweden/
├── __init__.py          # Package version
├── __main__.py          # Entry point for `python -m mcp_sweden` and `uvx`
├── server.py            # Root server — auto-discovers and mounts features
├── settings.py          # Configuration via environment variables
├── exceptions.py        # Shared exception hierarchy
├── _shared/             # Shared utilities
│   ├── feature.py       # FeatureMeta + FeatureRegistry (auto-discovery)
│   ├── http_client.py   # Async HTTP with retry + backoff
│   ├── cache.py         # TTL cache for API responses
│   └── rate_limiter.py  # Token-bucket rate limiter
└── data/                # Feature subpackages (auto-discovered)
    ├── riksdag/         # Each feature has:
    │   ├── __init__.py  #   FEATURE_META declaration
    │   ├── server.py    #   FastMCP server with tool registration
    │   ├── client.py    #   HTTP client for the API
    │   ├── tools.py     #   Tool implementations
    │   └── schemas.py   #   Pydantic response models
    ├── scb/
    ├── kolada/
    ├── skolverket/
    ├── sverigesradio/
    ├── avanza/
    ├── bolagsverket/
    ├── sl/
    ├── begagnad/
    └── solar/
```

### How auto-discovery works

1. `FeatureRegistry.discover("mcp_sweden.data")` scans all subpackages
2. Each subpackage must export `FEATURE_META` (a `FeatureMeta` instance) in `__init__.py`
3. Each subpackage must have a `server.py` that exports an `mcp` FastMCP object
4. Features are automatically mounted with namespace prefixes (e.g., `riksdag_search_documents`)
5. Zero config needed to add a new feature — just create the directory and follow the convention

### Adding a new feature

1. Create `src/mcp_sweden/data/<name>/`
2. Add `__init__.py` with `FEATURE_META`
3. Add `server.py` with `mcp = FastMCP("mcp-sweden-<name>")`
4. Implement tools in `tools.py`, HTTP calls in `client.py`
5. Register tools in `server.py`
6. Done — the registry auto-discovers it on next start

## Configuration

| Variable | Default | Description |
|---|---|---|
| `MCP_SWEDEN_HTTP_TIMEOUT` | `30.0` | HTTP request timeout (seconds) |
| `MCP_SWEDEN_HTTP_MAX_RETRIES` | `3` | Max retries on transient errors |
| `MCP_SWEDEN_HTTP_BACKOFF_BASE` | `1.0` | Exponential backoff base (seconds) |
| `MCP_SWEDEN_USER_AGENT` | `mcp-sweden/0.1.0` | HTTP User-Agent header |
| `MCP_SWEDEN_TOOL_SEARCH` | `bm25` | Tool discovery mode: `bm25` or `none` |
| `MCP_SWEDEN_API_TOKEN` | — | Bearer token for HTTP transport auth |
| `ANTHROPIC_API_KEY` | — | For LLM-powered tool recommendations |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
ruff format src/

# Type check
mypy src/
```

## License

MIT
