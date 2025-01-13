import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Read CSV File
# Update the file path to your actual CSV file
file_path = "f1_2024_driver_analysis.csv"
data = pd.read_csv(file_path)

# Step 2: Data Cleaning
# Convert RacePoints and QualifyingTimes columns from string representation of lists to actual lists
data['RacePoints'] = data['RacePoints'].apply(lambda x: [int(i) for i in x.strip("[]").replace("'", "").split(',')] if pd.notnull(x) else [])
data['QualifyingTimes'] = data['QualifyingTimes'].apply(lambda x: [i.strip() for i in x.strip("[]").replace("'", "").split(',')] if pd.notnull(x) else [])
data['RacePositions'] = data['RacePositions'].apply(lambda x: [int(i) for i in x.strip("[]").replace("'", "").split(',')] if pd.notnull(x) else [])

# Parse qualifying times to seconds
def parse_lap_time(lap_time):
    if lap_time and ':' in lap_time:
        try:
            minutes, seconds = lap_time.split(':')
            return int(minutes) * 60 + float(seconds)
        except ValueError:
            return None
    return None

data['QualifyingTimes'] = data['QualifyingTimes'].apply(lambda x: [parse_lap_time(time) for time in x])

# Step 3: Analyze
# Calculate cumulative points
data['CumulativePoints'] = data['RacePoints'].apply(lambda x: pd.Series(x).cumsum().tolist())

# Calculate correlation between qualifying times and final positions
def calculate_correlation(qual_times, race_positions):
    valid_data = [(q, r) for q, r in zip(qual_times, race_positions) if q is not None]
    if valid_data:
        qual, race = zip(*valid_data)
        return pd.Series(qual).corr(pd.Series(race))
    return None

data['QualifyingFinalCorrelation'] = data.apply(lambda row: calculate_correlation(row['QualifyingTimes'], row['RacePositions']), axis=1)

# Step 4: Visualize
# Plot cumulative points trend
for index, row in data.iterrows():
    plt.plot(row['CumulativePoints'], label=f"{row['FirstName']} {row['LastName']}")
plt.title("Cumulative Points Trend")
plt.xlabel("Races")
plt.ylabel("Cumulative Points")
plt.legend()
plt.show()

# Bar plot for average race points
data['AveragePoints'] = data['RacePoints'].apply(lambda x: sum(x) / len(x) if x else 0)
plt.bar(data['FirstName'], data['AveragePoints'], color='blue')
plt.title("Average Race Points")
plt.xlabel("Driver")
plt.ylabel("Average Points")
plt.xticks(rotation=45)
plt.show()
