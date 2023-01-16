# Gym stuff
from trading_env_class import UpdatedStockEnv


# Stable baselines
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import A2C

# Other libraries
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from finta import TA


# Import data
minute_data = pd.read_csv(
    "spy_minute_data.csv",
)

minute_data["Date"] = pd.to_datetime(minute_data["Date"])
minute_data.set_index("Date", inplace=True)

# Define indicators
minute_data["RSI"] = TA.RSI(minute_data)
minute_data["SMA"] = TA.SMA(minute_data, 200)
minute_data["MACD"] = TA.MACD(minute_data)["MACD"]
minute_data["SIGNAL"] = TA.MACD(minute_data)["SIGNAL"]


def CalculateTimeFromOpen(data):
    hour = data.index.hour
    minute = data.index.minute

    time = hour * 60 + minute - 570
    return time


minute_data['Time'] = (minute_data.index.hour * 60 +
                       minute_data.index.minute) - 570

minute_data = minute_data.fillna(0)
print(minute_data)


# Set window size and training range. Start away from 0 to give room for indicator calculation.
window = 30
lower_train_bound = 300
upper_train_bound = 666000

# Corresponding Dates
print(minute_data.index[lower_train_bound])
print(minute_data.index[upper_train_bound])

# Set evaluation range. Do not overlap with trained data range.
lower_evaluation_bound = 666000
upper_evaluation_bound = 1373000

# Corresponding Dates
print(minute_data.index[lower_evaluation_bound])
print(minute_data.index[upper_evaluation_bound])

# Create the training environment. Training frame bound is equal to data range present in training.
evaluation_environment = UpdatedStockEnv(df=minute_data, window_size=window, frame_bound=(
    lower_evaluation_bound, upper_evaluation_bound), training_frame_bound=(lower_train_bound, upper_train_bound))


# God know what this does. "Vectorized environment"


def env_maker():
    return evaluation_environment


evaluation_environment = DummyVecEnv([env_maker])

modelCode = "saved_models/batch1/step3000000.zip"

model = A2C.load(
    modelCode,
    env=evaluation_environment
)

# The current environment is a vectorized environment object. It doesn't have the same methods as my environment class.
# As long as the model is loaded with this vectorized environment, the code below can be executed with my environment class.
# The performance will be the same, but I will also be able to call my custom functions to visualize data.
evaluation_environment = UpdatedStockEnv(df=minute_data, window_size=window, frame_bound=(
    lower_evaluation_bound, upper_evaluation_bound), training_frame_bound=(lower_train_bound, upper_train_bound))

# Reset and manually evaluate.
observation = evaluation_environment.reset()
_states = None

algorithm_returns = []
number_of_trades = 0
previous_action = 0

while True:

    observation = observation[np.newaxis, ...]
    action, _states = model.predict(
        observation, state=_states, deterministic=True)

    if previous_action != action:
        number_of_trades += 1
        previous_action = action

    observation, rewards, done, info = evaluation_environment.step(action)

    algorithm_returns.append(info["total_profit"])

    if done:
        print("info", info)
        break


print("Number of Trades: " + str(number_of_trades))


evaluation_environment.render_all()

plt.title("Algorithm Decisions")
plt.xlabel("Date")
plt.ylabel("Asset Price")
plt.show()


plt.plot(minute_data.index[lower_evaluation_bound:lower_evaluation_bound +
         len(algorithm_returns)], algorithm_returns)

plt.title("Algorithm Returns")
plt.xlabel("Date")
plt.ylabel("Equity")
plt.show()
