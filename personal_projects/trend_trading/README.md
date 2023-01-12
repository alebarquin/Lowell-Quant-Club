One of the first algorithms I ever backtested. The system is a simple version of trend trading, based on the principles of Jesse Livermore, a successful day trader who operated pre 1940s, and who was interviewed in the book “Reminiscences of a Stock Operator.”
	</br>
  </br>
  While it had a successful history, it’s not likely to work in the more sophisticated markets that exist today. 
	</br>
  </br>
  The algorithm runs once a day at close, analyzing the top 50 constituents of the S&P index. It looks for breakouts above the 150 day high as signals to buy, and breakouts below the 50 day low as  signals to close existing positions. 
	</br>
  </br>
  Beyond these simple rules, I added code to allow reentries into a single asset up to a maximum of 3 total positions, each one being valued at 10% of the total portfolio. Multiple promising candidates were resolved by selecting the one with the strongest annual performance leading up, and by checking that the 90 day percentage volatility did not exceed a certain threshold. The moving average of the S&P acted as a filter that prevented selling of positions due to poor performance that coincided with the overall market. This resulted in very strong portfolio performance after the market began to recover. 
	</br>
  </br>
  While the backtest shows very strong performance, the low trade sample size and the numerous variables that I tweaked makes this almost certainly overfit. However, in combination with additional fundamental measures, the idea of creating a portfolio of already strong stocks and filtering out broad market trends would seem to follow all general investing principles. 