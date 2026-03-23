# Trading Agents — Copilot Plugin

A multi-agent AI trading analysis system reimplemented as **GitHub Copilot instruction files, skills, and MCP tools** — no LangChain, no LangGraph, no orchestration framework required.

> This is a clean-room reimplementation of the [TradingAgents](https://arxiv.org/abs/2412.20138) research concept, designed to run natively inside GitHub Copilot, Claude Code, or any MCP-compatible AI coding assistant.

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

**VS Code / GitHub Copilot:**
The `.vscode/mcp.json` file is already configured. Open this folder in VS Code with the Copilot extension — MCP servers are auto-registered.

**Claude Code:**
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "trading-market-data": {
      "command": "python3",
      "args": ["/path/to/trading-agents-copilot/mcp/market-data-server.py"]
    },
    "trading-news-data": {
      "command": "python3",
      "args": ["/path/to/trading-agents-copilot/mcp/news-data-server.py"]
    }
  }
}
```

**Codex / OpenAI:**
Register each MCP server via the OpenAI plugin manifest or your tool configuration.

---

## Usage

Once MCP servers are running and Copilot has the instruction file loaded, simply ask:

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

Copilot will automatically run the full 4-phase pipeline using the skills and MCP tools.

---

## Sub-Agents Reference

| File | Phase | Role |
|------|-------|------|
| `.claude/agents/market-analyst.md` | Phase 1 | Technical indicators analysis |
| `.claude/agents/sentiment-analyst.md` | Phase 1 | Social media & news sentiment |
| `.claude/agents/news-analyst.md` | Phase 1 | Global macro news analysis |
| `.claude/agents/fundamentals-analyst.md` | Phase 1 | Financial statements analysis |
| `.claude/agents/bull-researcher.md` | Phase 2 | Argues the bullish case |
| `.claude/agents/bear-researcher.md` | Phase 2 | Argues the bearish case |
| `.claude/agents/research-manager.md` | Phase 2 | Judges debate → investment plan |
| `.claude/agents/trader.md` | Phase 3 | Final BUY/HOLD/SELL decision |
| `.claude/agents/aggressive-analyst.md` | Phase 4 | Champions high-risk/high-reward |
| `.claude/agents/conservative-analyst.md` | Phase 4 | Champions capital preservation |
| `.claude/agents/neutral-analyst.md` | Phase 4 | Balanced risk/reward perspective |
| `.claude/agents/portfolio-manager.md` | Phase 4 | Final 5-tier rating decision |

---

## MCP Tools Reference

### market-data-server.py

| Tool | Description |
|------|-------------|
| `get_stock_data(symbol, start_date, end_date)` | OHLCV price data |
| `get_indicators(symbol, indicator, curr_date, look_back_days)` | Technical indicators (rsi, macd, macdh, macds, boll, boll_ub, boll_lb, atr, vwma, close_50_sma, close_200_sma, close_10_ema) |
| `get_fundamentals(ticker, curr_date)` | Company overview & valuation ratios |
| `get_balance_sheet(ticker, freq, curr_date)` | Balance sheet |
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
- **Alpha Vantage** (optional, free tier available) — higher quality news sentiment, 50+ indicators

---

## Supported Tickers

Any ticker supported by yfinance, including:
- US stocks: `AAPL`, `TSLA`, `NVDA`
- Canadian: `SHOP.TO`, `RY.TO`
- Japanese: `9984.T`, `7203.T`
- UK: `HSBA.L`, `BP.L`
- Indices: `^SPX`, `^VIX`

Always preserve the exchange suffix in your query.

---

## Customizing the Pipeline

**Change debate rounds:** Edit `.github/copilot-instructions.md` — find `debate_rounds` (default: 2) and `risk_rounds` (default: 2).

**Swap data vendor:** Set `ALPHA_VANTAGE_API_KEY` in your `.env` — the MCP servers automatically prefer Alpha Vantage when the key is present, falling back to yfinance.

**Add a new analyst:** Create a new sub-agent file in `.claude/agents/` and add it to the pipeline in `.github/copilot-instructions.md`.

---

## Credits

Inspired by the [TradingAgents](https://arxiv.org/abs/2412.20138) research paper (arXiv:2412.20138). This is a ground-up reimplementation as a Copilot-native plugin — no LangChain dependency.
