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
The minute data provided above is only a small subset of what the model was trained on. It is padded with the same value where data is missing. 
</br>
</br>
Once again, my understanding of some of the functions are rather limited. 
</br>
</br>
For one, I'm not sure what exactly the learn function is doing. Is learn call with an input of 50,000 timesteps twice equal to a single learn call with 100,000 timesteps? 
I believe the reset_num_timesteps = False ensures that the model's state is preserved, but does that mean that a new call will continue analyzing the data from where it left off, or will the model start from the first observation and loop over the same 50,000 observations? 
