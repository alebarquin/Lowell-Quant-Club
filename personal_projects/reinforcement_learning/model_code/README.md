Once again, my understanding of some of the functions are rather limited. 
</br>
</br>
For one, I'm not sure what exactly the learn function is doing. Is learn call with an input of 50,000 timesteps twice equal to a single learn call with 100,000 timesteps? 
I believe the reset_num_timesteps = False ensures that the model's state is preserved, but does that mean that a new call will continue analyzing the data from where it left off, or will the model start from the first observation and loop over the same 50,000 observations? 
