import clickhouse_connect

# connect to ClickHouse (WSL)
client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password=''
)

# STEP 3: create table
client.command("""
CREATE TABLE IF NOT EXISTS stock_data (
    date String,
    open Float32,
    high Float32,
    low Float32,
    close Float32,
    volume Int32
) ENGINE = MergeTree()
ORDER BY date
""")

print("Table created successfully")