import yfinance
import datetime
import sympy
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import symengine

# List of tickers to create custom portfolio and hedge target ticker below.
# For testing purposes, try including the target ticker in the tickers list.I'm cheating by hedging an etf with its constituents.
tickers = [
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOG",
    "XOM",
    "UNH",
    "JNJ",
    "NVDA",
    "JPM",
    "V",
    "PG",
    "HD",
    "TSLA",
    "MA",
    "CVX",
    "META",
    "MRK",
]


target_ticker = "SPY"
start_download = datetime.datetime(2000, 1, 1)

ticker_data = yfinance.download(
    tickers,
    start=start_download,
    group_by="ticker",
)

target_ticker_data = yfinance.download(
    target_ticker,
    start=start_download,
    group_by="ticker",
)


# Create a new data frame and populate it with only the close columns
tickers_close_data = pd.DataFrame()
target_ticker_close_data = pd.DataFrame()

for ticker in tickers:
    try:
        tickers_close_data[ticker] = ticker_data[(ticker, "Close")]
    except:
        tickers.remove(ticker)

target_ticker_close_data = target_ticker_data["Close"]

# Find the earliest date that contains data for all stocks
earliest_dates = []
for asset in tickers:
    if tickers_close_data[asset].first_valid_index() != None:
        earliest_dates.append(tickers_close_data[asset].first_valid_index())
    else:
        tickers_close_data = tickers_close_data.drop(asset, 1)

earliest_dates.append(target_ticker_close_data.first_valid_index())

# Update asset list to exclude stocks for whom no data was returned
tickers = list(tickers_close_data)

# Remove all data before earliest date
tickers_close_data = tickers_close_data.truncate(before=max(earliest_dates))
target_ticker_close_data = target_ticker_close_data.truncate(before=max(earliest_dates))

# Convert dollar changes to percent changes and drop the first row
tickers_percent_data = tickers_close_data.pct_change(1)
tickers_percent_data.drop(tickers_percent_data.index[0], inplace=True)

target_ticker_percent_data = target_ticker_close_data.pct_change(1)
target_ticker_percent_data.drop(target_ticker_percent_data.index[0], inplace=True)


# For simplicity, dividends are excluded. Any practical applicatino of this algorithm will require additional code to account for dividends.

# Create a list of variable weights corresponding to every ticker.
ticker_weight_variables = []
for ticker_number in range(0, len(tickers)):
    ticker_weight_variables.append(
        symengine.Symbol("w" + str(ticker_number), real=True)
    )


# We will be minimizing a custom function that represents the sum of square differences between portfolio returns and target returns over some optimization length.
optimization_length = 150


Weights = np.array(ticker_weight_variables).reshape(1, -1)

daily_return = []
for ticker_number in range(0, len(ticker_weight_variables)):
    ticker = tickers[ticker_number]
    daily_return.append(tickers_percent_data[ticker][0])

daily_return = np.array(daily_return).reshape(-1, 1)

# Create the first term of the function. The squared difference between the percentage return of the target asset and the rest of the portfolio.
least_squares_function = (target_ticker_percent_data[0] - Weights @ daily_return) ** 2

# Repeat the steps above for the rest of the optimization length
for date_position in range(1, optimization_length):

    daily_return = []
    for ticker_position in range(0, len(ticker_weight_variables)):
        ticker = tickers[ticker_position]
        daily_return.append(tickers_percent_data[ticker][date_position])

    daily_return = np.array(daily_return).reshape(-1, 1)
    todays_component = (
        target_ticker_percent_data[date_position] - Weights @ daily_return
    ) ** 2
    least_squares_function = least_squares_function + todays_component

# Strip outer parentheses
least_squares_function = least_squares_function[0][0]


# Apply "sum of absolute value of weights must equal 1" constraint
apply_contraints = False
if apply_contraints:
    onesVector = np.ones((Weights.shape[1], 1))
    sum_one_constraint = abs(Weights) @ onesVector
    lambda_variable = sympy.Symbol("L", real=True)
    lagrangian_function = least_squares_function - lambda_variable * (
        sum_one_constraint - 1
    )
    lagrangian_function = lagrangian_function[0][0]
else:
    lagrangian_function = least_squares_function

system_of_equations = []
# Differentiate with respect to each variable in list. The upcoming equation solver doesn't understand the sign() function that represents absolute value derivatives, therefore we manually replace
for symbol in ticker_weight_variables:
    derivative_wrt_symbol = symengine.diff(lagrangian_function, symbol)
    derivative_of_abs = symbol / abs(symbol)
    derivative_wrt_symbol = derivative_wrt_symbol.replace(
        sympy.sign(symbol), derivative_of_abs
    )
    derivative_wrt_symbol = derivative_wrt_symbol.expand()
    system_of_equations.append(derivative_wrt_symbol)

# Append derivative wrt lambda
if apply_contraints:
    system_of_equations.append(sympy.diff(lagrangian_function, lambda_variable))

initial_guess_vector = []
for n in range(0, len(ticker_weight_variables)):
    initial_guess_vector.append(1 / len(ticker_weight_variables))

if apply_contraints:
    initial_guess_vector.append(0.5)
    ticker_weight_variables.append(lambda_variable)

solution = sympy.nsolve(
    system_of_equations, ticker_weight_variables, initial_guess_vector, verify=False
)

# Remove the lambda variable from the solution. Keep only weights
if apply_contraints:
    solution = np.array(solution).reshape(-1, 1)[:-1]
else:
    solution = np.array(solution).reshape(-1, 1)

print("Matrix solution: " + str(solution))

# Graphing optimal solution
backtest_data = pd.concat(
    [tickers_percent_data, tickers_percent_data @ solution],
    axis=1,
)
backtest_data.rename({0: "Optimal_Solution"}, axis=1, inplace=True)

# Plot optimal solution
plt.plot(
    backtest_data.index,
    (backtest_data["Optimal_Solution"] + 1).cumprod() - 1,
    label="Optimal Solution",
)

# Plot target returns
plt.plot(
    backtest_data.index,
    (target_ticker_percent_data + 1).cumprod() - 1,
    label=target_ticker,
)

plt.ylabel("Decimal Change (% * 100)")
plt.xlabel("Date")

plt.legend()
plt.show()
