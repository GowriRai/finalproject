from market_data import MarketDataManager

manager = MarketDataManager()

data = manager.get_all_data()

for row in data:
    print(row)