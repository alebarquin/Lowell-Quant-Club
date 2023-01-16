Above is the code used to train and evaluate the models. This was all done in Python 3.7 with older dependencies whose versions I've included. 
</br>
</br>
The model environment class inherits an open source class available in the gym_anytrading package. The training and validation is done using OpenAI Gym and a fork called StableBaselines that contains already tuned training algorithms. 
</br>
</br>
About the trading_env_class:
</br>
I hard coded the model inputs into the class. They can be changed by altering the class definition. I also added a function that finds the upper and lower bounds of the data and normalizes it based on that range. This range is calculated based on the subset of the data that the model was trained on, so the trained_frame_boundaries argument should carry the same start and finish that the model was trained on. 
</br>
</br>
The minute data provided above is only a small subset of what the model was trained on. It is padded with a repeating value where data is missing. 
</br>
</br>
Once again, my understanding of some of the functions are rather limited, so the code is likely inneficient, and the comments are not very enlightening. 
</br>
</br>
Below is the performance of model number 3 million. 
![image](https://user-images.githubusercontent.com/102199762/212767715-de0daf0b-7763-4cc1-bf71-84f69aaa1d4b.png)

