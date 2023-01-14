This folder contains an example of how to solve a constrained optimization problem to minimize portfolio volatility. It accepts a list of tickers and finds optimal weights whose absolute value sums to 1 and that achieve a target portfolio return.
</br>
</br>
A second script is used to find a portfolio that minimizes the distance to a target returns curve. This is used to find a unique combination of assets that can hedge a second target asset.
</br>
</br>
Further Questions:
</br>
</br>
What is the relationship in price between an ETF and its constituents when dividends are paid out (since they happen at different times).
</br>
</br>
Can we successfully hedge an asset to capture only dividend payments?
</br>
</br>
Are returns that occur post optimization completely random, or is there still some level of correlation that makes these algorithms useful?
</br>
</br>
Can we reverse engineer "mystery" portfolios with some measurable level of confidence by searching for custom assets that match the return of the portfolio over some period of time. 
