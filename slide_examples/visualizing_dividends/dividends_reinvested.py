import yfinance
from matplotlib import pyplot as plt

# This short program is a very inneficient demonstration of how dividends compound over time.

SPY = yfinance.Ticker("SPY")
dividends = SPY.dividends
spy_prices = yfinance.download("SPY", period="Max")

cashEquity = spy_prices["Close"][spy_prices.index[0]]
shareEquity = 0
totalEquity = cashEquity + shareEquity
shares = 0

spy_total_returns_graphX = []
spy_total_returns_graphY = []

for date in spy_prices.index:

    # Check to see if dividends were paid out
    if date in dividends.index:
        cashEquity += dividends[date] * shares

    # Reinvest all excess cash into shares
    if cashEquity != 0:
        shares += cashEquity / spy_prices["Close"][date]
        cashEquity = 0

    shareEquity = shares * spy_prices["Close"][date]
    totalEquity = shareEquity + cashEquity

    spy_total_returns_graphX.append(date)
    spy_total_returns_graphY.append(totalEquity)

# Plot asset returns vs asset returns with dividends reinvested
plt.plot(spy_prices.index, spy_prices["Close"], label="SPY")
plt.plot(spy_total_returns_graphX, spy_total_returns_graphY, label="SPY Total Return")
plt.legend()
plt.show()
