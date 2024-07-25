from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockFetcher:
    def __init__(self, api_key=None, api_secret=None, request_token=None, interval="day", from_date=None):
        load_dotenv()

        self.api_key = api_key or os.getenv('API_KEY')
        self.api_secret = api_secret or os.getenv('API_SECRET')
        self.request_token = request_token or os.getenv('REQUEST_TOKEN')
        self.interval = interval
        self.from_date = from_date or os.getenv('FROM_DATE')

        self.kite = KiteConnect(api_key=self.api_key)
        self.access_token = self._generate_access_token()
        self.kite.set_access_token(self.access_token)
        self.instrument_lookup = self._create_instrument_lookup()

        self.to_date = self._get_yesterday_date()

    def _generate_access_token(self):
        try:
            # Generate session to get the access token
            data = self.kite.generate_session(self.request_token, api_secret=self.api_secret)
            return data["access_token"]
        except Exception as e:
            logger.error(f"Error generating access token: {e}")
            raise

    def _get_yesterday_date(self):
        current_date = datetime.now()
        yesterday_date = current_date - timedelta(days=1)
        return yesterday_date.strftime("%Y-%m-%d")

    def _create_instrument_lookup(self):
        try:
            instruments = self.kite.instruments()
            return {instrument['tradingsymbol']: instrument['instrument_token'] for instrument in instruments if instrument['exchange'] == 'NSE'}
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            raise

    def fetch_historical_data(self, symbol):
        try:
            instrument_token = self.instrument_lookup.get(symbol)
            if instrument_token is None:
                raise ValueError(f"Instrument token not found for symbol: {symbol}")

            historical_data = self.kite.historical_data(instrument_token, self.from_date, self.to_date, self.interval)
            df = pd.DataFrame(historical_data)
            df['symbol'] = symbol
            df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]
            return df
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise

    def fetch_all_data(self, symbols_file, output_dir="stock_data"):
        try:
            symbols_df = pd.read_csv(symbols_file)
            symbols = symbols_df['symbol'].tolist()

            os.makedirs(output_dir, exist_ok=True)

            for symbol in symbols:
                try:
                    new_data = self.fetch_historical_data(symbol)
                    
                    # Transform the new data
                    new_data['date'] = pd.to_datetime(new_data['date']).dt.date
                    new_data['volume'] = new_data['volume'].astype(float)
                    new_data['TOTAL_TRADES'] = None
                    new_data['QTY_PER_TRADE'] = None
                    new_data['DLV_QTY'] = None
                    new_data.columns = ['symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'TOTAL_TRADES', 'QTY_PER_TRADE', 'DLV_QTY']

                    # Path to the individual CSV file for the symbol
                    symbol_file = f"{output_dir}/{symbol}.csv"

                    if os.path.exists(symbol_file):
                        existing_data = pd.read_csv(symbol_file)
                        combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=['Date']).sort_values(by='Date')
                    else:
                        combined_data = new_data

                    # Save the combined data to the CSV file
                    combined_data.to_csv(symbol_file, index=False)
                    logger.info(f"Saved {symbol}.csv")
                    
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")

            # Save list of symbols to a CSV file
            sym_csv = pd.DataFrame(symbols, columns=['symbol'])
            sym_csv.to_csv(f"{output_dir}/sym_list.csv", index=False)
            logger.info(f"Symbol list saved to sym_list.csv")

            # Update the from_date in .env file
            new_from_date = (datetime.strptime(self.to_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            set_key('.env', 'FROM_DATE', new_from_date)
        except Exception as e:
            logger.error(f"Error processing symbols file: {e}")
            raise

if __name__ == "__main__":
    fetcher = StockFetcher()
    fetcher.fetch_all_data("symbols.csv")
