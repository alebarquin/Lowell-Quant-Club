import yfinance
import datetime
import pandas as pd
import numpy as np
import sympy
from sympy import pprint
from matplotlib import pyplot as plt

# Downloading data
tickers = ["SPY", "QQQ", "TLT", "GLD"]

df = yfinance.download(
    tickers,
    start=datetime.datetime(2000, 1, 1),
    end=datetime.datetime(2022, 8, 1),
    group_by="ticker",
)

# Add dividends
for n in tickers:
    asset = yfinance.Ticker(n)  # Create a ticker object
    divDf = asset.dividends  # Download dividend data for the ticker object
    divDf = divDf.reindex_like(df).fillna(
        0
    )  # Give the dividend table the same index as the main table and fill non existing values with 0
    df[(n, "Close")] = (
        divDf + df[(n, "Close")]
    )  # Now that indeces match, we can add the two columns

# Create a new data frame and populate it with only the close columns
newdf = pd.DataFrame()

for n in tickers:
    newdf[n] = df[(n, "Close")]

# Convert dollar changes to percent changes and drop the first row
newdf = newdf.pct_change(1)
newdf.drop(newdf.index[0], inplace=True)

# Since some assets start earlier than others, we need to start at the point when all assets have data
firstRealDate = []
for n in list(newdf):
    firstRealDate.append(newdf[n].first_valid_index())

newdf = newdf.truncate(before=max(firstRealDate))
print(newdf)

# ---------------------- #

# The sympy math starts here


assetNames = ["SPY", "QQQ", "TLT", "GLD"]
assetsLength = len(assetNames)

covM = newdf[assetNames].cov()  # Covariance matrix
pprint("Covariance Matrix: ")
pprint(covM)
pprint("---------------")

# Create list of sympy symbols for each weight and our two constraints
symbols = []
for n in range(0, assetsLength):
    symbols.append(sympy.Symbol("w" + str(n), real=True))

symbols.append(sympy.Symbol("Lm1", real=True))
symbols.append(sympy.Symbol("Lm2", real=True))

# Create our weights matrix
Weights = []
for n in range(0, assetsLength):
    Weights.append(symbols[n])

# Reshape the matrix to be vertical. -1 indicates that the rows should be whatever value fits as long as the columns is 1.
Weights = np.array(Weights).reshape(-1, 1)
WeightsT = np.transpose(Weights)


# Portfolio variance function, main function to minimize
f = WeightsT @ covM @ Weights
f = f[0][
    0
]  # f is nested in multiple lists, so we have to index it to get the actual expression.
pprint("Variance function: ")
pprint(f)
pprint("---------------")

# Constraint 1: Sum of the absolute weights must equal 1. Review matrix multiplication to understand the function.
onesVector = np.ones((1, Weights.shape[0]))
g = onesVector @ abs(Weights)
pprint("Constraint 1 Must Equal 1: ")
pprint(g)
pprint("---------------")

# Calculate an array of corresponding average daily returns based off of the columns of the data table.
ExpectedAssetReturns = np.array(newdf.mean(axis=0)[assetNames]).reshape(-1, 1)
pprint("Expected Returns: " + str(ExpectedAssetReturns))
pprint("---------------")
ExpectedPortfolioReturns = newdf.mean(axis=0)["SPY"] * 1  # Set returns target
pprint("Target Return: " + str(ExpectedPortfolioReturns))
pprint("---------------")

# Constraint 2: The sum of each weight multiplied with its corresponding return must equal our target return
h = WeightsT @ ExpectedAssetReturns
pprint("Constraint 2 Equals Target Return: ")
pprint(h)
pprint("---------------")

Lm1 = symbols[
    assetsLength
]  # Assets length is the number of assets we have. For a 0 indexed list, that means the first lagrange multiplier is located at
# that position: ex. 2 assets: [w1, w2, Lm1, Lm2], where w1 is at pos. 0 etc. and Lm1 starts at position 2.
Lm2 = symbols[assetsLength + 1]


# Defining and finding the gradient of the lagrangian with both constraints active
lagrangian = f - Lm1 * (g - 1) - Lm2 * (h - ExpectedPortfolioReturns)
lagrangian = lagrangian[0][0]
pprint("lagrangian: ")
pprint(lagrangian)
pprint("---------------")


sysEquations = []

# Calculate partial derivatives of all weights and then lagrange multipliers
for w in symbols[:-2]:

    der = sympy.diff(lagrangian, w)
    # The derivative of abs(w) is w / abs(w)... which is really just 1 or -1 depending on the sign of w. Sympy expresses this with
    # the sign(w) function, but that won't work with the equation solver, so we substitute the original w / abs(w)
    derOfAbs = w / abs(w)
    der = der.replace(sympy.sign(w), derOfAbs)
    sysEquations.append(der)

sysEquations.append(sympy.diff(lagrangian, Lm1))
sysEquations.append(sympy.diff(lagrangian, Lm2))

pprint("System of Equations: ")
pprint(sysEquations)
pprint("---------------")

# Initial guess for all weights and lagrange multipliers
guessV = []
for n in range(0, assetsLength):
    guessV.append(1 / assetsLength)
guessV.append(0.5)
guessV.append(0.5)


solution = sympy.nsolve(sysEquations, symbols, guessV, verify=False)
print(solution)


solution = np.array(solution).reshape(-1, 1)[0:assetsLength]
solution = [float(x[0]) for x in solution]

backtest = pd.concat([newdf, newdf[assetNames] @ solution], axis=1)
backtest.rename({0: "Optimal"}, axis=1, inplace=True)

backtest.fillna(0, inplace=True)
print(backtest)


startDate = (
    backtest["Optimal"].ne(0).idxmax()
)  # The starting point of the optimal equity
startLoc = backtest.index.get_loc(startDate)

assetNames.append("Optimal")
plt.plot(
    backtest.index[startLoc:],
    (backtest[["Optimal", "SPY"]][startDate:] + 1).cumprod() - 1,
)
plt.legend(["Optimal", "SPY"], loc="upper left")
plt.show()
