import numpy as np
import csv
import random
import math
import pandas as pd
import os
import sys

# File path for carbon intensity data
file_path = '/Users/cheko/Desktop/Carbon/carbon/data/US-CAL-CISO_2023_hourly.csv'

# File path for use behavior in appliance usage
file_path_start_time = '/Users/cheko/Desktop/Carbon/carbon/data/15minute_data_california.csv'

# Create the output folder if it doesn't exist
output_folder = 'two_day_forecasts'
os.makedirs(output_folder, exist_ok=True)


# Define a class for a Task
class Task:
    def __init__(self, name, duration, deadline, start_time):
        self.name = name
        self.duration = duration
        self.deadline = deadline
        self.start_time = start_time

# Scheduler class that will handle the logic for tasks
class Scheduler:
    def __init__(self, region, carbon_intensity_forecast):
        self.region = region
        self.carbon_intensity_forecast = carbon_intensity_forecast  # Array of size 48, 2 day forecast
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    """Executes the task at the given start time and calculates carbon usage."""
    def normal_execution(self, task):
        start_time = task.start_time  # Start at the defined start time
        
        end_time = start_time + int(math.ceil(task.duration))  # Round up duration to nearest hour because predictions are in hours
        # Flag if end time is past the two days
        if end_time > len(self.carbon_intensity_forecast):
            print(f"Task {task.name}: Can't fit in the 48 hour period.") # Revisit this policy.

        # Sum the carbon usage between start time (now) and end time
        carbon_usage = sum(self.carbon_intensity_forecast[start_time:end_time])
        return carbon_usage, start_time

    """Finds the optimal time to start based on the carbon intensity data."""
    def carbon_optimized_execution(self, task):
        best_start_time = None
        min_carbon_usage = float('inf')
        carbon_usage = sys.maxsize

        # Iterate over possible start times within the available window (before the deadline)
        for start_time in range(task.start_time, task.deadline - int(math.ceil(task.duration))):
            end_time = start_time + int(math.ceil(task.duration))
            if end_time <= task.deadline:
                carbon_usage = sum(self.carbon_intensity_forecast[start_time:end_time])
            
            # Update min carbon
            if carbon_usage < min_carbon_usage:
                min_carbon_usage = carbon_usage
                best_start_time = start_time

        # Iteration was unable to find best start time, however, this is unliley because 
        # we always start from the start now period. 

        if best_start_time is None:
            print(f"Task {task.name}: Cannot find an optimal time. Executing immediately.")
            return self.normal_execution(task)
        return min_carbon_usage, best_start_time


# A class for Household that will have its own scheduler
class Household:
    def __init__(self, household_id, region, carbon_intensity_forecast):
        self.household_id = household_id
        self.scheduler = Scheduler(region, carbon_intensity_forecast)

    def schedule_task(self, task):
        # Get carbon saving from starting immediately
        normal_usage, normal_start_time = self.scheduler.normal_execution(task)
        # Round off carbon saving to 2 dp
        normal_usage = round(normal_usage, 2)
        
        # Get optimal carbon for the given duration
        optimized_usage, optimized_start_time = self.scheduler.carbon_optimized_execution(task)
        # Round off carbon saving to 2 dp
        optimized_usage = round(optimized_usage, 2)
        
        # Difference bewteen optimized and normal start carbon
        carbon_savings = round(normal_usage - optimized_usage, 2)
        
        # Calculate the delay in start time
        delay = optimized_start_time - normal_start_time
        
        return normal_usage, optimized_usage, carbon_savings, normal_start_time, optimized_start_time, delay
    
# Function to read start times from available data

def get_rounded_times_for_date(date_str):

    # Get date
    date_str = '2014' + date_str[4:]

    # Read the CSV file
    data = pd.read_csv(file_path_start_time )

    # Filter for rows where 'dishwasher1' > 0.1
    # At >0.1 kW we know the washer is working
    data = data[data['dishwasher1'] > 0.1]

    # Convert 'local_15min' to datetime, forcing UTC
    data['local_15min'] = pd.to_datetime(data['local_15min'], utc=True)

    # Extract the date from 'local_15min'
    data['date'] = data['local_15min'].dt.date

    # Filter for the specified date
    date_filter = data[data['date'] == pd.to_datetime(date_str).date()]

    # Create a list for local times rounded to the next half hour
    rounded_times = []

    for time in date_filter['local_15min']:
        # Get the hour and minutes from the time
        hour = time.hour
        minutes = time.minute
        
        # Round the hour based on the minutes
        if minutes >= 30:
            rounded_time = hour + 1  # Round up to the next hour
        else:
            rounded_time = hour  # Keep the current hour

        rounded_times.append(int(rounded_time))

    return rounded_times

# Function to read the carbon intensity data from the CSV
def read_file():
    df = pd.read_csv(file_path)

    # Convert the 'Datetime (UTC)' column to datetime format
    df['Datetime (UTC)'] = pd.to_datetime(df['Datetime (UTC)'])

    # Localize the UTC times to UTC timezone
    df['Datetime (UTC)'] = df['Datetime (UTC)'].dt.tz_localize('UTC')

    # Convert UTC to California Time (Pacific Time Zone)
    df['California Time'] = df['Datetime (UTC)'].dt.tz_convert('America/Los_Angeles')

    # Extract the date part from the 'California Time' column
    df['Date'] = df['California Time'].dt.date

    # Group by the 'Date' and collect the 'Carbon Intensity gCO₂eq/kWh (direct)' values as a list
    carbon_intensity_per_hour = df.groupby(df['California Time'].dt.date)['Carbon Intensity gCO₂eq/kWh (direct)'].apply(list)

    return carbon_intensity_per_hour

# Function to handle incomplete data by filling missing hours with available data
def fill_incomplete_data(forecast, required_size=48):
    current_size = len(forecast)
    if current_size < required_size:
        missing_count = required_size - current_size
        forecast.extend(forecast[:missing_count])  # Fill missing data with the beginning values
    return forecast

# Function to get the forecast for the next 48 hours given a date
def get_two_day_forecast(start_date, carbon_intensity_per_hour):

    forecast = []

    # Get data for the first 24 hours (start_date)
    if start_date in carbon_intensity_per_hour:
        forecast.extend(carbon_intensity_per_hour[start_date][:24])  # First 24 hours
    
    # Get data for the next day (start_date + 1 day)
    next_day = start_date + pd.Timedelta(days=1)
    if next_day in carbon_intensity_per_hour:
        forecast.extend(carbon_intensity_per_hour[next_day][:24])  # Next 24 hours

    # Fill the data if less than 48 hours is available
    if(len(forecast) < 48):
        forecast = fill_incomplete_data(forecast, required_size=48)

    return forecast

# Main function to run the task scheduling
def run_task_scheduling():
    # Read the carbon intensity data
    carbon_intensity_per_hour = read_file()

    # Ask user to input a date to get the forecast
    user_date = input("Enter a date (YYYY-MM-DD) to get a 48-hour forecast: ")
    start_date = pd.to_datetime(user_date).date()

    # Get the forecast for the next two days
    forecast = get_two_day_forecast(start_date, carbon_intensity_per_hour)


  
    household_times = get_rounded_times_for_date(user_date)

    # for i in range(num_households):
    temp = 0
    for i in household_times:

        household_id = temp
        # Create a household with the carbon intensity data forecast
        household = Household(household_id, "ExampleRegion", forecast)
        
        # Random task duration between 0.5 and 3.5 hours (rounded to nearest 0.5)
        duration = round(random.uniform(0.5, 3.5) * 2) / 2
        
        # Round up duration for calculating end time constraint
        rounded_duration = int(math.ceil(duration))
        
        # Random deadline between the current hour and 42 (leaving room for task completion)
        deadline = random.randint(rounded_duration, 42)
        
        # Ensure the start time leaves room for the task to be completed before the deadline
        # max_start_time = min(23, deadline - rounded_duration)
        # start_time = random.randint(0, max_start_time)
        start_time = int(i)
        deadline = random.randint(start_time + int(math.ceil(duration)), 42)
        temp+=1
        
        # Create a task with the generated duration, random deadline, and random start time
        task = Task(f"Dishwashing {household_id}", duration=duration, deadline=deadline, start_time=start_time)
        
        # Schedule and calculate savings for the task
        normal_usage, optimized_usage, carbon_savings, normal_start_time, optimized_start_time, delay = household.schedule_task(task)
        

        # Creates households the appliance start times 

        '''
        What if unique households have more than one appliance working in this time
        Maybe it should be per appliance with each time an appliance repeats itself we have 
        The same household but a more complex system
        
        '''
        household_data = []
        # Store the data
        household_data.append({
            'household_id': household_id,
            'task_name': task.name,
            'duration_hours': duration,
            'deadline_hour': task.deadline,
            'normal_start_time': normal_start_time,
            'optimized_start_time': optimized_start_time,
            'delay_hours': delay,
            'normal_emissions': normal_usage,
            'green_emissions': optimized_usage,
            'carbon_savings': carbon_savings
        })

    # Write the results to a CSV file

    month = user_date[5:7]
    csv_filename = f'household_carbon_savings_with_dynamic_deadline_and_delays_{month}_2.csv'



    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['household_id', 'task_name', 'duration_hours', 'deadline_hour', 'normal_start_time', 'optimized_start_time', 'delay_hours', 'normal_emissions', 'green_emissions', 'carbon_savings'])
        writer.writeheader()
        writer.writerows(household_data)

    print(f'Results saved to {csv_filename}')

def get_house_holds(df):
    house_list = []
    for house in df.unique():
        house_list.add(house)
    return house_list

'''
for each house: return a dict with dates as key, where each date has a list of tasks and whatever 
                is needed for scheduling
    * for each dict, 
     - grab the date part of the dict, if not empty, put it into the scheduler
        - scheduler grabs forecast for that date
        - then calculates the carbon savings for the tasks of that day
        - then puts the results into a results file for that household
        - check if there are any special trends for a given household
        - all results from all the households are appended one file and carbon savings analyzed
for each day: check if there is a task for any of the appliances (default to dishwasher)
            - find when those appliances need to start, and find their duration
            - return a list of tasks their info as whatever else we need
             - drop 

- summary stats: 
    check the data for each households
    - at a month level, try to understand the summary statistics on when a typical load is 
    scheduled, a long with its finish time, and the average time till next load. 
    - how to find time till next load: since we only consider 48 hour forecast, and the
    - maximum delay is only until the next day 6pm, then just focus on the frequency of 
    having a load in the next 24 hours, that is, up to (6pm the following day). 
    The 6pm is heuristic in that the data shows there might be need to delay the task
    if after 6pm. 
             
'''



if __name__ == "__main__":
    run_task_scheduling()
