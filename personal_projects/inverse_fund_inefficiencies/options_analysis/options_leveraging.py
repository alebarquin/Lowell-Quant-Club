import requests
import numpy as np
from matplotlib import pyplot as plt
import yfinance as yf
import pandas as pd

tickers = ["SQQQ", "TQQQ"]

# When requesting data, try both including and excluding the last value. It depends on whether robinhood has published options data for the latest date.
# The correct version will produce a much clearer hedge out of the two.
price_data = {}
for ticker in tickers:
    price_data[ticker] = yf.download(ticker, period="400d")  # [:-1]

# Bearer token can be found by inspecting the robinhood page while logged in and navigating to the network tab. Some of the requests will carry the token in the header.
token = "YOUR_TOKEN"

# Request format may change in the future.
def getOptionData(_asset, _strike, exp_date, _type):

    option_url = (
        "https://api.robinhood.com/options/instruments/"
        + "?state=active"
        + "&type="
        + _type
        + "&chain_symbol="
        + _asset
        + "&strike_price="
        + _strike
    )

    request_header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": token,
    }

    # First find the id of the contract that matches my expiration date.
    response = requests.get(url=option_url, headers=request_header).json()
    option_information = pd.DataFrame(response["results"])

    rows = option_information.loc[option_information["expiration_date"] == exp_date]
    id = list(rows["id"])[0]

    # Then request the price data by id.
    contract_url = (
        "https://api.robinhood.com/marketdata/options/historicals/"
        + id
        + "/?interval=day"
    )
    price_history = requests.get(
        url=contract_url,
        headers=request_header,
    ).json()

    return price_history


def parseData(_hist, _startDate):
    price_data = pd.DataFrame(_hist["data_points"])

    price_data.set_index("begins_at", inplace=True)
    price_data.index = pd.to_datetime(price_data.index)

    price_data = price_data[price_data.index.get_loc(_startDate) :]
    price_data["close_price"] = price_data["close_price"].astype(float)
    return price_data


def calcAndPlot(_ticker, _strike, _exp, _start_analysis):
    call_data = getOptionData(_ticker, _strike, _exp, "call")
    call_data = parseData(call_data, _start_analysis)
    call_changes = np.diff(np.array(call_data["close_price"]))

    put_data = getOptionData(_ticker, _strike, _exp, "put")
    put_data = parseData(put_data, _start_analysis)
    put_changes = np.diff(np.array(put_data["close_price"]))

    ticker_price_changes = np.diff(
        np.array(price_data[_ticker]["Close"][-(len(put_changes) + 1) :])
    )

    # Plot synthetic long position on top of long stock position
    plt.plot(
        put_data.index[1:],
        np.cumsum(call_changes - put_changes),
        label=_ticker + " Options",
    )
    plt.plot(
        put_data.index[1:], np.cumsum(ticker_price_changes), label=_ticker + " Shares"
    )
    plt.plot(
        put_data.index[1:],
        np.cumsum(ticker_price_changes - (call_changes - put_changes)),
        label=_ticker + " - Options",
    )
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Dollar Change")
    plt.show()

    graph_x_axis = put_data.index
    return call_changes, put_changes, ticker_price_changes, graph_x_axis


# Compare a portfolio composed of asset 1 and asset 2 options.
# Specify the contract detials in the function arguments below: ticker, strike, exp, start of analysis.
# Data is only available for active contracts.

# Get first asset data
(
    first_asset_call_changes,
    first_asset_put_changes,
    first_asset_price_changes,
    graph_x_axis,
) = calcAndPlot(tickers[0], "45", "2023-01-20", "2022-07-21")

# Get second asset data
(
    second_asset_call_changes,
    second_asset_put_changes,
    second_asset_price_changes,
    graph_x_axis,
) = calcAndPlot(tickers[1], "32", "2023-01-20", "2022-07-21")

# Calculate the multiples of asset 1 and asset 2 to artificially hedge the two assets.


second_asset_multiple = list(
    price_data[tickers[0]]["Close"] / price_data[tickers[1]]["Close"]
)
adjusted_second_asset_price_changes = np.multiply(
    second_asset_price_changes,
    second_asset_multiple[-(len(second_asset_price_changes) + 1) : -1],
)

# The graphs below are my best attempt to analyze the option prices. Don't take the returns at face value, rather pay attention to the trend. Fees are not included.


# The dollar returns graphed below will represent the theoretical returns of a single share in asset 1 and x number of shares in asset 2, whose value
# equals the share value of asset 1, rebalanced daily.

plt.plot(
    graph_x_axis[1:],
    np.cumsum(-1 * (first_asset_price_changes + adjusted_second_asset_price_changes)),
)
plt.title("Short Stock in " + tickers[0] + " and " + tickers[1])
plt.xlabel("Date")
plt.ylabel("Dollar Change")
plt.show()

adjusted_second_asset_option_changes = np.multiply(
    second_asset_call_changes - second_asset_put_changes,
    second_asset_multiple[-(len(second_asset_price_changes) + 1) : -1],
)

# The dollar returns graphed below will represent the theoretical returns of a single synthetic long/short position in asset 1 and x number
# of synthetic long/short positions in asset 2, whose value equals the share value controlled by asset 1, rebalanced daily. This assumes
# fractional contracts, but in reality would require shares for hedging.

plt.plot(
    graph_x_axis[1:],
    np.cumsum(
        -1
        * (
            adjusted_second_asset_option_changes
            + first_asset_call_changes
            - first_asset_put_changes
        )
    ),
)
plt.title("Synthetic Short in " + tickers[0] + " and " + tickers[1])
plt.xlabel("Date")
plt.ylabel("Dollar Change (/100)")
plt.show()
