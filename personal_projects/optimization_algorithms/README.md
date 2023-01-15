This folder contains an example of how to solve a constrained optimization problem to minimize portfolio volatility. It accepts a list of tickers and finds optimal weights whose absolute value sums to 1 and that achieve a target portfolio return.
</br>
</br>
Volatility minimization for a 4 asset portfolio: ["SPY", "QQQ", "TLT", "GLD"] -> [7.84040749440165e-7], [0.424004109981917], [0.404640223613066], [0.266118205251890].
![image](https://user-images.githubusercontent.com/102199762/212568761-cfc64cd0-1876-4e41-b383-2d7058ad06f0.png)
</br>
</br>
A second script is used to find a portfolio that minimizes the distance to a target returns curve. This is used to find a unique combination of assets that can hedge a second target asset.
</br>
</br>
Custom portfolio optimized to mimic the movements of SPY.
![image](https://user-images.githubusercontent.com/102199762/212568960-1b6ea9d8-c439-45ad-9b5b-6e0b06610600.png)
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
