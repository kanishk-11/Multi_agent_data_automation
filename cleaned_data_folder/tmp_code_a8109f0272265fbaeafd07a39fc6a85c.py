import pandas as pd
import numpy as np
from datetime import datetime

# Load the data
airline_id_to_name = pd.read_csv('/Users/kanishk/Desktop/CleanAgent/.files/bac9c0cd-c34b-4510-a610-3543fb380c3e/e1f212b9-5e70-40d1-afce-c2330a7841c3.csv')
flight_bookings = pd.read_csv('/Users/kanishk/Desktop/CleanAgent/.files/bac9c0cd-c34b-4510-a610-3543fb380c3e/3d8eb30a-7f2f-4628-861d-8335ecd487b3.csv')

# Step 1: Analyze the files to find all the column names
print("Flight Bookings Columns:", flight_bookings.columns.tolist())
print("Airline ID to Name Columns:", airline_id_to_name.columns.tolist())

# Step 2: Rename columns
flight_bookings.columns = [
    'Airline_ID', 'Flight No.', 'Departure_Date', 'Arrival_Date', 'Departure_Time', 
    'Arrival_Time', 'Booking_Code', 'Passenger_Name', 'Seat_No.', 'Class', 
    'Fare', 'Extras', 'Loyalty_Points', 'Status', 'Gate', 'Terminal', 
    'Baggage_Claim', 'Duration_Hours', 'Layovers', 'Layover_Locations', 
    'Aircraft_Type', 'Pilot', 'Cabin_Crew', 'Inflight_Entertainment', 
    'Meal_Option', 'Wifi_Available', 'Window_Seat', 'Aisle_Seat', 
    'Emergency_Exit_Row', 'Number_of_Stops', 'Reward_Program_Member'
]

# Step 3: Replace Airline_ID with Airline_Name
airline_id_to_name_dict = dict(zip(airline_id_to_name['airlie_id'], airline_id_to_name['airline_name']))
flight_bookings['Airline_Name'] = flight_bookings['Airline_ID'].map(airline_id_to_name_dict)
flight_bookings.drop('Airline_ID', axis=1, inplace=True)

# Step 4: Combine Departure and Arrival timestamps
flight_bookings['Departure_Timestamp'] = pd.to_datetime(flight_bookings['Departure_Date'] + ' ' + flight_bookings['Departure_Time'])
flight_bookings['Arrival_Timestamp'] = pd.to_datetime(flight_bookings['Arrival_Date'] + ' ' + flight_bookings['Arrival_Time'])

# Step 5: Replace Yes/No with boolean values
flight_bookings['Inflight_Entertainment'] = flight_bookings['Inflight_Entertainment'].replace({'Yes': True, 'No': False})
flight_bookings['Window_Seat'] = flight_bookings['Window_Seat'].replace({'Yes': True, 'No': False})
flight_bookings['Reward_Program_Member'] = flight_bookings['Reward_Program_Member'].replace({'Yes': True, 'No': False})

# Step 6: Swap timestamps if necessary and calculate Duration_Hours
for index, row in flight_bookings.iterrows():
    if row['Arrival_Timestamp'] < row['Departure_Timestamp']:
        flight_bookings.at[index, 'Arrival_Timestamp'], flight_bookings.at[index, 'Departure_Timestamp'] = (
            flight_bookings.at[index, 'Departure_Timestamp'], flight_bookings.at[index, 'Arrival_Timestamp']
        )
    flight_bookings.at[index, 'Duration_Hours'] = round((flight_bookings.at[index, 'Arrival_Timestamp'] - flight_bookings.at[index, 'Departure_Timestamp']).total_seconds() / 3600, 1)

# Step 7: Ensure Number_of_Stops equals Layovers
flight_bookings['Number_of_Stops'] = flight_bookings['Layovers'].apply(lambda x: x if x > 0 else 0)

# Step 8: Make Aisle_Seat the opposite of Window_Seat
flight_bookings['Aisle_Seat'] = ~flight_bookings['Window_Seat']

# Step 9: Set Loyalty_Points to 0 if not a reward program member
flight_bookings.loc[flight_bookings['Reward_Program_Member'] == False, 'Loyalty_Points'] = 0

# Step 10: Set default meal option if Extras includes 'Meal'
flight_bookings.loc[flight_bookings['Extras'].str.contains('Meal', na=False) & (flight_bookings['Meal_Option'] == 'No Meal'), 'Meal_Option'] = 'Vegetarian'

# Step 11: Delete unnecessary columns
flight_bookings.drop(['Departure_Date', 'Departure_Time', 'Arrival_Date', 'Arrival_Time'], axis=1, inplace=True)

# Step 12: Reorder columns
flight_bookings = flight_bookings[['Airline_Name', 'Flight No.', 'Departure_Timestamp', 'Arrival_Timestamp'] + 
                                    [col for col in flight_bookings.columns if col not in ['Airline_Name', 'Flight No.', 'Departure_Timestamp', 'Arrival_Timestamp']]]

# Step 13: Save the cleaned data
flight_bookings.to_csv('cleaned_data.csv', index=False)

# Display the cleaned data
print(flight_bookings.head())