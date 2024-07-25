# Fetching Stock Data using Zerodha Kite Connect

## Usage

1. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

2. **Set Up Environment**:
   Edit the `.env` file in the project with your Kite Connect API credentials and initial from date:

     ```dotenv
     API_KEY=your_api_key
     API_SECRET=your_api_secret
     REQUEST_TOKEN=your_request_token
     FROM_DATE=yyyy-mm-dd  # Set your initial from date here
     ```

3. **Symbols File**:
   The `symbols.csv` file contains a list of stock symbol names whose data you want to fetch. Ensure each symbol is listed in a separate line under the column `symbol`.

4. **Generate Request Token**
   Run `generate_token.py` and login on the link generated in the terminal output. Copy the `request_token=` in the URL after you log in.
     
     ```sh
     python generate_token.py
     ```
     
4. **Run the Script**:
   ```sh
   python app.py
   ```
   This command will fetch and download historical data for the symbols listed in `symbols.csv` and save it to individual CSV files in the `stock_data` directory. Each time the script is run, new data will be appended to these files.

5. **Output**:
   - Individual CSV files for each symbol will be saved in the `stock_data` directory, with filenames in the format `{symbol}.csv`.
   - A file named `sym_list.csv` containing the list of symbols will also be saved in the `stock_data` directory.
   - The `FROM_DATE` in the `.env` file will be updated automatically to the day after the last fetched date to ensure that new data is appended from the correct date in subsequent runs.

