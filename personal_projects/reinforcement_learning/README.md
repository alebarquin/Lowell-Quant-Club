I'll start off by saying that trying to systematically train and validate my models has been a complete disaster. The difference in performance is incredibly difficult to attribute to a single change, and in all honesty I have made so many mistakes along the way that starting from the complete beginning seems like the only option. Keep in mind that as of this moment, my understanding of these algorithms does not go far beyond the concept of gradient descent taught in a third semester calculus course. My understanding of statistics and linear algebra is mediocre. 
</br>
</br>
I didn't have much interest in analyzing large timeframes since I was relatively confident they were driven more by macro news than some voodoo patterns, and I was curious whether there was any point in trying to analyze intraday price. 
</br>
</br>
I began by developing models for forex because low increment data was far more accessible. I have little to say about them except that I highly doubt anything I analyzed was accurate, but I hope to try again some time. 
</br>
</br>
Eventually I got my hands onto minute data for SPY. I played around with reward formulas, the window length for LSTM algorithms, the type of data to use, and how to represent it. 
</br>
</br>
Again, I have no clue how much of it was effective, but I generally used data that could be represented as a percentage and normalized it to a 0 and 1 range, using the bounds that were present during my training phase. I settled on an arbitrary window length of 30 and chose to pass a few oscilating indicators, the distance between a moving average and the real price, and the time. I even tried to pass the signal outputs of other models as inputs into the new model, but that failed miserably if I recall correctly.   
</br>
</br>
My data also had random gaps, with about 5% missing. I eventually realized this and began to pad it with the last available price, but that came after training all of my models. I don't know what effect this will have on the result or whether padding with a repeated value is a good solution. I may consider filling gaps with values that grow at a constant rate towards the next available price. 
</br>
</br>
There was a lot of confusion around the reward function. Should it occur at every step? At the end of each trade? What action would the algorithm associate the reward with? At the time I had no idea about overnight trends and chose to forcefully end all trades before market close, hoping that I would filter out the chaotic overnight gaps. However, I still have no clue how to deal with the fact that in the morning, indicators derive their value from prices before the overnight gap, causing a sort of lag. 
</br>
</br>
I eventually settled with rewarding the algorithm only at the end of a trade, when the long/short position reversed. The reward was equal to the percentage return of the trade, while all other actions received a neutral reward of 0. For whatever reason, the performance of an algorithm with a reward at every step (equal to the single minute percent change) was just inverse to the one that rewarded at the end of the trade (I'm assuming this was a mistake on my end but I don't know what caused it). I also tried to deduct a fee/spread at every non-neutral reward to encourage less frequent trades, but the algorithm could not adapt and failed to generate a positive reward.
</br>
</br>
When it came to evaluation, the trading frequency of the model was unreasonably high and accrued large fees. I wanted to measure the opportunity cost of using limit orders at the mid-price but that information is still out of my reach, although I'm hopeful that it would have improved performance over market orders.
</br>
</br>
When it came to optimizing the performance of the model, I tried techniques to filter the signals and reduce the number of trades. I also spent a lot of time systematically analyzing the trades themselves. By looking at the model's returns relative to trade length, I realized that it had a tendency to capture profits fast, and let losers drag, yet on average it did so very profitably. This resulted in nearly half of all losses being associated with the last trade of the day, which was being forefully closed. No matter how I tried to sidestep this trend, the model always preserved its average like some sort of self balancing equation. 
</br>
</br>
I did, with high confidence, find that morning trades outperformed all other trades throughout the day, and where the only profitable choice after fees (possibly because of the overnight/morning correlation shenanigans. Although I'm curious how the model identified that it was "the morning", since it did this even before including time data). After building a few algorithms that only traded morning signals, I also stratified the trades by weekday, and once again used some shady statistics to isolate only the best performing days.  
</br>
</br>
I really have no idea whether anything I built is in any way practical, but I have at least shown that there is a method to the madness of intraday price movements. I'm sure these models would also be good at identifying trends in more predictable scenarios, like the price decline for top stock gainers. 


