import yfinance
import finta
from matplotlib import pyplot as plt
import math


data = yfinance.download("SPY", period="30y", interval="1d")
data["ATR"] = finta.TA.ATR(data, 5)
data["SMA"] = finta.TA.SMA(data, 20)
print(data)


# 0 is neutral, -1 is short, 1 is long
currentPosition = 0

# Specifies start date for simulation. ex: 100 -> starts from 100th day in data.
startingIndex = 100

# The location of the last known crossover event (where the price swapped position relative to moving average ex. from above to below)
lastCrossover = "unknown"


# lookForSignal specifies if I should be looking for an entry signal.
# For example, if a crossover just occured, I am looking for the two highs / lows pattern, variable is True.
# If a signal was already spotted, and I'm awaiting price to trigger my entry, variable is False.
lookForSignal = False

placeEntry = False

lastEntryPrice = 0  # Entry price
entryTriggerPrice = 0  # Entry trigger price

tradeDirection = None  # Long or short, specified as above or below respectively (above or below in referance to the moving average.)
currentShares = 0
cashEquity = data["Close"][
    startingIndex
]  # Starting equity will be set to the price of the benchmark for easy comparison of returns
shareEquity = 0

# Our equity will be broken down into cash and shares.
currentEquity = cashEquity + shareEquity


# For plotting total returns
equityX = []
equityY = []

# Spread / rountrip fee in decimal form. Review slides on order book for a refresher on spreads.
# ex: Spread is .01 -> 1%: so both buy and sell order occurs at .5% markup, reducing total equity by that much.
spread = 0

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
            _shareEquity = (
                _currentShares * (2 * _lastEntryPrice - _exitPrice) * (1 - _spread / 2)
            )
            _currentEquity = _cashEquity + _shareEquity
        else:
            _shareEquity = _currentShares * (_exitPrice) * (1 - _spread / 2)
            _currentEquity = _cashEquity + _shareEquity

        # If stopped out, all share equity is converted to cash:
        _cashEquity = _currentEquity
        _shareEquity = 0
    else:
        if _currentPosition == -1:
            _shareEquity = _currentShares * (
                2 * _lastEntryPrice - _data["Close"][_currentIndex]
            )
            _currentEquity = _cashEquity + _shareEquity
        else:
            _shareEquity = _currentShares * (_data["Close"][_currentIndex])
            _currentEquity = _cashEquity + _shareEquity

    return _currentEquity, _cashEquity, _shareEquity


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


for n in range(startingIndex, len(data.index)):

    realDate = data.index[
        n
    ]  # n is integer position, realDate is the date corresponding to that position in the data table.

    if currentPosition != 0:

        stoppedOut, exitPrice = exitSignal(currentPosition, n, data)  # Apply stop loss

        # Calculate current equity
        currentEquity, cashEquity, shareEquity = calculateEquity(
            cashEquity,
            lastEntryPrice,
            currentPosition,
            currentShares,
            n,
            data,
            stoppedOut,
            exitPrice,
            spread,
        )

        equityX.append(realDate)
        equityY.append(currentEquity)

        if stoppedOut:
            currentShares = 0
            currentPosition = 0

    if currentPosition == 0:

        # Look for a new crossover.
        lastCrossover, lookForSignal = findCrossover(
            n, data, lastCrossover, lookForSignal
        )

        if lastCrossover != "unknown":

            # Look for an entry signal.
            if lookForSignal:
                (
                    entryTriggerPrice,
                    placeTrade,
                    lookForSignal,
                    tradeDirection,
                ) = entrySignal(lastCrossover, n, data)

            # If an entry signal was spotted, wait for price to hit the trigger.
            if placeTrade:

                if tradeDirection == "above":
                    if data["High"][realDate] >= entryTriggerPrice:
                        currentPosition = 1
                        currentShares = (currentEquity / entryTriggerPrice) * (
                            1 - spread / 2
                        )
                        cashEquity -= currentShares * entryTriggerPrice
                        shareEquity += (currentShares * entryTriggerPrice) * (1 - spread / 2) # the funds allocated to shares lose a percent to transaction fees.
                        currentEquity = cashEquity + shareEquity
                        lastEntryPrice = entryTriggerPrice
                        placeTrade = False

                elif tradeDirection == "below":
                    if data["Low"][realDate] <= entryTriggerPrice:
                        currentPosition = -1
                        currentShares = (
                            currentEquity / entryTriggerPrice 
                        )
                        cashEquity -= currentShares * entryTriggerPrice
                        shareEquity += (currentShares * entryTriggerPrice) * (1 - spread / 2)
                        currentEquity = cashEquity + shareEquity
                        lastEntryPrice = entryTriggerPrice
                        placeTrade = False

# Plotting equity curve
plt.plot(equityX, equityY)
plt.show()
