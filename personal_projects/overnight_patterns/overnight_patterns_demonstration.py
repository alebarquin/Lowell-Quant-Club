import yfinance as yf
from matplotlib import pyplot as plt
import numpy as np
import datetime
import pandas as pd
import math

ticker = "KO"

# Include or exclude dividends from demonstration. Dividend payments often cause a proportional decline in the price of
# the asset in the overnight session following the dividend ex-date. Adding them back may provide a clearer understanding of overnight performance.
count_dividends = True


ticker_price_data = yf.download(
    ticker,
    start=datetime.datetime(
        2000,
        1,
        1,
    ),
    interval="1d",
)

ticker_object = yf.Ticker(ticker)
dividend_history = ticker_object.dividends

# The overnight returns list corresponds to the night before the day session at the same index.
# ex. Date: 2022-1-11. The overnight returns value corresponding to this date represents the period that began at the previous day's close
# (on 2022-1-10), and is part of the same single day returns that include the day session of 2022-1-11.

intraday_returns_graphY = []
intraday_returns_graphX = []

overnight_returns_graphY = []
overnight_returns_graphX = []

weekend_returns_graphY = []
weekend_returns_graphX = []


# Loop through the data and record the cumulative return of the intraday, overnight, and weekend periods.

for n in range(1, len(ticker_price_data.index)):

    current_index = ticker_price_data.index[n]
    previous_index = ticker_price_data.index[n - 1]

    # Today's intraday returns
    intraday_returns_graphY.append(
        (
            ticker_price_data["Close"][current_index]
            - ticker_price_data["Open"][current_index]
        )
        / ticker_price_data["Open"][current_index]
    )

    intraday_returns_graphX.append(current_index)

    # Seperate weekend sessions from the weekday overnight returns
    # **if statement checks for Mondays, following weekend.**

    if current_index.weekday() == 0:
        weekend_returns_graphY.append(
            (
                ticker_price_data["Open"][current_index]
                - ticker_price_data["Close"][previous_index]
            )
            / ticker_price_data["Close"][previous_index]
        )
        weekend_returns_graphX.append(current_index)
    else:

        overnight_returns_graphY.append(
            (
                ticker_price_data["Open"][current_index]
                - ticker_price_data["Close"][previous_index]
            )
            / ticker_price_data["Close"][previous_index]
        )
        overnight_returns_graphX.append(current_index)

        # Add back dividends in overnight session to correct for after hour sell-off post payout.
        if count_dividends:
            if current_index in dividend_history:
                overnight_returns_graphY[-1] = (
                    overnight_returns_graphY[-1]
                    + dividend_history[current_index]
                    / ticker_price_data["Close"][previous_index]
                )


# Plot the overnight, intraday, and weekend returns
# Convert lists of discrete returns into cumulative returns.

starting_equity = ticker_price_data["Close"][ticker_price_data.index[0]]

cumulative_intraday_returns = (
    np.cumprod(np.array(intraday_returns_graphY) + 1) * starting_equity
)

cumulative_overnight_returns = (
    np.cumprod(np.array(overnight_returns_graphY) + 1) * starting_equity
)

cumulative_weekend_returns = (
    np.cumprod(np.array(weekend_returns_graphY) + 1) * starting_equity
)

# I can also choose to graph the total return of the underlying asset for comparison (include dividends)
ticker_performance_dividendAdj = ticker_price_data

for div_date in dividend_history.index:
    if div_date > ticker_price_data.index[0]:
        ticker_performance_dividendAdj["Close"][div_date:] += dividend_history[div_date]

# Control the y-axis scale. Set scale to "log" for relative scale
plt.yscale("log")

plt.plot(
    ticker_performance_dividendAdj.index,
    ticker_performance_dividendAdj["Close"],
    label="Total Return",
)

plt.plot(intraday_returns_graphX, cumulative_intraday_returns, label="Intraday Return")

plt.plot(
    overnight_returns_graphX, cumulative_overnight_returns, label="Overnight Return"
)

plt.plot(weekend_returns_graphX, cumulative_weekend_returns, label="Weekend Return")

plt.legend(fontsize="large")
plt.title(ticker)
plt.show()


# Calculate and visualize the correlation between different parts of the day.
# Separate Mondays from the intraday returns, so that one list of Mondays can be compared to weekends, and the other can be compared to regular
# weekday overnight returns.

monday_intraday_returns = []
intraday_returns_excluding_monday = []

for n in range(len(intraday_returns_graphX)):
    if intraday_returns_graphX[n].weekday() != 0:
        intraday_returns_excluding_monday.append(intraday_returns_graphY[n])
    else:
        monday_intraday_returns.append(intraday_returns_graphY[n])

smooth_period = 200
weekend_smooth_period = 200

smoothed_overnight_returns = list(
    pd.Series(overnight_returns_graphY).rolling(smooth_period).mean()
)
smoothed_intraday_returns_no_monday = list(
    pd.Series(intraday_returns_excluding_monday).rolling(smooth_period).mean()
)
smoothed_intraday_returns_monday = list(
    pd.Series(monday_intraday_returns).rolling(weekend_smooth_period).mean()
)
smoothed_weekend_returns = list(
    pd.Series(weekend_returns_graphY).rolling(weekend_smooth_period).mean()
)

# Remove nan values that occur at the start of the list as a result of insufficient data to calculate a trailing average.

smoothed_overnight_returns = [
    x for x in smoothed_overnight_returns if math.isnan(x) == False
]

smoothed_intraday_returns_no_monday = [
    x for x in smoothed_intraday_returns_no_monday if math.isnan(x) == False
]

smoothed_intraday_returns_monday = [
    x for x in smoothed_intraday_returns_monday if math.isnan(x) == False
]

smoothed_weekend_returns = [
    x for x in smoothed_weekend_returns if math.isnan(x) == False
]

print("Overnight and Intraday Smoothed Weekday Correlation")
print(np.corrcoef(smoothed_overnight_returns, smoothed_intraday_returns_no_monday))
plt.scatter(smoothed_overnight_returns, smoothed_intraday_returns_no_monday)

plt.title("Overnight vs Intraday")
plt.xlabel("Overnight Returns")
plt.ylabel("Intraday Returns")
plt.show()

print("Weekend and Monday Intraday Smoothed Correlation")
print(np.corrcoef(smoothed_weekend_returns, smoothed_intraday_returns_monday))
plt.scatter(smoothed_weekend_returns, smoothed_intraday_returns_monday)

plt.title("Weekend vs Monday Intraday")
plt.xlabel("Weekend Returns")
plt.ylabel("Intrady Monday Returns")
plt.show()
