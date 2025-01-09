## Title
<!-- Give your project a short title. -->
Crime Data Analysis in Chicago post Covid (2021-present)

## Main Question
1. What are the patterns in crime types and locations across different neighborhoods in Chicago?
2. Apply time-series models to predict crime rates based on weather trends.

## Description

<!-- Describe your data science project in max. 200 words. Consider writing about why and how you attempt it. -->
The objective of this project is to analyze and model crime data in Chicago to identify spatial and temporal patterns. By examining historical crime incidents, we aim to uncover insights into when and where various types of crimes are most likely to occur. Leveraging a dataset that includes information on crime type, location, and date, this project will employ data analysis and machine learning techniques to predict potential crime hotspots.

The analysis will provide a deeper understanding of crime patterns in Chicago, potentially aiding in proactive law enforcement and community awareness. This project will involve data cleaning, exploration, feature engineering, model development, and visualization to provide actionable insights.

## Datasources

### Datasource1: Chicago Crime Dataset
* Metadata URL: https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2/data
* CSV URL: https://data.cityofchicago.org/api/views/ijzp-q8t2/rows.csv?accessType=DOWNLOAD&bom=true&format=true&delimiter=;
* Data Type: CSV

The Chicago Crime Dataset provides a comprehensive record of reported crimes in the city of Chicago from 2001 to the present. This dataset is essential for analyzing crime patterns, trends, and correlations within the city and can aid in understanding the distribution and nature of criminal activity over time.

- **Date**: Date the crime was reported
- **Community Area:**: Specific neighborhood and approximate location of the incident
- **Primary Type**: Classification of the crime (e.g., assault, theft)
- **District**: Police district where the crime occurred, aiding in high-level regional crime analysis.

### Datasource2: Chicago Weather Dataset
* Metadata URL: https://meteostat.net/en/station/72530?t=2021-01-01/2025-01-02
* Data URL: https://bulk.meteostat.net/v2/monthly/72530.csv.gz
* Data Type: CSV

This data source will provide weather and climate data in Chicago, including average air temperature, daily minimum and maximum air temperature, monthly precipitation total, maximum snow depth, average wind direction and speed, peak wind gust, average sea-level air pressure, and monthly sunshine total.

## Work Packages

1. Extract Data from Multiple Sources
2. Implement Data Transformation Step in ETL Pipeline
3. Implement Data Loading Step in ETL Data Pipeline
4. Automated Tests for the Project
5. Continuous Integration Pipeline for the Project
6. Final Report and Presentation Submission
