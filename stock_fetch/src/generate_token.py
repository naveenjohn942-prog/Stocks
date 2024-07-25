from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

load_dotenv()
kite = KiteConnect(api_key=os.getenv('API_KEY'))
url = kite.login_url()

