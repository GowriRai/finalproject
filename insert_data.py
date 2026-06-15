import clickhouse_connect
import pandas as pd

# connect to ClickHouse
client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password=''
)

# read CSV
df = pd.read_csv("market_data.csv")

# insert into ClickHouse
client.insert_df("stock_data", df)

print("Data inserted successfully")