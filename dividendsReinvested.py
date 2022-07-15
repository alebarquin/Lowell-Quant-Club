import yfinance
from matplotlib import pyplot as plt


SPY = yfinance.Ticker("SPY")
dividends = SPY.dividends
prices = yfinance.download("SPY", period="Max")

cashEquity = prices["Close"][prices.index[0]]
shareEquity = 0
totalEquity = cashEquity + shareEquity
shares = 0

returnsX = []
returnsY = []

for n in prices.index:

    # Check to see if dividends were paid out
    if n in dividends.index:
        cashEquity += dividends[n] * shares

    # Reinvest all excess cash into shares
    if cashEquity != 0:
        shares += cashEquity / prices["Close"][n]
        cashEquity = 0

    shareEquity = shares * prices["Close"][n]
    totalEquity = shareEquity + cashEquity

    returnsX.append(n)
    returnsY.append(totalEquity)

# Plot asset returns vs asset returns with dividends reinvested
plt.plot(prices.index, prices["Close"])
plt.plot(returnsX, returnsY)
plt.show()
