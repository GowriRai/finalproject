#!/usr/bin/env python3
"""
Market Data MCP Server - FastMCP version
Provides tools for Claude to fetch and analyze market data
"""

import json
import csv
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# ============================================================================
# INIT
# ============================================================================

mcp = FastMCP("market-data")

# Always load CSV from same directory as this script
CSV_PATH = Path(__file__).parent / "market_data.csv"

def load_data():
    if not CSV_PATH.exists():
        print(f"❌ market_data.csv not found at {CSV_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CSV_PATH, newline='') as f:
        data = list(csv.DictReader(f))
    print(f"✅ Loaded {len(data)} records from {CSV_PATH}", file=sys.stderr)
    return data

DATA = load_data()

# ============================================================================
# TOOLS
# ============================================================================

@mcp.tool()
def fetch_all_data() -> str:
    """Fetch all market data from CSV"""
    return json.dumps(DATA)


@mcp.tool()
def fetch_stocks() -> str:
    """Get list of all unique stock ticker symbols in the dataset"""
    stocks = sorted(set(row['Stock'] for row in DATA))
    return json.dumps({"stocks": stocks, "count": len(stocks)})


@mcp.tool()
def fetch_dates() -> str:
    """Get list of all unique dates in the dataset"""
    dates = sorted(set(row['Date'] for row in DATA))
    return json.dumps({"dates": dates, "count": len(dates)})


@mcp.tool()
def fetch_by_stock(stock: str) -> str:
    """Get all market data rows for a specific stock ticker symbol"""
    stock_upper = stock.upper()
    rows = [r for r in DATA if r['Stock'] == stock_upper]
    if not rows:
        return json.dumps({
            "error": f"No data found for {stock}",
            "available_stocks": sorted(set(r['Stock'] for r in DATA))
        })
    return json.dumps({"stock": stock_upper, "records": len(rows), "data": rows})


@mcp.tool()
def fetch_by_date(date: str) -> str:
    """Get all market data for a specific date (YYYY-MM-DD format)"""
    rows = [r for r in DATA if r['Date'] == date]
    if not rows:
        return json.dumps({
            "error": f"No data found for {date}",
            "available_dates": sorted(set(r['Date'] for r in DATA))
        })
    return json.dumps({"date": date, "records": len(rows), "data": rows})


@mcp.tool()
def analyze_stock(stock: str) -> str:
    """Calculate detailed price and volume statistics for a specific stock"""
    stock_upper = stock.upper()
    rows = [r for r in DATA if r['Stock'] == stock_upper]
    if not rows:
        return json.dumps({
            "error": f"No data found for {stock}",
            "available_stocks": sorted(set(r['Stock'] for r in DATA))
        })
    try:
        prices = [float(r['Price']) for r in rows]
        volumes = [int(r['Volume']) for r in rows]
        avg_price = sum(prices) / len(prices)
        price_change = prices[-1] - prices[0]
        price_change_pct = (price_change / prices[0] * 100) if prices[0] != 0 else 0
        variance = sum((x - avg_price) ** 2 for x in prices) / len(prices)
        return json.dumps({
            "stock": stock_upper,
            "records": len(rows),
            "date_range": {"first": rows[0]['Date'], "last": rows[-1]['Date']},
            "price": {
                "current": round(prices[-1], 2),
                "average": round(avg_price, 2),
                "min": round(min(prices), 2),
                "max": round(max(prices), 2),
                "range": round(max(prices) - min(prices), 2),
                "change": round(price_change, 2),
                "change_pct": round(price_change_pct, 2)
            },
            "volume": {
                "average": int(sum(volumes) / len(volumes)),
                "total": sum(volumes),
                "min": min(volumes),
                "max": max(volumes)
            },
            "volatility": round(variance ** 0.5, 4)
        })
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def compare_stocks(stocks: list[str]) -> str:
    """Compare multiple stocks side by side"""
    results = {}
    for stock in stocks:
        stock_upper = stock.upper()
        rows = [r for r in DATA if r['Stock'] == stock_upper]
        if not rows:
            results[stock_upper] = {"error": "No data found"}
            continue
        try:
            prices = [float(r['Price']) for r in rows]
            price_change = prices[-1] - prices[0]
            price_change_pct = (price_change / prices[0] * 100) if prices[0] != 0 else 0
            results[stock_upper] = {
                "current_price": round(prices[-1], 2),
                "avg_price": round(sum(prices) / len(prices), 2),
                "min_price": round(min(prices), 2),
                "max_price": round(max(prices), 2),
                "change_pct": round(price_change_pct, 2),
                "trend": "📈 UP" if price_change > 0 else "📉 DOWN" if price_change < 0 else "➡️ FLAT"
            }
        except ValueError as e:
            results[stock_upper] = {"error": str(e)}
    return json.dumps(results)


@mcp.tool()
def calculate_moving_average(stock: str, days: int = 3) -> str:
    """Calculate moving average for a stock over a given number of days"""
    stock_upper = stock.upper()
    rows = [r for r in DATA if r['Stock'] == stock_upper]
    if not rows:
        return json.dumps({"error": f"No data found for {stock}"})
    if len(rows) < days:
        return json.dumps({"error": f"Need at least {days} data points, only have {len(rows)}"})
    prices = [float(r['Price']) for r in rows]
    dates = [r['Date'] for r in rows]
    result = []
    for i in range(len(prices)):
        ma = None if i < days - 1 else sum(prices[i-days+1:i+1]) / days
        result.append({
            "date": dates[i],
            "price": round(prices[i], 2),
            "moving_average": round(ma, 2) if ma is not None else None,
            "vs_ma": round(prices[i] - ma, 2) if ma is not None else None
        })
    return json.dumps({"stock": stock_upper, "days": days, "data": result})


@mcp.tool()
def find_best_performer() -> str:
    """Find the stock with the highest percentage price gain"""
    stocks = set(r['Stock'] for r in DATA)
    best_stock, best_change = None, -float('inf')
    for stock in stocks:
        rows = [r for r in DATA if r['Stock'] == stock]
        prices = [float(r['Price']) for r in rows]
        change_pct = ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] != 0 else 0
        if change_pct > best_change:
            best_change, best_stock = change_pct, stock
    return json.dumps({"stock": best_stock, "change_pct": round(best_change, 2), "status": "📈 BULLISH"})


@mcp.tool()
def find_worst_performer() -> str:
    """Find the stock with the lowest percentage price gain"""
    stocks = set(r['Stock'] for r in DATA)
    worst_stock, worst_change = None, float('inf')
    for stock in stocks:
        rows = [r for r in DATA if r['Stock'] == stock]
        prices = [float(r['Price']) for r in rows]
        change_pct = ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] != 0 else 0
        if change_pct < worst_change:
            worst_change, worst_stock = change_pct, stock
    return json.dumps({"stock": worst_stock, "change_pct": round(worst_change, 2), "status": "📉 BEARISH"})


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting Market Data MCP Server (FastMCP)...", file=sys.stderr)
    mcp.run(transport="stdio")