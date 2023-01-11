import yfinance
import finta
from matplotlib import pyplot as plt
import math
import numpy as np
import datetime


assetList = [
    "SPY",
    "GLD",
    "QQQ",
]  # Input desired assets here. The start date of the test will begin at the latest start date of the asset group.

weights = [
    0.4,
    0.3,
    0.3,
]  # Set corresponding portfolio allocation for each asset. Number of weights must match number of assets.

# Spread / rountrip fee in decimal form. Review slides on order book for a refresher on spreads.
# ex: Spread is .01 -> 1%: so both buy and sell order occurs at .5% markup, reducing total equity by that much.
spread = 0

startingIndex = 100


priceTables = []
dividendTables = []

currentPositions = []
currentShares = []
exitPrices = []
lastCrossovers = []
placeTrades = []
lookForSignals = []
lastEntryPrices = []
entryTriggerPrices = []
tradeDirections = []
stoppedOut = []

cashEquity = 1000
shareEquity = []


n = 0

for asset in assetList:

    priceTables.append(yfinance.download(asset))
    dateTable = priceTables[n]

    dateTable["ATR"] = finta.TA.ATR(dateTable, 5)
    dateTable["SMA"] = finta.TA.SMA(dateTable, 20)
    dateTable["LSMA"] = finta.TA.SMA(dateTable, 200)
    dateTable["Long"] = np.nan
    dateTable["Short"] = np.nan

    dividendTables.append(yfinance.Ticker(asset).dividends)
    currentPositions.append(0)
    currentShares.append(0)
    exitPrices.append(0)
    lastCrossovers.append("unknown")
    placeTrades.append(False)
    lookForSignals.append(False)
    lastEntryPrices.append(0)
    entryTriggerPrices.append(0)
    tradeDirections.append(None)
    shareEquity.append(0)
    stoppedOut.append(False)

    n += 1

currentEquity = cashEquity + sum(shareEquity)


# For plotting total returns
equityX = []
equityY = []
graphX = 0


# Long and short trade statistics
LongWin = 0
LongLoss = 0
NetLongLoss = 0
NetLongWin = 0
ShortWin = 0
ShortLoss = 0
NetShortWin = 0
NetShortLoss = 0

# Find latest start date in asset histories
startDate = datetime.datetime(1000, 1, 1)
for n in range(0, len(priceTables)):
    if priceTables[n].index[0] > startDate:
        startDate = priceTables[n].index[0]

# Cut all data tables to begin with this date
for n in range(0, len(priceTables)):
    position = priceTables[n].index.get_loc(startDate)
    priceTables[n] = priceTables[n][position:]

print(priceTables[0].index[0])

# Calculates equity whenever a position is open to construct a profit curve.
def calculateEquity(
    _cashEquity,
    _lastEntryPrice,  # Entry price of ongoing trade.
    _currentPosition,  # Current trade direction: 1 for long, -1 for short.
    _currentShares,  # Number of shares owned.
    _currentIndexPosition,  # Position of data table index, for referencing the current date and corresponding values
    _data,  # Data table
    _stoppedOut,  # Trade ended? T or F
    _exitPrice,  # If _stoppedOut is True, then an exit price will be specified
    _spread,  # Preset fee
):

    _currentIndex = _data.index[_currentIndexPosition]

    # If I am stopped out, use exit price for calculations. Otherwise, use the current close.
    # Notice that equity for short positions is calculated as double the intial - current.
    # ex. 100 entry price. current price is 95 -> for a short position that is 5 dollar profit defined as 100*2 - 95 = 105
    if _stoppedOut:
        if _currentPosition == -1:
            # _shareEquity = (
            #     _currentShares * (2 * _lastEntryPrice - _exitPrice) * (1 - _spread / 2)
            # )
            _shareEquity = _currentShares * (_exitPrice) * (1 - _spread / 2)
        else:
            _shareEquity = _currentShares * (_exitPrice) * (1 - _spread / 2)

        _cashEquity += _shareEquity
        _shareEquity = 0
    else:
        if _currentPosition == -1:
            # _shareEquity = _currentShares * (
            #     2 * _lastEntryPrice - _data["Close"][_currentIndex]
            # )
            _shareEquity = _currentShares * (_data["Close"][_currentIndex])
        else:
            _shareEquity = _currentShares * (_data["Close"][_currentIndex])

    return _cashEquity, _shareEquity


def findCrossover(
    _currentIndexPosition,
    _data,
    _previousCrossover,  # The index position of the previous crossover event
    _currentSignalStatus,  # Waiting for new entry signal? T or F.
):

    _currentIndex = _data.index[_currentIndexPosition]

    if _data["Close"][_currentIndex] > _data["SMA"][_currentIndex]:
        pricePosition = "above"
    else:
        pricePosition = "below"

    # While loop incrementing dates to find where price last crossed the moving average.
    # The "isnan" and try,except statements account for the start of the test where there is a possibility of reaching values that could not be calculated,
    # or reaching the start of the table before finding a crossover event.
    if pricePosition == "above":
        try:
            while (
                not math.isnan(_data["SMA"][_currentIndex])
                and _data["Close"][_currentIndex] > _data["SMA"][_currentIndex]
            ):
                _currentIndexPosition -= 1
                _currentIndex = _data.index[_currentIndexPosition]

            if math.isnan(_data["SMA"][_currentIndex]):
                _currentIndex = "unknown"
            else:
                _currentIndexPosition += 1
                _currentIndex = _data.index[_currentIndexPosition]
        except:
            _currentIndex = "unknown"

    else:
        try:
            while (
                not math.isnan(_data["SMA"][_currentIndex])
                and _data["Close"][_currentIndex] < _data["SMA"][_currentIndex]
            ):
                _currentIndexPosition -= 1
                _currentIndex = _data.index[_currentIndexPosition]

            if math.isnan(_data["SMA"][_currentIndex]):
                _currentIndex = "unknown"
            else:
                _currentIndexPosition += 1
                _currentIndex = _data.index[_currentIndexPosition]
        except:
            _currentIndex = "unknown"

    # If a new crossover event occured, look for new entry signal. Otherwise, the variable remains unchanged.
    if _currentIndex != _previousCrossover:
        _lookForSignal = True
    else:
        _lookForSignal = _currentSignalStatus

    return _currentIndex, _lookForSignal


def entrySignal(_lastCrossover, _currentIndexPosition, _data):

    _currentIndex = _data.index[_currentIndexPosition]
    lastCrossoverPosition = _data.index.get_loc(_lastCrossover)

    if _data["Close"][_currentIndex] > _data["SMA"][_currentIndex]:
        pricePosition = "above"
    else:
        pricePosition = "below"

    _tradeDirection = None
    signal = 0  # Number of highs or lows, above or below the moving average respectively. 2 is the target number for an entry.
    signalFound = False
    extremes = (
        []
    )  # List of highest high/ lowest low for the 2 signal candles. Used for calculating _entryPrice.
    _entryPrice = None
    _placeTrade = None

    # Variable for scrolling through historic dates to look for valid signals.
    # Begins at the crossover event and continues to the current date.
    signalIndexPosition = lastCrossoverPosition

    # Scroll from crossover event to current date. If two valid signals occur, exit.
    if pricePosition == "above":
        while signalIndexPosition <= _currentIndexPosition:

            signalIndex = _data.index[signalIndexPosition]
            if _data["Low"][signalIndex] > _data["SMA"][signalIndex]:
                signal += 1
                extremes.append(_data["High"][signalIndex])
            if signal == 2:
                _entryPrice = max(extremes) + 0.2 * _data["ATR"][signalIndex]
                signalFound = True
                break

            signalIndexPosition += 1

    else:
        while signalIndexPosition <= _currentIndexPosition:

            signalIndex = _data.index[signalIndexPosition]
            if _data["High"][signalIndex] < _data["SMA"][signalIndex]:
                signal += 1
                extremes.append(_data["Low"][signalIndex])
            if signal == 2:
                _entryPrice = min(extremes) - 0.2 * _data["ATR"][signalIndex]
                signalFound = True
                break

            signalIndexPosition += 1

    # If signal found, make sure that the entry was not missed. For example, the start of the script may start after a valid entry signal.
    # If signal was not found, return on next day to keep checking.
    if signalFound:
        if signalIndexPosition != _currentIndexPosition:
            _placeTrade = False
        else:
            _placeTrade = True
            _tradeDirection = pricePosition
        _lookForSignal = False
    else:
        _placeTrade = False
        _lookForSignal = True

    return (
        _entryPrice,
        _placeTrade,
        _lookForSignal,
        _tradeDirection,
    )


def exitSignal(_currentPosition, _currentIndexPosition, _data):
    _currentIndex = _data.index[_currentIndexPosition]
    _yesterdayIndex = _data.index[
        _currentIndexPosition - 1
    ]  # Because SMA and ATR get calculated at close, we need to use yesterday's existing values.
    _stoppedOut = False
    _exitPrice = None
    if _currentPosition == -1:
        if _data["High"][_currentIndex] > (
            _data["SMA"][_yesterdayIndex] + 0.2 * (_data["ATR"][_yesterdayIndex])
        ):
            _stoppedOut = True
            _exitPrice = _data["SMA"][_yesterdayIndex] + 0.2 * (
                _data["ATR"][_yesterdayIndex]
            )
    else:
        if _data["Low"][_currentIndex] < (
            _data["SMA"][_yesterdayIndex] - 0.2 * (_data["ATR"][_yesterdayIndex])
        ):
            _stoppedOut = True
            _exitPrice = _data["SMA"][_yesterdayIndex] - 0.2 * (
                _data["ATR"][_yesterdayIndex]
            )
    return _stoppedOut, _exitPrice


for n in range(startingIndex, len(priceTables[0].index)):
    activeTrade = False
    realDate = priceTables[0].index[
        n
    ]  # n is integer position, realDate is the date corresponding to that position in the data table.

    for a in range(0, len(priceTables)):

        if realDate in dividendTables[a].index:
            cashEquity += currentShares[a] * dividendTables[a][realDate]

        if currentPositions[a] != 0:

            # To construct a nice graph, I only count the days where there is an ongoing trade.
            if weights[a] != 0:
                activeTrade = True

            stoppedOut[a], exitPrices[a] = exitSignal(
                currentPositions[a], n, priceTables[a]
            )  # Apply stop loss

            # Reminder that our short posititions are now long, yet our original stop loss mechanics remain. It no longer makes sense to stop
            # a long trade when the price moves up, therefore I'll add a universal stop loss of 10%.
            if not stoppedOut[a]:
                if currentPositions[a] == -1:
                    if priceTables[a]["Close"][realDate] < 0.9 * lastEntryPrices[a]:
                        stoppedOut[a] = True
                        exitPrices[a] = priceTables[a]["Close"][realDate]
                else:
                    if priceTables[a]["Close"][realDate] < 0.9 * lastEntryPrices[a]:
                        stoppedOut[a] = True
                        exitPrices[a] = priceTables[a]["Close"][realDate]

            # Calculate current equity
            cashEquity, shareEquity[a] = calculateEquity(
                cashEquity,
                lastEntryPrices[a],
                currentPositions[a],
                currentShares[a],
                n,
                priceTables[a],
                stoppedOut[a],
                exitPrices[a],
                spread,
            )

            if stoppedOut[a]:

                if currentPositions[a] == 1:
                    if exitPrices[a] > entryTriggerPrices[a]:
                        LongWin += 1
                        NetLongWin += (
                            exitPrices[a] - entryTriggerPrices[a]
                        ) / entryTriggerPrices[a]
                    else:
                        LongLoss += 1
                        NetLongLoss += (
                            exitPrices[a] - entryTriggerPrices[a]
                        ) / entryTriggerPrices[a]
                else:
                    if exitPrices[a] < entryTriggerPrices[a]:
                        ShortWin += 1
                        NetShortWin -= (
                            exitPrices[a] - entryTriggerPrices[a]
                        ) / entryTriggerPrices[a]
                    else:
                        ShortLoss += 1
                        NetShortLoss -= (
                            exitPrices[a] - entryTriggerPrices[a]
                        ) / entryTriggerPrices[a]

                currentShares[a] = 0
                currentPositions[a] = 0

        if currentPositions[a] == 0:

            # Look for a new crossover.
            lastCrossovers[a], lookForSignals[a] = findCrossover(
                n, priceTables[a], lastCrossovers[a], lookForSignals[a]
            )

            if lastCrossovers[a] != "unknown":

                # Look for an entry signal.
                if lookForSignals[a]:
                    (
                        entryTriggerPrices[a],
                        placeTrades[a],
                        lookForSignals[a],
                        tradeDirections[a],
                    ) = entrySignal(lastCrossovers[a], n, priceTables[a])

                # If an entry signal was spotted, wait for price to hit the trigger.
                if placeTrades[a]:

                    if (
                        tradeDirections[a] == "above"
                        and priceTables[a]["LSMA"][realDate]
                        > priceTables[a]["LSMA"][priceTables[a].index[n - 1]]
                    ):
                        if priceTables[a]["High"][realDate] >= entryTriggerPrices[a]:
                            currentPositions[a] = 1
                            if currentEquity * weights[a] > cashEquity:
                                currentShares[a] = cashEquity / entryTriggerPrices[a]
                            else:
                                currentShares[a] = (
                                    currentEquity / entryTriggerPrices[a] * weights[a]
                                )
                            cashEquity -= currentShares[a] * entryTriggerPrices[a]
                            shareEquity[a] += (
                                currentShares[a] * entryTriggerPrices[a]
                            ) * (1 - spread / 2)
                            currentEquity = cashEquity + sum(shareEquity)
                            lastEntryPrices[a] = entryTriggerPrices[a]
                            placeTrades[a] = False

                    if (
                        tradeDirections[a] == "below"
                        and priceTables[a]["LSMA"][realDate]
                        > priceTables[a]["LSMA"][priceTables[a].index[n - 1]]
                    ):
                        if priceTables[a]["Low"][realDate] <= entryTriggerPrices[a]:

                            currentPositions[a] = -1
                            if currentEquity * weights[a] > cashEquity:
                                currentShares[a] = cashEquity / entryTriggerPrices[a]
                            else:
                                currentShares[a] = (
                                    currentEquity / entryTriggerPrices[a] * weights[a]
                                )

                            cashEquity -= currentShares[a] * entryTriggerPrices[a]
                            shareEquity[a] += (
                                currentShares[a] * entryTriggerPrices[a]
                            ) * (1 - spread / 2)
                            currentEquity = cashEquity + sum(shareEquity)
                            lastEntryPrices[a] = entryTriggerPrices[a]
                            placeTrades[a] = False

    currentEquity = cashEquity + sum(shareEquity)
    if activeTrade:
        equityX.append(graphX)
        equityY.append(currentEquity)
        graphX += 1


# Trade Statistics. All the try, excepts exist to avoid division by 0

try:
    print("Numbers of long wins: " + str(LongWin))
    print("Average long wins: " + str(NetLongWin / LongWin))
except:
    pass

try:
    print("Number of long losses: " + str(LongLoss))
    print("Average long losses: " + str(NetLongLoss / LongLoss))
except:
    pass

try:
    print("Numbers of short wins: " + str(ShortWin))
    print("Average short wins: " + str(NetShortWin / ShortWin))
except:
    pass

try:
    print("Numbers of short losses: " + str(ShortLoss))
    print("Average short losses: " + str(NetShortLoss / ShortLoss))
except:
    pass

# Plotting equity curve
plt.plot(equityX, equityY)
plt.show()
