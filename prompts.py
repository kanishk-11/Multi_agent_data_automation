class Prompts:
    ORIGINAL_COLUMNS = "airlie_id,flght#,departure_dt,arrival_dt,dep_time,arrivl_time,booking_cd,passngr_nm,seat_no,class,fare,extras,loyalty_pts,status,gate,terminal,baggage_claim,duration_hrs,layovers,layover_locations,aircraft_type,pilot,cabin_crew,inflight_ent,meal_option,wifi,window_seat,aisle_seat,emergency_exit_row,number_of_stops,reward_program_member"
    
    FLIGHT_COLUMN_TYPES = "Airline_ID, Flight No., Departure_Date, Arrival_Date, Departure_Time, Arrival_Time, Booking_Code, Passenger_Name, Seat_No., Class, Fare, Extras, Loyalty_Points, Status, Gate, Terminal, Baggage_Claim, Duration_Hours, Layovers, Layover_Locations, Aircraft_Type, Pilot, Cabin_Crew, Inflight_Entertainment, Meal_Option, Wifi_Available, Window_Seat, Aisle_Seat, Emergency_Exit_Row, Number_of_Stops, Reward_Program_Member"
    
    TERMINATION_NOTICE = "\n\nIf you think all the conversations complete the task correctly and smoothly, then ONLY output TERMINATE to indicate the conversation is finished and this is your last message."
    CLEANED_DATA_STORAGE_DIRECTORY="cleaned_data_folder"
    
    QUERY_SYSTEM_MESSAGE = """You are a senior python engineer specialized in airline data processing.
                    You will be asked to perform some queries on the data.
                    Write the code to perform the queries
                    the code should only print the output !!!
                    """
                    
    ClEANR_SYSTEM_MESSAGE = """
                        You are a senior python engineer specialized in airline data cleaning.
                        You are responsible for writing python code to clean and standardize airline data.
                        Please ALWAYS show the result after ALL these steps only!!!
                    """
 
    @staticmethod
    def get_problem_prompt(path, flight_column_types, original_columns):
        return f""" Clean the airline data table {path}.\n
                 the current data has columns: {original_columns}. 
            Focus on doing this through these steps one by one:
            1. Analyse the files to find all the columns names
            2. Change columns to {flight_column_types}.
            3. Replace all the entries in the first 'Airline_ID' column, by Airline_Name for each flight using the AirlineID to Name file. Then change this 'Airline_ID' column name to 'Airline_Name'.
            4. Combine Departure_Time with Departure_Date, and Arrival_Time with Arrival_Date, to give a complete timestamp.
            5. In Inflight_Entertainment, Window_Seat, and Reward_Program_Member columns. Replace Yes with boolean 'TRUE', and No with boolean 'False'
            6. If for a particular row, Arrival_Timestamp is less than the Departure_Timestamp, swap the Arrival_Timestamp and Departure_Timestamp for that row. Calculate Duration_Hours = (Arrival_Date - Departure_Date) in hours. ROUND THEM OFF to ONE DECIMAL PLACE.
            7. Number_of_Stops must be equal to Layovers. If layovers > 0, number_of_stops must > 0
            8. In all rows, make the Aisle_Seat bool value opposite of Window_Seat value of that row.
            9. If reward_program_member = 'No', Loyalty_Points = 0
            10. If Extras includes 'Meal', meal_option cannot be 'No Meal'. Use vegetarian as default
                        Use pandas, numpy, re, datetime, and other relevant libraries.
            11. Delete Departure_Date, Departure_Time, Arrival_Date and Arrival_Time columns.
            12. Put Departure_Timestamp and Arrival_Timestamp columns as third and fourth columns respectively.
            13. Save the new data as csv : cleaned_data.csv
            """
    
    @staticmethod
    def get_query_prompt(dataframe, path, question):
        return f""" You are given standarized airline with data: {dataframe} path: {path}.
            Given the query : {question}.
            1. From the contents of all the columns, find out which columns in the data will be needed to process this information.
            2. Define the query that you would need to perform in the contents of these columns.
            3. write the code for performing the query using pandas.
            4. print the output in a user friendly, readable format."""
    