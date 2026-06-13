# Kickbacks.ai MCP Server

[![PyPI](https://img.shields.io/pypi/v/kickbacks-mcp.svg)](https://pypi.org/project/kickbacks-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/kickbacks-mcp.svg)](https://pypi.org/project/kickbacks-mcp/)
[![License](https://img.shields.io/pypi/l/kickbacks-mcp.svg)](https://github.com/msgok/kickbacks-mcp/blob/main/LICENSE)

> **Earn ad revenue from AI coding agent spinners** — MCP server for [Kickbacks.ai](https://kickbacks.ai) that exposes tools to check balance, earnings, status, ad history, and enable/disable ads.

## What is Kickbacks.ai?

Kickbacks.ai pays developers **50% of ad revenue** from ads shown in AI coding agent spinners (Claude Code, Codex). While your agent "thinks", its spinner shows sponsored lines instead of generic verbs like "Discombobulating...".

| Platform | Status |
|----------|--------|
| VS Code Extension (Claude Code) | ✅ Primary |
| VS Code Extension (Codex) | ⚠️ Temp disabled |
| Terminal CLI (Claude Code 2.1.143+) | ✅ Works |

## Quick Start

### 1. Get API Credentials
Email **support@kickbacks.ai** for partner API access.

### 2. Install & Configure
```bash
# Install via uvx (recommended)
uvx kickbacks-mcp

# Or install locally
pip install kickbacks-mcp
# or
pip install -e .
```

### 3. Set Environment Variables
```bash
export KICKBACKS_API_KEY=your_api_key_here
export KICKBACKS_USER_ID=your_user_id_here  # optional
```

### 4. Add to Hermes Agent Config
```yaml
# ~/.hermes/config.yaml
mcp_servers:
  kickbacks:
    command: "uvx"
    args: ["kickbacks-mcp"]
    env:
      KICKBACKS_API_KEY: "your_key"
```

### 5. Use in Any MCP-Compatible Agent
```bash
# Check balance
> kickbacks_balance

# See earnings breakdown
> kickbacks_earnings

# Check status & caps
> kickbacks_status

# View ad history
> kickbacks_ads_history

# Enable/disable ads
> kickbacks_set_enabled enabled=true
```

## Available Tools

| Tool | Description |
|------|-------------|
| `kickbacks_balance` | Current balance (total earnings) |
| `kickbacks_earnings` | Breakdown: today/week/month/total |
| `kickbacks_status` | Connection state, caps, session stats |
| `kickbacks_ads_history` | Impression/click log with pagination |
| `kickbacks_set_enabled` | Enable/disable ads |
| `kickbacks_config` | Check configuration status |

## Example Outputs

```
> kickbacks_earnings
Earnings Breakdown:
  Today: $0.42
  This Week: $7.11
  This Month: $42.50
  Total: $156.78
  Currency: USD

> kickbacks_status
Connected: ✅ | Authenticated: ✅ | Enabled: ✅ | Last sync: 2026-06-13T21:32:31 | Session: 23 impressions, 2 clicks

> kickbacks_ads_history
Ad History (showing 2 of 2):
  👁 [2026-06-13T21:32:31] Ramp - save time and money (spinner) - $0.0010
  👆 [2026-06-13T21:32:31] Bitcoin Devs Takeover Toronto (statusbar) - $0.0500
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `KICKBACKS_API_KEY` | Yes | API key from Kickbacks.ai |
| `KICKBACKS_USER_ID` | No | Your Kickbacks user ID |
| `KICKBACKS_API_BASE` | No | Custom API base URL (default: `https://api.kickbacks.ai/v1`) |

### Hermes Agent Config
```yaml
mcp_servers:
  kickbacks:
    command: "uvx"
    args: ["kickbacks-mcp"]
    env:
      KICKBACKS_API_KEY: "ghp_xxx..."
      KICKBACKS_USER_ID: "user_123"
    timeout: 60
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "kickbacks": {
      "command": "uvx",
      "args": ["kickbacks-mcp"],
      "env": {
        "KICKBACKS_API_KEY": "your_key"
      }
    }
  }
}
```

## Development

### Local Development
```bash
# Clone
git clone https://github.com/msgok/kickbacks-mcp
cd kickbacks-mcp

# Install in dev mode
pip install -e ".[dev]"

# Run directly
python -m kickbacks_mcp.server

# Run tests
pytest
```

### Project Structure
```
kickbacks_mcp/
├── __init__.py      # Package init
├── client.py        # Kickbacks API client
├── server.py        # MCP server with tools
├── pyproject.toml   # Project config
└── README.md        # This file
```

### Adding Real API Support
When Kickbacks provides API access:
1. Edit `client.py` → replace `_mock_response()` with real HTTP calls
2. Update data models if API differs
3. Test with `pytest tests/`

## Publishing to PyPI

```bash
# Build
pip install build
python -m build

# Publish
pip install twine
twine upload dist/*
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Kickbacks API Access**: support@kickbacks.ai
- **Issues**: [GitHub Issues](https://github.com/msgok/kickbacks-mcp/issues)
- **Kickbacks Website**: https://kickbacks.ai

---

*Built for the Hermes Agent ecosystem. Works with any MCP-compatible agent.*