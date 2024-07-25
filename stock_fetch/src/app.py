# import scrape
import scrape

stock_fetcher = scrape.StockFetcher()
stock_fetcher.fetch_all_data(r"\symbol_list\test.csv")