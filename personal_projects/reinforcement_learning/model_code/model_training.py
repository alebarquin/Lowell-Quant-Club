# Gym stuff
from trading_env_class import UpdatedStockEnv

# Stable baselines
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import A2C

# Other libraries
import pandas as pd
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

# Set window size and training range. Start away from 0 to give room for indicator calculation
window = 30
lower_train_bound = 300
upper_train_bound = 666000

# Corresponding dates
print(minute_data.index[lower_train_bound])
print(minute_data.index[upper_train_bound])


# Create the training environment. Training frame bound is equal to data range present in training.
training_environment = UpdatedStockEnv(df=minute_data, window_size=window, frame_bound=(
    lower_train_bound, upper_train_bound), training_frame_bound=(lower_train_bound, upper_train_bound))

# God know what this does


def env_maker():
    return training_environment


training_environment = DummyVecEnv([env_maker])

# Baseline choice is A2C (Advantage Actor Critic) that uses the LSTM policy. Allows passing sequences of data rather than single data points, I think?
model = A2C("MlpLstmPolicy", training_environment, verbose=1)

# Train the model
TIMESTEPS = 500000

time_steps = 0
while time_steps < 4000000:

    # Learn function has crashed on occasion
    while True:
        try:
            model.learn(
                total_timesteps=TIMESTEPS, reset_num_timesteps=False,
            )
            break
        except:
            continue

    if time_steps % 500000 == 0:
        model.save(
            "saved_models/batch1/"
            + "step"
            + str(time_steps)
        )

    time_steps += 500000
