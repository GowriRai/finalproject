import clickhouse_connect

class MarketDataManager:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='default',
            password=''
        )

    def get_all_data(self):
        query = "SELECT * FROM stock_data"
        result = self.client.query(query)

        columns = result.column_names
        return [dict(zip(columns, row)) for row in result.result_rows]