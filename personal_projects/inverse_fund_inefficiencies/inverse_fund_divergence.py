import yfinance
import datetime
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


# Tickers list must contain pairs of hedgable assets. A weights list can be changed below to scale and flip the returns of these assets, so that
# a graph of their sum will be designed to hedge one another.
tickers = ["SH", "SPY"]

target_ticker = tickers[-1]
donwload_start = datetime.datetime(2000, 1, 1)

ticker_data = yfinance.download(
    tickers,
    start=donwload_start,
    group_by="ticker",
)


# Create a new data frame and populate it with only the close columns
ticker_data_close = pd.DataFrame()

for ticker in tickers:
    try:
        ticker_data_close[ticker] = ticker_data[(ticker, "Close")]
    except:
        tickers.remove(ticker)

# Begin data table where all assets have data (some may have existed longer than others)
earliest_dates = []
for ticker in tickers:
    if ticker_data_close[ticker].first_valid_index() != None:
        earliest_dates.append(ticker_data_close[ticker].first_valid_index())
    else:
        ticker_data_close = ticker_data_close.drop(ticker, 1)

tickers = list(ticker_data_close)

ticker_data_close = ticker_data_close.truncate(before=max(earliest_dates))
ticker_data = ticker_data.truncate(before=max(earliest_dates))

# Convert dollar changes to percent changes
ticker_data_percent = ticker_data_close.pct_change(1)
ticker_data_percent.drop(ticker_data_percent.index[0], inplace=True)

# Add dividends to the tickers. Note that I am only adding the dividend on the day that it is paid out and not to all future values.
# This is because I am preparing to calculate the percentage change day to day.

for ticker in tickers:
    asset_object = yfinance.Ticker(ticker)
    dividend_table = asset_object.dividends
    if len(dividend_table) == 0:
        continue
    dividend_table = dividend_table.reindex_like(ticker_data_percent).fillna(0)

    # Note, division is arranged so that the percent is calculated relative to the close prior to ex-date, since that is how overnight losses
    # due to sell-offs are calculated as well.
    ticker_data_percent[ticker] = ticker_data_percent[
        ticker
    ] + dividend_table / np.array(ticker_data[(ticker, "Close")][:-1])

# Create a list of weights that correspond to tickers, excluding the target ticker. These weights scale and flip the returns of the assets so they can be added below.
ticker_weights = [1]

# Graph returns of "perfectly hedged" portfolio
ticker_data_percent["Hedge"] = ticker_data_percent[tickers[:-1]] @ ticker_weights
ticker_data_percent["Hedged_Portfolio"] = (
    ticker_data_percent[tickers[-1]] + ticker_data_percent["Hedge"]
)


plt.plot(
    ticker_data_percent.index,
    (ticker_data_percent["Hedged_Portfolio"] + 1).cumprod() - 1,
)
plt.xlabel("Date")
plt.ylabel("Decimal Return (% * 100)")
plt.show()

# Plot the two assets on top of one another to watch them diverge.
plt.plot(
    ticker_data_percent.index,
    (ticker_data_percent[target_ticker] + 1).cumprod() - 1,
    label=target_ticker,
)

plt.plot(
    ticker_data_percent.index,
    (-1 * ticker_data_percent["Hedge"] + 1).cumprod() - 1,
    label="Hedge",
)

plt.xlabel("Date")
plt.ylabel("Decimal Return (% * 100)")

plt.legend()
plt.show()
