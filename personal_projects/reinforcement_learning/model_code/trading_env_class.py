from gym_anytrading.envs import TradingEnv, Actions, Positions
from gym import spaces
import numpy as np
from matplotlib import pyplot as plt

# Seperating the changes made to the parent "Trading Env" class and the child "StockEnv" class


class UpdatedTradingEnv(TradingEnv):

    def __init__(self, df, window_size):
        super().__init__(df, window_size)
        # Update the observation space
        self.observation_space = spaces.Box(
            low=-1, high=1, shape=self.shape, dtype=np.float32
        )

    def step(self, action):
        self._done = False

        # Tick now gets updated after calculations

        step_reward = self._calculate_reward(action)
        self._total_reward += step_reward

        self._update_profit(action)

        trade = False
        if (action == Actions.Buy.value and self._position == Positions.Short) or (
            action == Actions.Sell.value and self._position == Positions.Long
        ):
            trade = True

        if trade:
            self._position = self._position.opposite()
            self._last_trade_tick = self._current_tick

        self._position_history.append(self._position)

        info = dict(
            total_reward=self._total_reward,
            total_profit=self._total_profit,
            position=self._position.value,
        )

        self._update_history(info)

        # Update tick
        self._current_tick += 1

        if self._current_tick == self._end_tick:
            self._done = True

        observation = self._get_observation()

        return observation, step_reward, self._done, info

    def render_all(self, mode="human"):
        window_ticks = np.arange(len(self._position_history))
        graph_x_axis = self.df.index[self.frame_bound[0] -
                                     self.window_size:self.frame_bound[1]]

        plt.plot(graph_x_axis, self.prices)

        short_ticks = []
        long_ticks = []
        for i, tick in enumerate(window_ticks):
            if self._position_history[i] == Positions.Short:
                short_ticks.append(tick - 1)
            elif self._position_history[i] == Positions.Long:
                long_ticks.append(tick - 1)

        plt.plot(graph_x_axis[short_ticks], self.prices[short_ticks], "ro")
        plt.plot(graph_x_axis[long_ticks], self.prices[long_ticks], "go")

        plt.suptitle(
            "Total Reward: %.6f" % self._total_reward
            + " ~ "
            + "Total Profit: %.6f" % self._total_profit
        )


class UpdatedStockEnv(UpdatedTradingEnv):
    def __init__(self, df, window_size, frame_bound, training_frame_bound):
        assert len(frame_bound) == 2

        self.frame_bound = frame_bound

        # Added training frame bound to normalize data to the range used during training
        self.training_frame_bound = training_frame_bound

        super().__init__(df, window_size)

        # 0 built in fees
        self.trade_fee_bid_percent = 0
        self.trade_fee_ask_percent = 0

    def _calculate_data_bounds(self, indicator_list):
        # New function normalizes data to a -1 and 1 range based on the "training_frame_bound" provided.
        data_start = self.training_frame_bound[0] - self.window_size
        data_end = self.training_frame_bound[1]

        prices = self.df.loc[:, "Close"].to_numpy()[data_start:data_end]

        # Hard coded indicators should match the ones defined in the process_data function
        SMA = self.df.loc[:, "SMA"].to_numpy()[data_start:data_end]
        RSI = self.df.loc[:, "RSI"].to_numpy()[data_start:data_end]
        MACD = self.df.loc[:, "MACD"].to_numpy()[data_start:data_end]
        MACD_signal = self.df.loc[:, "SIGNAL"].to_numpy()[data_start:data_end]
        int_time = self.df.loc[:, "Time"].to_numpy()[data_start:data_end]
        SMA_price_distance = (SMA) / prices

        training_set_bounds = [
            RSI, SMA_price_distance, MACD, MACD_signal, int_time]

        # Apply normalization to every indicator passed into this function, based on the min and max present in the training frame bound.
        for position in range(len(indicator_list)):
            indicator_list[position] = np.interp(
                indicator_list[position], (training_set_bounds[position].min(), training_set_bounds[position].max()), (-1, +1))

        return indicator_list

    def _process_data(self):

        # The indicators are hard coded below and must always be passed in the order stored in signal features.
        data_start = self.frame_bound[0] - self.window_size
        data_end = self.frame_bound[1]

        prices = self.df.loc[:, "Close"].to_numpy()[data_start:data_end]

        SMA = self.df.loc[:, "SMA"].to_numpy()[data_start:data_end]
        RSI = self.df.loc[:, "RSI"].to_numpy()[data_start:data_end]
        MACD = self.df.loc[:, "MACD"].to_numpy()[data_start:data_end]
        MACD_signal = self.df.loc[:, "SIGNAL"].to_numpy()[data_start:data_end]
        int_time = self.df.loc[:, "Time"].to_numpy()[data_start:data_end]
        SMA_price_distance = (SMA) / prices

        indicator_list = [
            RSI, SMA_price_distance, MACD, MACD_signal, int_time]

        self.bars = self.df.index[data_start:data_end]

        normalized_data = list(self._calculate_data_bounds(indicator_list))
        signal_features = np.column_stack(
            normalized_data)

        return prices, signal_features

    def _calculate_reward(self, action):

        step_reward = 0

        trade = False

        if (action == Actions.Buy.value and self._position == Positions.Short) or (
            action == Actions.Sell.value and self._position == Positions.Long
        ):
            trade = True

        if trade:
            current_price = self.prices[self._current_tick]
            last_trade_price = self.prices[self._last_trade_tick]
            price_diff = (current_price - last_trade_price) / last_trade_price

            # Modified to reward short positions as well
            if self._position == Positions.Long:
                step_reward += price_diff
            else:
                step_reward -= price_diff

        return step_reward

    def _update_profit(self, action):

        trade = False
        if (action == Actions.Buy.value and self._position == Positions.Short) or (
            action == Actions.Sell.value and self._position == Positions.Long
        ):
            trade = True

        # Calculate changing equity
        if (
            trade
            or (self._current_tick + 1 == self._end_tick)
        ):
            current_price = self.prices[self._current_tick]
            last_trade_price = self.prices[self._last_trade_tick]

            if self._position == Positions.Long:
                shares = (
                    self._total_profit
                ) / last_trade_price
                self._total_profit = (
                    (shares)
                    * current_price
                )
            else:
                shares = (
                    self._total_profit
                ) / last_trade_price
                self._total_profit = shares * (
                    2 * last_trade_price - current_price
                )
