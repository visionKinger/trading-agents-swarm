"""
MCP Server: News & Insider Data
Wraps yfinance news and optionally Alpha Vantage for company news,
global macroeconomic news, and insider transactions.
Register this server in your MCP config to give Copilot access to news tools.
"""

import json
import os
from datetime import datetime, timedelta

try:
    import yfinance as yf
except ImportError:
    raise RuntimeError("Install dependencies: pip install yfinance")

AV_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")

# ---------------------------------------------------------------------------
# MCP Tool Definitions
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "get_news",
        "description": "Retrieve recent news articles for a specific ticker symbol over a date range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol, e.g. AAPL"},
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
            },
            "required": ["ticker", "start_date", "end_date"],
        },
    },
    {
        "name": "get_global_news",
        "description": "Retrieve broad macroeconomic and global news relevant to financial markets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "curr_date": {"type": "string", "description": "Current date in YYYY-MM-DD format"},
                "look_back_days": {"type": "integer", "description": "Number of days to look back (default: 7)", "default": 7},
                "limit": {"type": "integer", "description": "Maximum number of articles to return (default: 10)", "default": 10},
            },
            "required": ["curr_date"],
        },
    },
    {
        "name": "get_insider_transactions",
        "description": "Retrieve recent insider buying and selling activity for a ticker symbol.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol, e.g. AAPL"},
            },
            "required": ["ticker"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------

def get_news(ticker: str, start_date: str, end_date: str) -> str:
    """Fetch company-specific news via yfinance (or Alpha Vantage if key set)."""
    if AV_KEY:
        return _get_news_alpha_vantage(ticker, start_date, end_date)
    return _get_news_yfinance(ticker, start_date, end_date)


def _get_news_yfinance(ticker: str, start_date: str, end_date: str) -> str:
    try:
        t = yf.Ticker(ticker)
        news = t.news
        if not news:
            return f"No news found for {ticker}."

        start_ts = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
        end_ts = datetime.strptime(end_date, "%Y-%m-%d").timestamp() + 86400

        articles = []
        for item in news:
            pub_ts = item.get("providerPublishTime", 0)
            if start_ts <= pub_ts <= end_ts:
                articles.append(item)

        if not articles:
            # Fall back to most recent 10 articles if date filter yields nothing
            articles = news[:10]

        lines = [f"News for {ticker} ({start_date} to {end_date})", "=" * 60]
        for a in articles:
            ts = datetime.fromtimestamp(a.get("providerPublishTime", 0)).strftime("%Y-%m-%d %H:%M")
            lines.append(f"\n[{ts}] {a.get('title', 'No title')}")
            lines.append(f"Source: {a.get('publisher', 'Unknown')}")
            lines.append(f"URL: {a.get('link', '')}")
            summary = a.get("summary", "") or a.get("description", "")
            if summary:
                lines.append(f"Summary: {summary[:300]}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching news for {ticker}: {e}"


def _get_news_alpha_vantage(ticker: str, start_date: str, end_date: str) -> str:
    try:
        import urllib.request
        time_from = start_date.replace("-", "") + "T0000"
        time_to = end_date.replace("-", "") + "T2359"
        url = (
            f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
            f"&tickers={ticker}&time_from={time_from}&time_to={time_to}"
            f"&limit=20&apikey={AV_KEY}"
        )
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())

        feed = data.get("feed", [])
        if not feed:
            return _get_news_yfinance(ticker, start_date, end_date)

        lines = [f"News for {ticker} ({start_date} to {end_date}) [Alpha Vantage]", "=" * 60]
        for a in feed[:15]:
            lines.append(f"\n[{a.get('time_published', '')[:10]}] {a.get('title', '')}")
            lines.append(f"Source: {a.get('source', '')}")
            lines.append(f"URL: {a.get('url', '')}")
            lines.append(f"Summary: {a.get('summary', '')[:300]}")
            sentiment = a.get("overall_sentiment_label", "")
            score = a.get("overall_sentiment_score", "")
            if sentiment:
                lines.append(f"Sentiment: {sentiment} ({score})")
        return "\n".join(lines)
    except Exception:
        return _get_news_yfinance(ticker, start_date, end_date)


def get_global_news(curr_date: str, look_back_days: int = 7, limit: int = 10) -> str:
    """Fetch broad macroeconomic news. Uses Alpha Vantage if key set, else yfinance proxies."""
    if AV_KEY:
        return _get_global_news_alpha_vantage(curr_date, look_back_days, limit)
    return _get_global_news_yfinance(curr_date, look_back_days, limit)


def _get_global_news_yfinance(curr_date: str, look_back_days: int, limit: int) -> str:
    """Proxy global news via a basket of macro ETFs and indices."""
    macro_tickers = ["SPY", "TLT", "GLD", "DXY", "^VIX"]
    end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=look_back_days)
    start_date = start_dt.strftime("%Y-%m-%d")

    all_articles = []
    seen_titles = set()
    for sym in macro_tickers:
        try:
            t = yf.Ticker(sym)
            for item in (t.news or []):
                title = item.get("title", "")
                if title not in seen_titles:
                    seen_titles.add(title)
                    all_articles.append(item)
        except Exception:
            continue

    all_articles.sort(key=lambda x: x.get("providerPublishTime", 0), reverse=True)

    lines = [f"Global Macro News (last {look_back_days} days, as of {curr_date})", "=" * 60]
    for a in all_articles[:limit]:
        ts = datetime.fromtimestamp(a.get("providerPublishTime", 0)).strftime("%Y-%m-%d %H:%M")
        lines.append(f"\n[{ts}] {a.get('title', 'No title')}")
        lines.append(f"Source: {a.get('publisher', 'Unknown')}")
        lines.append(f"URL: {a.get('link', '')}")
        summary = a.get("summary", "") or a.get("description", "")
        if summary:
            lines.append(f"Summary: {summary[:300]}")

    return "\n".join(lines)


def _get_global_news_alpha_vantage(curr_date: str, look_back_days: int, limit: int) -> str:
    try:
        import urllib.request
        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=look_back_days)
        time_from = start_dt.strftime("%Y%m%d") + "T0000"
        time_to = end_dt.strftime("%Y%m%d") + "T2359"
        topics = "economy_macro,finance,forex,energy_transportation"
        url = (
            f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
            f"&topics={topics}&time_from={time_from}&time_to={time_to}"
            f"&limit={limit}&apikey={AV_KEY}"
        )
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())

        feed = data.get("feed", [])
        if not feed:
            return _get_global_news_yfinance(curr_date, look_back_days, limit)

        lines = [f"Global Macro News (last {look_back_days} days) [Alpha Vantage]", "=" * 60]
        for a in feed[:limit]:
            lines.append(f"\n[{a.get('time_published', '')[:10]}] {a.get('title', '')}")
            lines.append(f"Source: {a.get('source', '')}")
            lines.append(f"URL: {a.get('url', '')}")
            lines.append(f"Summary: {a.get('summary', '')[:300]}")
        return "\n".join(lines)
    except Exception:
        return _get_global_news_yfinance(curr_date, look_back_days, limit)


def get_insider_transactions(ticker: str) -> str:
    try:
        t = yf.Ticker(ticker)
        df = t.insider_transactions
        if df is None or df.empty:
            return f"No insider transaction data found for {ticker}."
        df = df.head(20)
        lines = [f"Insider Transactions for {ticker}", "=" * 60]
        lines.append(df.to_string(index=False))
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching insider transactions for {ticker}: {e}"


# ---------------------------------------------------------------------------
# MCP stdio transport
# ---------------------------------------------------------------------------

TOOLS = {
    "get_news": get_news,
    "get_global_news": get_global_news,
    "get_insider_transactions": get_insider_transactions,
}


def handle_request(request: dict) -> dict:
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "trading-news-data", "version": "1.0.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOL_SCHEMAS}}

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        fn = TOOLS.get(tool_name)
        if not fn:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
        try:
            result = fn(**args)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": result}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}

    if method == "notifications/initialized":
        return None

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    import sys
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}), flush=True)


if __name__ == "__main__":
    main()
