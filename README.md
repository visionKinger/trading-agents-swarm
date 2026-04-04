# Trading Agents Swarm

A multi-agent AI trading analysis system built as **native instruction files and MCP tools** — no LangChain, no LangGraph, no orchestration framework required. Runs natively inside **GitHub Copilot**, **Claude Code**, and **OpenAI Codex**.

> This is a clean-room reimplementation of the [TradingAgents](https://arxiv.org/abs/2412.20138) research concept, designed to run natively inside any MCP-compatible AI coding assistant.

---

## Pipeline

```
Phase 1 — Parallel Analysis
  ├── Market Analyst      (technical indicators via MCP)
  ├── Sentiment Analyst   (company news & social sentiment via MCP)
  ├── News Analyst        (global macro news via MCP)
  └── Fundamentals Analyst (financials via MCP)
        ↓
Phase 2 — Investment Debate
  Bull Researcher ←→ Bear Researcher (N rounds)
  └── Research Manager → investment_plan
        ↓
Phase 3 — Trading Decision
  Trader → FINAL TRANSACTION PROPOSAL: BUY/HOLD/SELL
        ↓
Phase 4 — Risk Debate
  Aggressive ←→ Conservative ←→ Neutral (N rounds)
  └── Portfolio Manager → Buy/Overweight/Hold/Underweight/Sell
        ↓
Phase 5 — DOCX Report
  Full analysis saved as {TICKER}_analysis_{DATE}.docx
```

---

## Setup

### 1. Install MCP dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment (optional — yfinance works without Alpha Vantage)

```bash
cp .env.example .env
# Edit .env and add your ALPHA_VANTAGE_API_KEY if you have one
```

### 3. Register MCP servers

#### GitHub Copilot (VS Code)

The `.vscode/mcp.json` file is already configured. Open this folder in VS Code with the GitHub Copilot extension — MCP servers are auto-registered.

The orchestration instructions live in `.github/copilot-instructions.md` and are automatically loaded by Copilot. Sub-agents are in `.github/agents/`.

#### Claude Code

The `.mcp.json` file at the repository root is automatically loaded by Claude Code. The orchestration instructions live in `CLAUDE.md` and sub-agents are in `.claude/agents/`.

To add the MCP servers globally instead, add them to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "trading-market-data": {
      "command": "python3",
      "args": ["/path/to/trading-agents-swarm/mcp/market-data-server.py"]
    },
    "trading-news-data": {
      "command": "python3",
      "args": ["/path/to/trading-agents-swarm/mcp/news-data-server.py"]
    }
  }
}
```

#### OpenAI Codex

The orchestration instructions live in `AGENTS.md` and are automatically loaded by Codex. Sub-agents are in `.github/agents/`.

Register the MCP servers in your Codex configuration:

```json
{
  "mcpServers": {
    "trading-market-data": {
      "command": "python3",
      "args": ["./mcp/market-data-server.py"]
    },
    "trading-news-data": {
      "command": "python3",
      "args": ["./mcp/news-data-server.py"]
    }
  }
}
```

---

## Usage

Once the MCP servers are registered, simply ask your AI assistant:

```
Analyze AAPL for today
```
```
Should I buy NVDA? Use today's date.
```
```
Run a full trading analysis on TSLA for 2024-11-15
```
```
Give me a trading recommendation for SHOP.TO
```

The assistant will automatically run the full 4-phase pipeline and generate a DOCX report.

---

## Architecture

| File / Directory | Purpose |
|---|---|
| `.github/copilot-instructions.md` | Orchestrator instructions for GitHub Copilot |
| `.github/agents/*.md` | Sub-agent prompts for GitHub Copilot |
| `CLAUDE.md` | Orchestrator instructions for Claude Code |
| `.claude/agents/*.md` | Sub-agent prompts for Claude Code |
| `AGENTS.md` | Orchestrator instructions for OpenAI Codex |
| `mcp/market-data-server.py` | MCP server for stock prices, indicators, and fundamentals |
| `mcp/news-data-server.py` | MCP server for news and insider transactions |
| `.vscode/mcp.json` | MCP server registration for VS Code / GitHub Copilot |
| `.mcp.json` | MCP server registration for Claude Code |
| `requirements.txt` | Python dependencies for MCP servers |

---

## Sub-Agents Reference

Each sub-agent has a mirrored file in `.github/agents/` (Copilot / Codex) and `.claude/agents/` (Claude Code).

| Agent | Phase | Role |
|-------|-------|------|
| `market-analyst` | Phase 1 | Technical indicators analysis |
| `sentiment-analyst` | Phase 1 | Social media & news sentiment |
| `news-analyst` | Phase 1 | Global macro news analysis |
| `fundamentals-analyst` | Phase 1 | Financial statements analysis |
| `bull-researcher` | Phase 2 | Argues the bullish case |
| `bear-researcher` | Phase 2 | Argues the bearish case |
| `research-manager` | Phase 2 | Judges debate → investment plan |
| `trader` | Phase 3 | Final BUY/HOLD/SELL decision |
| `aggressive-analyst` | Phase 4 | Champions high-risk/high-reward |
| `conservative-analyst` | Phase 4 | Champions capital preservation |
| `neutral-analyst` | Phase 4 | Balanced risk/reward perspective |
| `portfolio-manager` | Phase 4 | Final 5-tier rating decision |

---

## MCP Tools Reference

### market-data-server.py

| Tool | Description |
|------|-------------|
| `get_stock_data(symbol, start_date, end_date)` | OHLCV price data |
| `get_indicators(symbol, indicator, curr_date, look_back_days)` | Technical indicators — call once per indicator: `rsi`, `macd`, `macdh`, `macds`, `boll`, `boll_ub`, `boll_lb`, `atr`, `vwma`, `close_50_sma`, `close_200_sma`, `close_10_ema` |
| `get_fundamentals(ticker, curr_date)` | Company overview & valuation ratios |
| `get_balance_sheet(ticker, freq, curr_date)` | Balance sheet (annual or quarterly) |
| `get_cashflow(ticker, freq, curr_date)` | Cash flow statement |
| `get_income_statement(ticker, freq, curr_date)` | Income statement |

### news-data-server.py

| Tool | Description |
|------|-------------|
| `get_news(ticker, start_date, end_date)` | Company-specific news |
| `get_global_news(curr_date, look_back_days, limit)` | Global macroeconomic news |
| `get_insider_transactions(ticker)` | Insider buy/sell activity |

---

## Data Sources

- **yfinance** (default, free, no API key needed) — stock prices, indicators, fundamentals, news
- **Alpha Vantage** (optional, free tier available) — higher quality news sentiment; set `ALPHA_VANTAGE_API_KEY` in `.env`

---

## Supported Tickers

Any ticker supported by yfinance, including:
- US stocks: `AAPL`, `TSLA`, `NVDA`, `MSFT`
- Chinese A-shares: `601012.SS`, `600519.SS`
- Canadian: `SHOP.TO`, `RY.TO`
- Japanese: `9984.T`, `7203.T`
- UK: `HSBA.L`, `BP.L`
- Indices: `^SPX`, `^VIX`

Always preserve the exchange suffix in your query.

---

## Customizing the Pipeline

**Change debate rounds:** Edit the orchestrator instructions file for your tool — find `debate_rounds` (default: 2) and `risk_rounds` (default: 2).

**Swap data vendor:** Set `ALPHA_VANTAGE_API_KEY` in `.env` — the MCP servers automatically prefer Alpha Vantage when the key is present, falling back to yfinance.

**Add a new analyst:** Create new sub-agent files in `.github/agents/` and `.claude/agents/`, then wire the new agent into the pipeline in all three orchestrator files.

---

## Credits

Inspired by the [TradingAgents](https://arxiv.org/abs/2412.20138) research paper (arXiv:2412.20138). This is a ground-up reimplementation as a native AI assistant plugin — no LangChain dependency.
