I'll start off by saying that trying to approach model training and validation systematically has been a complete disaster for me. The difference in performance is incredibly difficult to attribute to a single change, and in all honesty I have made so many mistakes along the way that starting from the complete beginning seems like the only option. Keep in mind that as of this moment, my understanding of these algorithms does not extend beyond the concept of gradient descent taught in a third semester calculus course. My statistics and linear algebra is mediocre. 
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
There was a lot of confusion around the best way to calculate the reward. Should it occur at every step? At the end of each trade? What action would the algorithm associate the reward with? At the time I had no idea about overnight trends and chose to forcefully end all trades before market close, hoping that I would be filtering out the chaotic jumps occured at that time. However, I had no clue how to deal with the fact that in the morning, indicators derived their value from prices before the overnight gap, causing a sort of lag. 
</br>
</br>
I eventually settled with rewarding the algorithm only at the end of a trade, when consecutive signals changed. The reward value was equal to the percentage return of the trade. All other actions received a neutral reward of 0. For whatever reason, the performance of an algorithm with a reward at every step (equal to the single minute percent change) was just inverse to the one that rewarded at the end of the trade (I'm assuming this was a mistake on my end but I don't know how). I also tried to deduct a flat spread at every non-neutral reward to encourage less frequent trades, but the algorithm could not adapt and failed to generate a positive reward.
</br>
</br>



and the moving average a self-balancing mathematical equation. 
