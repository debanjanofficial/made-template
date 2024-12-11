#!/bin/bash

# Set paths for input data and output database
DB_FILE="data/processed_data.db"
CSV_CRIME_INPUT="data/crime_data.csv"
CSV_WEATHER_INPUT="data/Chicago_Weather.csv"

# Run the pipeline
echo "Loading and executing pipeline.py"
python project/pipeline.py

# Validate the pipeline execution success
if [ $? -ne 0 ]; then
    echo "Failed to execute pipeline.py"
    exit 1
fi

# Validate input files exist
echo "Checking input files..."
if [ ! -f "$CSV_CRIME_INPUT" ]; then
    echo "Failed: $CSV_CRIME_INPUT file does not exist."
    exit 1
fi
if [ ! -f "$CSV_WEATHER_INPUT" ]; then
    echo "Failed: $CSV_WEATHER_INPUT file does not exist."
    exit 1
fi

# Check for the existence of the database file
echo "Final check for database file..."
if [ -f "$DB_FILE" ]; then
    echo "Database file exists."
else
    echo "Test failed: Database file is missing."
    exit 1
fi

# Validate database tables
echo "Checking database tables..."
TABLES=$(sqlite3 "$DB_FILE" ".tables")

# Adjust table name checks to be case-insensitive
echo "$TABLES" | grep -qi "CrimeData"
if [ $? -eq 0 ]; then
    echo "Test passed: 'CrimeData' table exists."
else
    echo "Test failed: 'CrimeData' table is missing."
    exit 1
fi

echo "$TABLES" | grep -qi "WeatherData"
if [ $? -eq 0 ]; then
    echo "Test passed: 'WeatherData' table exists."
else
    echo "Test failed: 'WeatherData' table is missing."
    exit 1
fi

echo "Listing columns in 'CrimeData' table..."
COLUMNS=$(sqlite3 "$DB_FILE" "PRAGMA table_info(CrimeData);")
echo "$COLUMNS"

echo "Listing columns in 'WeatherData' table..."
COLUMNS=$(sqlite3 "$DB_FILE" "PRAGMA table_info(WeatherData);")
echo "$COLUMNS"


echo ""

# Data Integrity Checks for the 'CrimeData' table
#echo "Verifying data integrity in the 'CrimeData' table..."
#NULL_CHECK=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM CrimeData WHERE date IS NULL;")
#if [ "$NULL_CHECK" -eq 0 ]; then
    #echo "Data integrity check passed: No unexpected NULL values in 'CrimeData'."
#else
    #echo "Data integrity check failed: Found $NULL_CHECK unexpected NULL values in 'CrimeData'."
    #exit 1
#fi

echo ""

# Data Integrity Checks for the 'WeatherData' table
echo "Verifying data integrity in the 'WeatherData' table..."
TMAX_CHECK=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM WeatherData WHERE tmax IS NULL;")
TMIN_CHECK=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM WeatherData WHERE tmin IS NULL;")
if [ "$TMAX_CHECK" -eq 0 ] && [ "$TMIN_CHECK" -eq 0 ]; then
    echo "Data integrity check passed: No unexpected NULL values in 'WeatherData'."
else
    echo "Data integrity check failed: Found $TMAX_CHECK unexpected NULL values in 'tmax', $TMIN_CHECK unexpected NULL values in 'tmin'."
    exit 1
fi

echo ""
echo "All tests passed successfully."
