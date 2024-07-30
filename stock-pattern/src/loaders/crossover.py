import os
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib.dates import DateFormatter, DayLocator


def detect_ema_crossovers(data):
    # Calculate EMAs
    data['EMA_9'] = ta.trend.ema_indicator(data['Close'], window=9)
    data['EMA_18'] = ta.trend.ema_indicator(data['Close'], window=18)
    data['EMA_44'] = ta.trend.ema_indicator(data['Close'], window=44)

    # Detect when EMA_9 crosses above EMA_18
    data['EMA_9_above_18'] = (data['EMA_9'] > data['EMA_18']).astype(int)
    data['EMA_9_above_18_shifted'] = data['EMA_9_above_18'].shift(1, fill_value=0)
    data['cross_9_above_18'] = (data['EMA_9_above_18'] - data['EMA_9_above_18_shifted'] == 1)

    # Detect when EMA_18 crosses above EMA_44
    data['EMA_18_above_44'] = (data['EMA_18'] > data['EMA_44']).astype(int)
    data['EMA_18_above_44_shifted'] = data['EMA_18_above_44'].shift(1, fill_value=0)
    data['cross_18_above_44'] = (data['EMA_18_above_44'] - data['EMA_18_above_44_shifted'] == 1)

    # Detect when both conditions are true
    data['all_crosses'] = data['cross_9_above_18'] & data['cross_18_above_44']

    # Store crossover dates and prices
    data['cross_date'] = np.where(data['all_crosses'], data.index, pd.NaT)
    data['cross_price'] = np.where(data['all_crosses'], data['Close'], np.nan)

    return data


def plot_crossovers(data, stock_name, output_folder):
    cross_points = data[data['all_crosses']]
    if not cross_points.empty:
        mc = mpf.make_marketcolors(up='g', down='r', edge='inherit', wick='inherit')
        s = mpf.make_mpf_style(marketcolors=mc)

        add_plot = [
            mpf.make_addplot(data['EMA_9'], color='blue', label='9 EMA'),
            mpf.make_addplot(data['EMA_18'], color='orange', label='18 EMA'),
            mpf.make_addplot(data['EMA_44'], color='purple', label='44 EMA'),
            mpf.make_addplot(data['cross_price'], type='scatter', marker='o', markersize=50, color='red')
        ]

        fig, axlist = mpf.plot(
            data,
            type='candle',
            style=s,
            addplot=add_plot,
            title=f'Crossover Points for {stock_name}',
            ylabel='Price',
            returnfig=True,
            volume=False,
            show_nontrading=True
        )

        # Customize x-axis
        axlist[0].xaxis.set_major_locator(DayLocator(interval=7))  # Set major ticks to every week
        axlist[0].xaxis.set_major_formatter(DateFormatter('%b %d'))  # Format ticks to show month and day
        fig.autofmt_xdate()  # Rotate date labels for better readability

        handles, labels = axlist[0].get_legend_handles_labels()
        axlist[0].legend(handles, labels)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        plt.savefig(os.path.join(output_folder, f'{stock_name}_crossovers.png'))
        plt.close()


def process_stock_files(directory_path, output_folder, date_col='Date'):
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            stock_name = filename.split('.')[0]
            file_path = os.path.join(directory_path, filename)
            data = pd.read_csv(file_path)

            if date_col not in data.columns:
                print(f"Skipping {stock_name} due to missing '{date_col}' column.")
                continue

            data[date_col] = pd.to_datetime(data[date_col])
            data.set_index(date_col, inplace=True)
            data = detect_ema_crossovers(data)
            plot_crossovers(data, stock_name, output_folder)
            print(f'Processed {stock_name}')


if __name__ == "__main__":
    directory_path = 'D:\RapidHire\stock_final\stock_fetch\src\stock_data'
    output_folder = 'images'  # Folder to save the images
    process_stock_files(directory_path, output_folder, date_col='Date')
