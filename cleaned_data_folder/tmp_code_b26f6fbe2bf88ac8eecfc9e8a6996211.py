import pandas as pd
import numpy as np
from datetime import datetime

# Load the data
airline_id_to_name = pd.read_csv('/Users/kanishk/Desktop/CleanAgent/.files/c20c13f9-e64b-4d57-9915-760959cc9001/67033978-bae9-435d-9ec1-138f4bd6c817.csv')
flight_bookings = pd.read_csv('/Users/kanishk/Desktop/CleanAgent/.files/c20c13f9-e64b-4d57-9915-760959cc9001/0f30f3ca-0a27-48c5-96c5-292b3421f8d8.csv')

# Step 1: Analyze the files to find all the column names
print("Flight Bookings Columns:", flight_bookings.columns.tolist())
print("Airline ID to Name Columns:", airline_id_to_name.columns.tolist())

# Step 2: Rename columns
flight_bookings.columns = [
    'Airline_ID', 'Flight_No.', 'Departure_Date', 'Arrival_Date', 'Departure_Time', 
    'Arrival_Time', 'Booking_Code', 'Passenger_Name', 'Seat_No.', 'Class', 
    'Fare', 'Extras', 'Loyalty_Points', 'Status', 'Gate', 'Terminal', 
    'Baggage_Claim', 'Duration_Hours', 'Layovers', 'Layover_Locations', 
    'Aircraft_Type', 'Pilot', 'Cabin_Crew', 'Inflight_Entertainment', 
    'Meal_Option', 'Wifi_Available', 'Window_Seat', 'Aisle_Seat', 
    'Emergency_Exit_Row', 'Number_of_Stops', 'Reward_Program_Member'
]

# Step 3: Replace Airline_ID with Airline_Name
airline_id_to_name_dict = dict(zip(airline_id_to_name['Airline_ID'], airline_id_to_name['Airline_Name']))
flight_bookings['Airline_Name'] = flight_bookings['Airline_ID'].map(airline_id_to_name_dict)
flight_bookings.drop('Airline_ID', axis=1, inplace=True)

# Step 4: Combine Departure_Time with Departure_Date, and Arrival_Time with Arrival_Date
flight_bookings['Departure_Timestamp'] = pd.to_datetime(flight_bookings['Departure_Date'] + ' ' + flight_bookings['Departure_Time'])
flight_bookings['Arrival_Timestamp'] = pd.to_datetime(flight_bookings['Arrival_Date'] + ' ' + flight_bookings['Arrival_Time'])

# Step 5: Replace Yes/No with boolean values
flight_bookings['Inflight_Entertainment'] = flight_bookings['Inflight_Entertainment'].replace({'Yes': True, 'No': False})
flight_bookings['Window_Seat'] = flight_bookings['Window_Seat'].replace({'Yes': True, 'No': False})
flight_bookings['Reward_Program_Member'] = flight_bookings['Reward_Program_Member'].replace({'Yes': True, 'No': False})

# Step 6: Swap timestamps if Arrival is before Departure and calculate Duration_Hours
flight_bookings.loc[flight_bookings['Arrival_Timestamp'] < flight_bookings['Departure_Timestamp'], ['Arrival_Timestamp', 'Departure_Timestamp']] = flight_bookings.loc[flight_bookings['Arrival_Timestamp'] < flight_bookings['Departure_Timestamp'], ['Departure_Timestamp', 'Arrival_Timestamp']].values
flight_bookings['Duration_Hours'] = (flight_bookings['Arrival_Timestamp'] - flight_bookings['Departure_Timestamp']).dt.total_seconds() / 3600
flight_bookings['Duration_Hours'] = flight_bookings['Duration_Hours'].round(1)

# Step 7: Ensure Number_of_Stops equals Layovers
flight_bookings['Number_of_Stops'] = flight_bookings['Layovers'].where(flight_bookings['Layovers'] > 0, 0)

# Step 8: Make Aisle_Seat the opposite of Window_Seat
flight_bookings['Aisle_Seat'] = ~flight_bookings['Window_Seat']

# Step 9: Set Loyalty_Points to 0 if Reward_Program_Member is 'No'
flight_bookings.loc[flight_bookings['Reward_Program_Member'] == False, 'Loyalty_Points'] = 0

# Step 10: Set default meal option if Extras includes 'Meal'
flight_bookings.loc[flight_bookings['Extras'].str.contains('Meal', na=False) & (flight_bookings['Meal_Option'] == 'No Meal'), 'Meal_Option'] = 'Vegetarian'

# Step 11: Delete unnecessary columns
flight_bookings.drop(['Departure_Date', 'Departure_Time', 'Arrival_Date', 'Arrival_Time'], axis=1, inplace=True)

# Step 12: Reorder columns to place Departure_Timestamp and Arrival_Timestamp as third and fourth columns
columns_order = list(flight_bookings.columns[:2]) + ['Departure_Timestamp', 'Arrival_Timestamp'] + list(flight_bookings.columns[2:-2])
flight_bookings = flight_bookings[columns_order]

# Step 13: Save the cleaned data as csv
flight_bookings.to_csv('cleaned_data.csv', index=False)

# Display the cleaned data
print(flight_bookings.head())