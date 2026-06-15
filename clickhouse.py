import clickhouse_connect

client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password=''   # empty now
)

print(client.query('SELECT 1').result_rows)