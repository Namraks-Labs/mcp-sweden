# mcp-sweden

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A production-ready [Model Context Protocol](https://modelcontextprotocol.io/) server for Swedish open data. Connect any MCP-compatible AI assistant to 10 Swedish government, statistics, media, finance, and public service APIs through **57 tools** — no API keys required.

**[sweden.mcp.namraks.com](https://sweden.mcp.namraks.com)** | Built by [Namraks Labs](https://github.com/Namraks-Labs)

## Features

| Data Source | Description | Tools | API |
|---|---|---|---|
| **riksdag** | Parliament members, votes, documents, debates | 5 | [data.riksdagen.se](https://data.riksdagen.se) |
| **scb** | Population, economy, labor, trade, environment statistics | 5 | [api.scb.se](https://api.scb.se) |
| **kolada** | Municipality & region KPIs, comparisons, rankings | 6 | [api.kolada.se](https://api.kolada.se) |
| **skolverket** | School registry, statistics, grades, teacher data | 7 | [api.skolverket.se](https://api.skolverket.se) |
| **sverigesradio** | Channels, programs, episodes, playlists, news, traffic | 9 | [api.sr.se](https://sverigesradio.se/oppetapi) |
| **avanza** | Stock quotes, funds, market data, orderbook, charts | 6 | [avanza.se](https://www.avanza.se) |
| **bolagsverket** | Company search, registration data, annual reports | 4 | [bolagsverket.se](https://bolagsverket.se) |
| **sl** | Stockholm public transport — stations, real-time departures, lines | 5 | [transport.integration.sl.se](https://transport.integration.sl.se/v1) |
| **begagnad** | Search Swedish second-hand marketplaces (Blocket, Tradera) | 5 | Web scraping |
| **solar** | Solar energy production, irradiance, installations | 5 | [SMHI Open Data](https://opendata-download-metfcst.smhi.se) |

All data sources are free and require no authentication.

## Quick Start

### Use the hosted instance (recommended)

A public instance is running at **[sweden.mcp.namraks.com](https://sweden.mcp.namraks.com)**. No setup required:

**Claude Code:**

```bash
claude mcp add mcp-sweden --transport http https://sweden.mcp.namraks.com/mcp
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mcp-sweden": {
      "url": "https://sweden.mcp.namraks.com/mcp"
    }
  }
}
```

### Run locally

```bash
# Clone and install
git clone https://github.com/Namraks-Labs/mcp-sweden.git
cd mcp-sweden
pip install -e .

# Start via stdio (for Claude Desktop / Claude Code)
fastmcp run mcp_sweden.server:mcp

# Or start via HTTP
fastmcp run mcp_sweden.server:mcp --transport http --port 8000
```

**Claude Desktop config (local stdio):**

```json
{
  "mcpServers": {
    "mcp-sweden": {
      "command": "fastmcp",
      "args": ["run", "mcp_sweden.server:mcp"]
    }
  }
}
```

### Docker

```bash
docker build -t mcp-sweden .
docker run -p 8000:8000 mcp-sweden
```

## Architecture

The server uses a convention-based auto-discovery architecture inspired by [mcp-brasil](https://github.com/jxnxts/mcp-brasil). Each data source is a self-contained subpackage that is automatically detected and mounted at startup.

```
src/mcp_sweden/
├── server.py            # Root server — auto-discovers and mounts features
├── settings.py          # Configuration via environment variables
├── _shared/             # Shared utilities (HTTP client, cache, rate limiter)
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

Adding a new data source is as simple as creating a new subpackage following the convention — the registry discovers it automatically on startup.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `MCP_SWEDEN_HTTP_TIMEOUT` | `30.0` | HTTP request timeout (seconds) |
| `MCP_SWEDEN_HTTP_MAX_RETRIES` | `3` | Max retries on transient errors |
| `MCP_SWEDEN_HTTP_BACKOFF_BASE` | `1.0` | Exponential backoff base (seconds) |
| `MCP_SWEDEN_USER_AGENT` | `mcp-sweden/0.1.0` | HTTP User-Agent header |
| `MCP_SWEDEN_TOOL_SEARCH` | `bm25` | Tool discovery mode: `bm25` or `none` |
| `MCP_SWEDEN_API_TOKEN` | — | Bearer token for HTTP transport auth |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint & format
ruff check src/
ruff format src/

# Type check
mypy src/
```

## Contributing

Contributions are welcome! To add a new Swedish data source:

1. Create a subpackage under `src/mcp_sweden/data/<name>/`
2. Define `FEATURE_META` in `__init__.py`
3. Implement tools in `tools.py` and register them in `server.py`
4. Add Pydantic schemas in `schemas.py` and HTTP calls in `client.py`
5. Submit a pull request

See the existing data sources for reference.

## License

[MIT](LICENSE) — Copyright (c) 2026 Namraks Labs
