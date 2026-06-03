#!/usr/bin/env python3

import json
import sys
from mcp.server.fastmcp import FastMCP
import clickhouse_connect

# ============================================================================
# INIT
# ============================================================================

mcp = FastMCP("market-data")

# ✅ Create ClickHouse client
client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="default",
    password=""
)

# ============================================================================
# LOAD DATA FROM CLICKHOUSE
# ============================================================================

def load_data():
    result = client.query("SELECT * FROM stock_data")

    # ✅ Convert to dictionary format
    columns = result.column_names
    rows = result.result_rows

    data = [dict(zip(columns, row)) for row in rows]
    return data


DATA = load_data()

# ============================================================================
# TOOLS
# ============================================================================

@mcp.tool()
def fetch_all_data() -> str:
    return json.dumps(DATA)


@mcp.tool()
def fetch_stocks() -> str:
    stocks = sorted(set(row['Stock'] for row in DATA))
    return json.dumps({"stocks": stocks, "count": len(stocks)})


@mcp.tool()
def fetch_dates() -> str:
    dates = sorted(set(row['Date'] for row in DATA))
    return json.dumps({"dates": dates, "count": len(dates)})


@mcp.tool()
def fetch_by_stock(stock: str) -> str:
    stock_upper = stock.upper()
    rows = [r for r in DATA if r['Stock'] == stock_upper]

    if not rows:
        return json.dumps({"error": f"No data found for {stock}"})

    return json.dumps({"stock": stock_upper, "records": len(rows), "data": rows})


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🚀 MCP Server Running...", file=sys.stderr)
    mcp.run(transport="stdio")