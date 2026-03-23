"""
MCP Server: Market & Financial Data
Wraps yfinance (default) and Alpha Vantage for stock price, technical indicators,
and fundamental data. Register this server in your MCP config to give Copilot
access to all market data tools.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    raise RuntimeError("Install dependencies: pip install yfinance pandas stockstats")

# Optional Alpha Vantage support
AV_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")

# ---------------------------------------------------------------------------
# MCP Tool Definitions (JSON Schema for Copilot MCP registration)
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "get_stock_data",
        "description": "Retrieve OHLCV stock price data for a given ticker symbol.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Ticker symbol, e.g. AAPL, TSLA, 9984.T"},
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
            },
            "required": ["symbol", "start_date", "end_date"],
        },
    },
    {
        "name": "get_indicators",
        "description": (
            "Retrieve a technical indicator for a given ticker symbol. "
            "Available indicators: close_50_sma, close_200_sma, close_10_ema, "
            "macd, macds, macdh, rsi, boll, boll_ub, boll_lb, atr, vwma. "
            "Call once per indicator."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Ticker symbol"},
                "indicator": {"type": "string", "description": "Indicator name, e.g. rsi, macd, boll"},
                "curr_date": {"type": "string", "description": "Current trading date in YYYY-MM-DD format"},
                "look_back_days": {"type": "integer", "description": "Days to look back (default: 30)", "default": 30},
            },
            "required": ["symbol", "indicator", "curr_date"],
        },
    },
    {
        "name": "get_fundamentals",
        "description": "Retrieve comprehensive fundamental data (valuation ratios, key metrics, company profile) for a ticker.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
                "curr_date": {"type": "string", "description": "Current date in YYYY-MM-DD format"},
            },
            "required": ["ticker", "curr_date"],
        },
    },
    {
        "name": "get_balance_sheet",
        "description": "Retrieve balance sheet data (assets, liabilities, equity) for a ticker.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
                "freq": {"type": "string", "description": "annual or quarterly (default: quarterly)", "default": "quarterly"},
                "curr_date": {"type": "string", "description": "Current date in YYYY-MM-DD format"},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_cashflow",
        "description": "Retrieve cash flow statement (operating, investing, financing) for a ticker.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
                "freq": {"type": "string", "description": "annual or quarterly (default: quarterly)", "default": "quarterly"},
                "curr_date": {"type": "string", "description": "Current date in YYYY-MM-DD format"},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_income_statement",
        "description": "Retrieve income statement (revenue, expenses, net income) for a ticker.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol"},
                "freq": {"type": "string", "description": "annual or quarterly (default: quarterly)", "default": "quarterly"},
                "curr_date": {"type": "string", "description": "Current date in YYYY-MM-DD format"},
            },
            "required": ["ticker"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------

def get_stock_data(symbol: str, start_date: str, end_date: str) -> str:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        if df.empty:
            return f"No price data found for {symbol} between {start_date} and {end_date}."
        df.index = df.index.strftime("%Y-%m-%d")
        return df[["Open", "High", "Low", "Close", "Volume"]].to_string()
    except Exception as e:
        return f"Error fetching stock data for {symbol}: {e}"


def get_indicators(symbol: str, indicator: str, curr_date: str, look_back_days: int = 30) -> str:
    try:
        from stockstats import StockDataFrame

        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=look_back_days + 60)  # extra buffer for indicator warmup

        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_dt.strftime("%Y-%m-%d"), end=curr_date)
        if df.empty:
            return f"No data found for {symbol}."

        df = df.rename(columns={"Open": "open", "High": "high", "Low": "low",
                                  "Close": "close", "Volume": "volume"})
        sdf = StockDataFrame.retype(df.copy())

        # Map friendly names to stockstats column names
        indicator_map = {
            "close_50_sma": "close_50_sma",
            "close_200_sma": "close_200_sma",
            "close_10_ema": "close_10_ema",
            "macd": "macd",
            "macds": "macds",
            "macdh": "macdh",
            "rsi": "rsi_14",
            "boll": "boll",
            "boll_ub": "boll_ub",
            "boll_lb": "boll_lb",
            "atr": "atr",
            "vwma": "vwma",
        }
        col = indicator_map.get(indicator.lower(), indicator.lower())
        _ = sdf[col]  # trigger computation

        result_df = sdf[[col]].tail(look_back_days)
        result_df.index = result_df.index.strftime("%Y-%m-%d")
        return f"{indicator} for {symbol} (last {look_back_days} days):\n{result_df.to_string()}"
    except Exception as e:
        return f"Error computing {indicator} for {symbol}: {e}"


def get_fundamentals(ticker: str, curr_date: str) -> str:
    try:
        t = yf.Ticker(ticker)
        info = t.info
        keys = [
            "longName", "sector", "industry", "country", "fullTimeEmployees",
            "marketCap", "enterpriseValue", "trailingPE", "forwardPE",
            "priceToBook", "priceToSalesTrailing12Months", "enterpriseToEbitda",
            "profitMargins", "operatingMargins", "grossMargins", "returnOnEquity",
            "returnOnAssets", "revenueGrowth", "earningsGrowth",
            "totalDebt", "totalCash", "freeCashflow", "operatingCashflow",
            "currentRatio", "quickRatio", "debtToEquity",
            "dividendYield", "payoutRatio", "beta",
            "52WeekChange", "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
            "targetMeanPrice", "recommendationMean", "numberOfAnalystOpinions",
            "longBusinessSummary",
        ]
        lines = [f"Fundamentals for {ticker} (as of {curr_date})", "=" * 60]
        for k in keys:
            v = info.get(k)
            if v is not None:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {e}"


def get_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_balance_sheet if freq == "quarterly" else t.balance_sheet
        if df is None or df.empty:
            return f"No balance sheet data found for {ticker}."
        df.columns = [str(c)[:10] for c in df.columns]
        return f"Balance Sheet ({freq}) for {ticker}:\n{df.to_string()}"
    except Exception as e:
        return f"Error fetching balance sheet for {ticker}: {e}"


def get_cashflow(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_cashflow if freq == "quarterly" else t.cashflow
        if df is None or df.empty:
            return f"No cash flow data found for {ticker}."
        df.columns = [str(c)[:10] for c in df.columns]
        return f"Cash Flow Statement ({freq}) for {ticker}:\n{df.to_string()}"
    except Exception as e:
        return f"Error fetching cash flow for {ticker}: {e}"


def get_income_statement(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_income_stmt if freq == "quarterly" else t.income_stmt
        if df is None or df.empty:
            return f"No income statement data found for {ticker}."
        df.columns = [str(c)[:10] for c in df.columns]
        return f"Income Statement ({freq}) for {ticker}:\n{df.to_string()}"
    except Exception as e:
        return f"Error fetching income statement for {ticker}: {e}"


# ---------------------------------------------------------------------------
# MCP stdio transport
# ---------------------------------------------------------------------------

TOOLS = {
    "get_stock_data": get_stock_data,
    "get_indicators": get_indicators,
    "get_fundamentals": get_fundamentals,
    "get_balance_sheet": get_balance_sheet,
    "get_cashflow": get_cashflow,
    "get_income_statement": get_income_statement,
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
                "serverInfo": {"name": "trading-market-data", "version": "1.0.0"},
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
        return None  # no response needed

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
