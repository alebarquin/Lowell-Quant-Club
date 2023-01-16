While experimenting with both overnight returns and the hedging algorithms, I noticed that long and inverse funds fail to hedge one another. I am not referring to the fact that they diverge over time because they track single day returns, but rather that they diverge even on a single day time range. Above is a script that demonstrates this, but make sure look through all the code to make necessary changes everywhere. 
</br>
</br>
A few important observations/notes: 
</br>
</br>
These funds track only single day returns, therefore a theoretical perfect hedge between a long and short fund requires daily rebalancing. 
</br>
</br>
The divergence that occurs expands and contracts with interest rates, where a long position in both a long and short fund generates profit at roughly the risk-free rate, and incures losses when rates reach lower levels. The interest rates also affect the stability of the returns. 
</br>
</br>
The higher the leverage of the funds, the less affected they are by rising rates. Instead they show consistent decline, only occasionally leveling out. 
</br>
</br>
The consistent smooth returns can be broken down into chaotic overnight and market open returns, which balance very nicely.
</br>
</br>
Because these stable returns were recreated with stocks, the immediate question was whether they can be leveraged with instruments like options. The test code is provided above. I observed that synthetic long positions for non-leveraged fund pairs did not generate profits or losses (SPY+SH). On the other hand synthetic short positions seemed to generate profits for leveraged fund pairs (SQQQ+TQQQ), although not nearly as steadily as a position in stocks. 

</br>
</br>

Below are examples of the portfolio returns previously discussed and an illustration of the gradual divergence between two funds.  
![image](https://user-images.githubusercontent.com/102199762/212520028-e350120c-a70b-4bcd-9af8-950d48a07b92.png)

</br>
</br>

![image](https://user-images.githubusercontent.com/102199762/212520051-acee4877-23ce-4268-baea-ec075b63d234.png)

</br>
</br>

![image](https://user-images.githubusercontent.com/102199762/212520076-27111172-d517-4a6b-a919-b39b44e26667.png)

</br>
</br>

Further Questions:
</br>
</br>
Why does this occur? 
</br>
</br>
Do short borrowing costs erode any opportunity for profits when rates are low? Why weren't they reflected in the options market?
</br>
</br>
Why do only some options price in these divergences?
</br>
</br>
Why do all options systematically deviate from the price movement given by put-call parity on a given day?
</br>
</br>
Is this an effective strategy in the options market? It seems like the profits are large enough to make it possible even after the costs associated with frequent transactions. 
