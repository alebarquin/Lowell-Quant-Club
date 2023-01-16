I'll start off by saying that trying to systematically training and validate my models has been a complete disaster for me. The difference in performance is incredibly difficult to attribute to a single change, and in all honesty I have made so many mistakes along the way that starting from the complete beginning seems like the only option. Keep in mind that as of this moment, my understanding of these algorithms does not extend beyond the concept of gradient descent taught in a third semester calculus course. My statistics and linear algebra is mediocre. 
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
My data also had random gaps, with about 5% missing. Although I eventually realized this and began to pad it with the last available price, all of my models were trained on what I had before. I don't know what effect this has on the result or whether padding with a repeated value is a good solution. I may consider filling gaps with values that grow at a constant rate towards the next available price. 
</br>
</br>
There was a lot of confusion around the best way to calculate the reward. Should it occur at every step? At the end of each trade? What action would the algorithm associate the reward with? At the time I had no idea about overnight trends and chose to forcefully end all trades before market close, hoping that I would be filtering out the chaotic jumps occured at that time. However, I had no clue how to deal with the fact that in the morning, indicators derived their value from prices before the overnight gap, causing a sort of lag. 
</br>
</br>
I eventually settled with rewarding the algorithm only at the end of a trade, when consecutive signals changed. The reward value was equal to the percentage return of the trade. All other actions received a neutral reward of 0. For whatever reason, the performance of an algorithm with a reward at every step (equal to the single minute percent change) was just inverse to the one that rewarded at the end of the trade (I'm assuming this was a mistake on my end but I don't know what caused it). I also tried to deduct a flat spread at every non-neutral reward to encourage less frequent trades, but the algorithm could not adapt and failed to generate a positive reward.
</br>
</br>
When it came to evaluation, the trading frequency of the model was unreasonably high and accrued large fees. On the other hand, measuring the opportunity cost of using limit orders at the mid-price for a liquid asset like SPY always seemed out of reach, although I'm hopeful that it would have improved performance over market orders.
</br>
</br>
When it came to optimizing the performance of the model, I tried techniques to filter the signals and reduce the number of trades and spent a lot of time systematically analyzing the trades themselves. By looking at the model's returns relative to trade length, I realized that it had a tendency to capture profits fast, and let losers drag, yet on average it did so very profitably. This resulted in nearly half of all losses occuring at the last trades of the day which was being forefully closed. No matter how I tried to sidestep this trend, the model always preserved its average like some sort of self balancing equation. 
</br>
</br>
I did, with high confidence, find that morning trades outperformed all other trades throughout the day, and where the only profitable choice after fees (possibly because of the overnight/morning correlation shenanigans). After building a few algorithms that only traded morning signals, I also stratified the trades by weekday, and once again used some shady statistics to isolate only the historically best performing days.  
</br>
</br>
At the end of the day I really have no idea whether anything I built is in any way practical, but I have at least shown that there is a method to the madness of intraday price movements. 


