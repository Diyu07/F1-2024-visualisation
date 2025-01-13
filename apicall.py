import requests
import csv

# Define the base API endpoint for the 2024 season
BASE_URL = "http://ergast.com/api/f1/2024"

# Fetch data from the API
def fetch_data(endpoint):
    response = requests.get(endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return None

# Parse the driver data
def parse_driver_data(data):
    drivers = []
    if data:
        driver_list = data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        for driver in driver_list:
            drivers.append({
                'DriverID': driver.get('driverId'),
                'FirstName': driver.get('givenName'),
                'LastName': driver.get('familyName'),
                'DateOfBirth': driver.get('dateOfBirth'),
                'Nationality': driver.get('nationality')
            })
    return drivers

# Fetch race results and points scored
def fetch_race_results():
    race_results = {}
    for round_no in range(1, 25):  # Assuming 24 races in the season
        endpoint = f"{BASE_URL}/{round_no}/results.json"
        data = fetch_data(endpoint)
        if data:
            race_data = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            if race_data:
                for result in race_data[0].get('Results', []):
                    driver_id = result.get('Driver', {}).get('driverId')
                    position = result.get('position')
                    points = result.get('points')
                    if driver_id not in race_results:
                        race_results[driver_id] = {
                            'TotalPoints': 0,
                            'RacePositions': [],
                            'RacePoints': []
                        }
                    race_results[driver_id]['RacePositions'].append(position)
                    race_results[driver_id]['RacePoints'].append(points)
                    race_results[driver_id]['TotalPoints'] += float(points)
    return race_results

# Fetch qualifying lap times
def fetch_qualifying_data():
    qualifying_data = {}
    for round_no in range(1, 25):
        endpoint = f"{BASE_URL}/{round_no}/qualifying.json"
        data = fetch_data(endpoint)
        if data:
            race_data = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            if race_data:
                for result in race_data[0].get('QualifyingResults', []):
                    driver_id = result.get('Driver', {}).get('driverId')
                    lap_time = result.get('Q3') or result.get('Q2') or result.get('Q1')
                    if driver_id not in qualifying_data:
                        qualifying_data[driver_id] = []
                    qualifying_data[driver_id].append(lap_time)
    return qualifying_data

# Merge all data
def merge_driver_data(drivers, race_results, qualifying_data):
    for driver in drivers:
        driver_id = driver['DriverID']
        driver['TotalPoints'] = race_results.get(driver_id, {}).get('TotalPoints', 0)
        driver['RacePositions'] = race_results.get(driver_id, {}).get('RacePositions', [None] * 24)
        driver['RacePoints'] = race_results.get(driver_id, {}).get('RacePoints', [0] * 24)
        driver['QualifyingTimes'] = qualifying_data.get(driver_id, [None] * 24)
    return drivers

# Save data to a CSV file
def save_to_csv(file_name, data):
    if data:
        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Data successfully saved to {file_name}")
    else:
        print("No data to save.")

# Main script execution
def main():
    print("Fetching driver data for the 2024 season...")
    driver_data = fetch_data(f"{BASE_URL}/drivers.json")
    drivers = parse_driver_data(driver_data)

    print("Fetching race results and points...")
    race_results = fetch_race_results()

    print("Fetching qualifying lap times...")
    qualifying_data = fetch_qualifying_data()

    print("Merging all data...")
    complete_data = merge_driver_data(drivers, race_results, qualifying_data)

    print("Saving data to CSV...")
    save_to_csv("f1_2024_driver_analysis.csv", complete_data)

if __name__ == "__main__":
    main()
