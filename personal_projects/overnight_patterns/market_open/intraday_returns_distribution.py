import pandas as pd
import math
from matplotlib import pyplot as plt
import statistics
import numpy as np


assetName = "Ford"

# Import intraday increment data
stock_price_data = pd.read_csv("ford_data.csv")
stock_price_data.set_index("Date", inplace=True)
stock_price_data.index = pd.to_datetime(stock_price_data.index)
print(stock_price_data)


# We will be graphing the cumulative returns of intraday sections. Specify the length of the periods to analyze.
subsection_length = 5
total_sections = 390 / subsection_length

# Weekend returns typically differ from the rest of the overnight returns. Because we are investigating the relationship between the typical
# overnight trend and the morning returns that follow, weekends and Mondays can be exluded with the variable below.
exclude_monday = True

# Dictionary containing the subsection of the day, and containing its corresponding everyday returns. Ex: First minute of the day
# subsection list will contain values corresponding to the return of the first minute of every day.

subsection_returns = {}
for n in range(int(total_sections)):
    subsection_returns[n] = []

subsection_returns_corresponding_dates = {}
for n in range(int(total_sections)):
    subsection_returns_corresponding_dates[n] = []

previous_section_of_day = None
entry_price = stock_price_data["Close"][stock_price_data.index[0]]


# Loop through data and calculate averages per specified section. Code is slow so give it a minute or consider shorting the range for analysis.
for index_position in range(len(stock_price_data.index)):

    current_index = stock_price_data.index[index_position]
    minute_number = (current_index.hour - 9) * 60 + (current_index.minute - 30)
    weekday = current_index.weekday()
    section_of_day = math.floor(minute_number / subsection_length)

    if previous_section_of_day != section_of_day and weekday != 0:

        if section_of_day == 0:
            entry_price = stock_price_data["Open"][current_index]

        final_price = stock_price_data["Close"][
            stock_price_data.index[index_position + subsection_length - 1]
        ]

        subsection_returns[section_of_day].append(
            (final_price - entry_price) / entry_price
        )

        subsection_returns_corresponding_dates[section_of_day].append(current_index)

        entry_price = final_price

    previous_section_of_day = section_of_day

# Print a bar graph of subsections and their corresponding average returns
averages = []
for key in range(int(total_sections)):
    averages.append(statistics.mean(subsection_returns[key]))

plt.bar(np.arange(0, len(subsection_returns)), averages)
plt.title(assetName)
plt.xlabel("Subsection")
plt.ylabel("Average Return")
plt.show()

# Graph the cumulative returns of the first few minutes of market open.
fig = plt.figure()
for n in range(4):
    cumulativeReturns = np.cumprod(np.array(subsection_returns[n]) + 1)
    subplot = fig.add_subplot(2, 2, n + 1)
    subplot.plot(subsection_returns_corresponding_dates[n], cumulativeReturns)
    subplot.title.set_text("Minute " + str(n + 1))

fig.suptitle("Subsection Cumulative Returns")
plt.show()
