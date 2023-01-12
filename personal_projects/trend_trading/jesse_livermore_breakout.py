from datetime import datetime
from datetime import timedelta
import yfinance
import pandas_market_calendars as mcal
import stockstats
import json
import matplotlib.pyplot as plt
import numpy as np
import statistics

NYSE = mcal.get_calendar("NYSE")
marketCalendar = NYSE.schedule(start_date="2010-01-01", end_date="2023-12-30").index

# Arrays for plotting strategy equity
strategyDates = []
strategyReturns = []
# --- #

# Get historical SPY constituents
with open("historicalSPYConstituents.txt") as f:
    tickers = f.read()

constituents = json.loads(tickers)
# --- #

# Convert date:constituents dictionary to a complete list of stocks needed for backtest
stocksList = []

for key in constituents:
    stocksList.extend(constituents[key])

# Remove duplicates
stocksList = list(set(stocksList))

dataStart = datetime(2012, 1, 1)
stocksData = yfinance.download(stocksList, start=dataStart)
# ---#

# Define how to reference table data depending on date table format. Time refers to open or close.
def tableReference(ticker, date, time):
    return stocksData[(time, ticker)][date]


# --- #

# Function to increment date until it falls on a regular market trading day
def incrementDate(current_date, direction):
    if direction == "forward":
        increment_direction = 1
    elif direction == "backward":
        increment_direction = -1

    output_date = current_date + timedelta(days=increment_direction)
    while output_date not in marketCalendar:
        output_date = output_date + timedelta(days=increment_direction)

    return output_date


backtest_date = datetime(2013, 3, 5)

# SPY dataframe for measuring market trends
spy_data = yfinance.download("SPY", period="20y")
spy_formatted_data = stockstats.StockDataFrame.retype(spy_data)

yf_spy_ticker = yfinance.Ticker("SPY")
spy_dividends = yf_spy_ticker.dividends

# Creating a second table, where the closing prices are adjusted for dividends. This will be used to calculate raw performance.
# The values will only be updated after the backtest begins to maintain equal starting capital based on share price.
spy_performance_dividendAdj = yfinance.download("SPY", period="20y")

for div_date in spy_dividends.index:
    if div_date > backtest_date:
        spy_performance_dividendAdj["Close"][div_date:] += spy_dividends[div_date]

# Define class for storing details of position
class createPosition:
    def __init__(self, shares, consecutive_entries, avg_price, entry_date):
        self.shares = shares
        self.consecutive_entries = consecutive_entries
        self.avg_price = avg_price
        self.entry_date = entry_date


openPositions = {}
tradingLog = {}

# Backtest variables
max_trade_percent = 0.1
cashEquity = spy_data["close"][backtest_date]
shareEquity = 0

# previousYear is used to check for new year and record annual equity
previousYear = backtest_date.year
annual_backtest_equity = {backtest_date: cashEquity}
annual_spy_equity = {backtest_date: cashEquity}

# Backtest statistics, hold totals, averages calculated at the end
losing_trades = 0
winning_trades = 0
losing_trade_losses = 0
winning_trade_gains = 0

# Keep track of average length of winning and losing positions, holds totals, averages calculated at the end
losing_trade_length = 0
winning_trade_length = 0

# To graph number of simulatenous positions
unique_positions_graphX = []
unique_positions_graphY = []


# To graph percent of portfolio invested
percent_invested_graphX = []
percent_invested_graphY = []

# To update the historical contituents list throughout the backtest
constituentsKeys = list(constituents.keys())

keys_dateform = []

for key in constituentsKeys:
    keys_dateform.append(datetime.strptime(key, "%Y/%m/%d"))

constituentsKeyIndex = 0
while keys_dateform[constituentsKeyIndex] < backtest_date:
    constituentsKeyIndex += 1
    # Rewind counter to last value that is less than backtest start date
    if keys_dateform[constituentsKeyIndex] > backtest_date:
        constituentsKeyIndex -= 1
        break

print("Starting constituents list: " + str([constituentsKeys[constituentsKeyIndex]]))

# Calculate equity function

# Referencing dividend history is slow so instead I will save previously downloaded data
dividend_history_database = {}


def calculateEquity(_backtest_date, _cashEquity):
    global dividend_history_database
    _shareEquity = 0
    if len(openPositions) > 0:
        for ticker in openPositions:
            if openPositions[ticker] == 0:
                continue
            _shareEquity = _shareEquity + (
                openPositions[ticker].shares
                * tableReference(ticker, _backtest_date, "Close")
            )
            if ticker not in list(dividend_history_database.keys()):
                yf_ticker = yfinance.Ticker(ticker)
                dividends_history = yf_ticker.dividends
                dividend_history_database[ticker] = dividends_history

            dividends_history = dividend_history_database[ticker]
            if _backtest_date in dividends_history.index:
                _cashEquity += (
                    dividends_history[_backtest_date] * openPositions[ticker].shares
                )

    return _shareEquity, _cashEquity


while backtest_date < datetime(2023, 1, 10):

    # Record annual performance, where previousYear is last trading day's year, then update previousYear
    if backtest_date.year != previousYear:
        annual_backtest_equity[backtest_date] = totalEquity
        annual_spy_equity[backtest_date] = spy_performance_dividendAdj["Close"][
            backtest_date
        ]
    previousYear = backtest_date.year

    # Update constituents list, but check that I won't index out of bounds
    if (
        backtest_date in keys_dateform
        and constituentsKeyIndex < len(constituentsKeys) - 1
    ):
        constituentsKeyIndex = constituentsKeyIndex + 1

    # List ends with 2019-2-27 but I may opt to skip to custom present day list instead.
    use_present_list = True
    if backtest_date == datetime(2019, 2, 27) and use_present_list:
        constituentsKeyIndex = constituentsKeyIndex + 1

    # Add todays date to trading log
    tradingLog.setdefault(backtest_date, [])

    # Check for market downturn, hold positions if not company specific
    sma = spy_formatted_data["close_25_sma"][backtest_date]
    close = spy_data["close"][backtest_date]

    if close < sma:
        tradingLog.pop(backtest_date)
        shareEquity, cashEquity = calculateEquity(backtest_date, cashEquity)
        totalEquity = cashEquity + shareEquity

        strategyDates.append(backtest_date)
        strategyReturns.append(totalEquity)

        percent_invested_graphX.append(backtest_date)
        stockProportion = shareEquity / totalEquity
        percent_invested_graphY.append(stockProportion)

        backtest_date = incrementDate(backtest_date, "forward")
        continue

    # Next available date, assets are sold at open
    tomorrow = incrementDate(backtest_date, "forward")

    print("Date: " + str(backtest_date))
    if len(openPositions) > 0:

        for ticker in openPositions:

            if openPositions[ticker] == 0:
                # Previously held tickers with no current position are tagged with 0
                continue

            lows = []

            current_index_position = stocksData.index.get_loc(backtest_date)
            last_50_close = list(
                stocksData[("Close", ticker)][
                    current_index_position - 49 : current_index_position + 1
                ]
            )
            last_50_open = list(
                stocksData[("Open", ticker)][
                    current_index_position - 49 : current_index_position + 1
                ]
            )
            last_50_close.extend(last_50_open)
            minimum = min(last_50_close)

            if minimum == tableReference(ticker, backtest_date, "Close"):
                # If today is the minimum, close the position
                percent_profit = (
                    tableReference(ticker, tomorrow, "Open")
                    - openPositions[ticker].avg_price
                ) / openPositions[ticker].avg_price

                if percent_profit < 0:
                    losing_trade_losses = losing_trade_losses + percent_profit
                    losing_trades += 1
                    dif = backtest_date - openPositions[ticker].entry_date
                    losing_trade_length = losing_trade_length + int(dif.days)
                else:
                    winning_trade_gains = winning_trade_gains + percent_profit
                    winning_trades += 1
                    dif = backtest_date - openPositions[ticker].entry_date
                    winning_trade_length = winning_trade_length + int(dif.days)

                cashEquity = cashEquity + (
                    openPositions[ticker].shares
                    * tableReference(ticker, tomorrow, "Open")
                )

                # Add dividends if it happens to be paid out on the same day
                yf_ticker = yfinance.Ticker(ticker)
                dividends_history = yf_ticker.dividends
                if backtest_date in dividends_history.index:
                    cashEquity += (
                        dividends_history[backtest_date] * openPositions[ticker].shares
                    )

                print("Sold on 50 day low:" + str(ticker))
                tradingLog[backtest_date].append(
                    {
                        "Date": backtest_date,
                        "Ticker": ticker,
                        "Shares": openPositions[ticker].shares,
                        "Action": "Sold on 50 day low",
                        "Percent Change": percent_profit,
                    }
                )
                openPositions[ticker] = 0

    shareEquity, cashEquity = calculateEquity(backtest_date, cashEquity)

    totalEquity = cashEquity + shareEquity
    strategyDates.append(backtest_date)
    strategyReturns.append(totalEquity)
    print("Equity: " + str(totalEquity))

    candidates = []
    cash_position_size = totalEquity * max_trade_percent

    # Calculate average number of simultaneous positions, I'm going to exclude times when I'm under SMA since I can't trade then
    unique_positions = 0
    for z in openPositions:
        if openPositions[z] == 0:
            continue
        else:
            unique_positions += 1
    unique_positions_graphX.append(backtest_date)
    unique_positions_graphY.append(unique_positions)

    # Average proportion of money invested relative to total equity
    percent_invested_graphX.append(backtest_date)
    stockProportion = shareEquity / totalEquity
    percent_invested_graphY.append(stockProportion)

    if cashEquity < cash_position_size:
        print("Buying power too low")
        if len(tradingLog[backtest_date]) == 0:
            tradingLog.pop(backtest_date)
        backtest_date = incrementDate(backtest_date, "forward")
        continue

    print("Analysis start: " + str(datetime.now()))

    for ticker in constituents[constituentsKeys[constituentsKeyIndex]][0:50]:
        highs = []

        # Check that the asset exists
        try:
            tableReference(ticker, backtest_date, "Close")
        except:
            continue

        # Check for 150 day highs, only consider candle body
        current_index_position = stocksData.index.get_loc(backtest_date)
        last_150_close = list(
            stocksData[("Close", ticker)][
                current_index_position - 149 : current_index_position + 1
            ]
        )
        last_150_open = list(
            stocksData[("Open", ticker)][
                current_index_position - 149 : current_index_position + 1
            ]
        )
        last_150_close.extend(last_150_open)
        maximum = max(last_150_close)

        if maximum == tableReference(ticker, backtest_date, "Close"):
            try:
                if openPositions[ticker].consecutive_entries < 3:
                    candidates.append(ticker)
            except:
                candidates.append(ticker)

    if len(candidates) == 0:
        print("No good trades today")
        print("Analysis end: " + str(datetime.now()))
        if len(tradingLog[backtest_date]) == 0:
            tradingLog.pop(backtest_date)
        backtest_date = incrementDate(backtest_date, "forward")
        continue

    # If there are candidates, select the one with the strongest past performance, and one check that its volatility is below a threshold.
    last_year = backtest_date - timedelta(days=360)
    while last_year not in marketCalendar:
        last_year = last_year + timedelta(days=1)

    highest_return = float("-inf")
    chosen_ticker = None

    for ticker in candidates:

        asset_performance = (
            tableReference(ticker, backtest_date, "Close")
            - tableReference(ticker, last_year, "Close")
        ) / tableReference(ticker, last_year, "Close")

        if asset_performance > highest_return:

            current_index_position = stocksData.index.get_loc(backtest_date)
            last_90_close = list(
                stocksData[("Close", ticker)][
                    current_index_position - 89 : current_index_position + 1
                ]
            )
            asset_movements = np.diff(np.array(last_90_close)) / np.array(
                last_90_close[:-1]
            )
            std_dev = statistics.pstdev(asset_movements)
            if std_dev > 0.05:
                continue

            highest_return = asset_performance
            chosen_ticker = ticker

    if chosen_ticker == None:
        print("Candidates too volatile")
        if len(tradingLog[backtest_date]) == 0:
            tradingLog.pop(backtest_date)
        backtest_date = incrementDate(backtest_date, "forward")
        continue

    print("Ticker chosen: " + str(chosen_ticker))
    shares = cash_position_size / tableReference(chosen_ticker, backtest_date, "Close")

    try:

        if openPositions[chosen_ticker] == 0:
            # New position on previously held ticker
            openPositions[chosen_ticker] = createPosition(
                shares,
                1,
                tableReference(chosen_ticker, tomorrow, "Open"),
                backtest_date,
            )
        else:
            # Adding on to existing position

            openPositions[chosen_ticker].consecutive_entries += 1
            openPositions[chosen_ticker].avg_price = (
                openPositions[chosen_ticker].avg_price
                * openPositions[chosen_ticker].shares
                + tableReference(chosen_ticker, tomorrow, "Open") * shares
            ) / (openPositions[chosen_ticker].shares + shares)

            openPositions[chosen_ticker].shares += shares
    except:
        # New position on not previously held ticker
        openPositions[chosen_ticker] = createPosition(
            shares,
            1,
            tableReference(chosen_ticker, tomorrow, "Open"),
            backtest_date,
        )
    tradingLog[backtest_date].append(
        {
            "Date": backtest_date,
            "Ticker bought": chosen_ticker,
            "Shares": shares,
            "Price": tableReference(chosen_ticker, tomorrow, "Open"),
            "Side": "Buy",
        }
    )
    cashEquity = cashEquity - (shares * tableReference(chosen_ticker, tomorrow, "Open"))

    backtest_date = incrementDate(backtest_date, "forward")

print("Annual Backtest Equity: " + str(annual_backtest_equity))
print("Annual SPY Equity: " + str(annual_spy_equity))

# Plot annual returns as a bargraph

backtest_annual_percentChange = np.diff(
    np.array(list(annual_backtest_equity.values()))
) / np.array(list(annual_backtest_equity.values())[:-1])


spy_annual_percentChange = np.diff(
    np.array(list(annual_spy_equity.values()))
) / np.array(list(annual_spy_equity.values())[:-1])

# Plot side by side vertical bar graph of annual strategy and SPY returns. Returns correspond to year of.
bargraph_xvalues = []
for n in list(annual_backtest_equity.keys())[1:]:
    bargraph_xvalues.append(n.year - 1)


fig = plt.figure()

subplot_list = [None, None]

subplot_list[0] = fig.add_subplot(2, 1, 1)
subplot_list[1] = fig.add_subplot(2, 1, 2)

# Add bargraphs and relevant titles

subplot_list[0].bar(bargraph_xvalues, backtest_annual_percentChange)
subplot_list[0].title.set_text("Backtest Returns")

subplot_list[1].bar(bargraph_xvalues, spy_annual_percentChange)
subplot_list[1].title.set_text("SPY Returns")
plt.show()


print("Winning Trades: " + str(winning_trades))
print("Losing Trades: " + str(losing_trades))
print("Average Gain: " + str(winning_trade_gains / winning_trades))
print("Average Loss: " + str(losing_trade_losses / losing_trades))
print("Average Win Length: " + str(winning_trade_length / winning_trades))
print("Average Loss Length: " + str(losing_trade_length / losing_trades))

# Graph strategy equity
plt.plot(strategyDates, strategyReturns, label="Strategy")

# SPY plot
starting_index = spy_data.index.get_loc(strategyDates[0])
plt.plot(
    spy_data.index[starting_index:],
    spy_performance_dividendAdj["Close"][starting_index:],
    label="SPY",
)

plt.title("Strategy Returns")
plt.legend()
plt.show()

# Graph unique positions
plt.plot(unique_positions_graphX, unique_positions_graphY)
plt.title("Unique assets")
plt.show()

# Graph percent invested
plt.plot(percent_invested_graphX, percent_invested_graphY)
plt.title("Percent invested")
plt.show()
