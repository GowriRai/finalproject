import clickhouse_connect

client = clickhouse_connect.get_client(
    host="172.28.172.119",
    port=8123,
    username="default",
    password=""
)

result = client.query("SELECT 1")
client.command("USE mystocks_db")
print(client.query("SHOW DATABASES").result_rows)
result = client.query("SELECT * FROM stock_data LIMIT 5")
print(result.result_rows)