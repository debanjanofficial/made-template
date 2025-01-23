# Methods of Advanced Data Engineering

This repository contains the entire workflow, data, and analyses for exploring patterns of crime incidents and their correlation with environmental factors in Chicago using python and also all mandatory exercises using jayvee.

# Project Name: Analyzing the Impact of Weather on Crime Patterns in Chicago (Post-COVID, 2021-Present)

Chicago's urban landscape presents a unique opportunity to study the interplay between weather patterns and criminal activity. This project examines the relationship between temperature variations and crime incidents in Chicago from 2021 onwards, a period marked by significant societal changes following the COVID-19 pandemic.
By analyzing daily temperature data alongside crime reports, we seek to understand how weather conditions might influence criminal behavior across Chicago's diverse neighborhoods. The study combines two key datasets: detailed crime records from the Chicago Police Department and comprehensive weather data including temperature extremes, creating a robust foundation for pattern analysis.

---

## Features

- Exploratory Data Analysis (EDA) for temporal, spatial, and environmental trends.
- Insights into high-risk areas in Chicago.
- using meteorological data to investigate relationships between crime and environmental conditions.
- Automated ETL (Extract, Transform, Load) pipeline for data processing.
- Comprehensive visualizations including heatmaps, scatterplots, and bar charts.

---

## Dataset Details

### Chicago Crime Data
- **Source:** Chicago Crime Dataset(2021-Present): Contains detailed
crime records.
- **Attributes:** Date, time, location, demographics, and more.

### Chicago Weather Data
- **Source:** Chicago Weather Data (2021-present)
- **Attributes:** Temperature, precipitation, and other environmental factors.

For dataset preparation, preprocessing, and license compliance, see the `data` folder and `source_info.json`.

---

## Repository Structure
   ```bash
made-template/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── exercise-feedback.yml
├── .vscode/
│   ├── extensions.json
│   └── settings.json
├── data/
│   ├── .gitkeep
│   ├── Chicago_Weather.csv
│   ├── crime_data_filtered.csv
│   ├── Crimes_-_2001_to_Present.csv
│   └── weather_data.csv
├── examples/
│   ├── data-exploration-example.ipynb
│   ├── data.sqlite
│   ├── final-report-example.ipynb
│   └── project-plan-example.md
├── exercises/
│   ├── .gitkeep
│   ├── airports.sqlite
│   ├── country-stats.sqlite
│   ├── exercise1.jv
│   ├── exercise2.jv
│   ├── exercise3.jv
│   ├── exercise4.jv
│   ├── exercise5.jv
│   ├── gtfs.sqlite
│   └── temperatures.sqlite
├── project/
│   ├── analysis.ipynb
│   ├── analysis-report.pdf
│   ├── data-report.pdf
│   ├── pipeline.py
│   ├── pipeline.sh
│   ├── project-plan.md
│   ├── source_info.json
│   └── tests.sh
├── .gitignore
├── LICENSE
├── pipeline.log
├── README.md
├── requirements.txt
└── .DS_Store 
   ```


## Repo Details

### `.github/workflows`
- **ci.yml**: Defines the continuous integration pipeline for testing the code.
- **exercise-feedback.yml**: Configures the workflow for providing exercise feedback.

### `data`
- **.gitkeep**: Placeholder for ensuring the `data` directory is versioned.

### `exercises`
- **airports.sqlite, country-stats.sqlite, gtfs.sqlite, temperatures.sqlite, trees.sqlite**: Databases from different exercises.
- **exercise1.jv - exercise5.jv**: Sample Jayvee files for exercises.
- **.gitkeep**: Ensures the directory remains in version control.

### `project`
- **analysis-report.pdf**: Final report documenting the key findings and analysis.
- **data-report.pdf**: Detailed report on the processed datasets.
- **pipeline.py**: Python script automating the ETL process.
- **pipeline.sh**: Shell script for running the pipeline.
- **project-plan.md**: Project plan outlining objectives, methodology, and milestones.
- **source_info.json**: JSON file with metadata about the sources used.
- **tests.sh**: Bash script for testing data and pipeline functionality.
-**analysis.ipynb**: Exploratory Data Analysis of cleaned, preprocessed data which are in `data` folder.

### Root Files
- **LICENSE**: Licensing details for the repository.
- **README.md**: This documentation file.
- **requirements.txt**: Python dependencies required for the project.

---

## Installation

### Prerequisites
- Python 3.11
- Required libraries (see `requirements.txt`)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/debanjanofficial/made-template.git
   cd made-template

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Run the pipeline
   to execute the data ETL pipeline and perform analysis:
   ```bash 
   python3 project/pipeline.py

4. Or, use the shell script to automate:
   ```bash 
   bash project/pipeline.sh

5. Test the Pipeline
   Run the provided test suite to ensure the integrity of the pipeline:
   ```bash
   bash project/tests.sh

---

## Key Insights

### Temporal Patterns
- Summer months record approximately 260,000 crimes whereas winter periods show lower rates with about 200,000 crimes.

### Spatial Trends
- The average daily crime count maintains a relatively stable baseline between 600-800 incidents throughout the period.

### Environmental Factors
- Criminal activity tends to increase with higher
temperatures.
- Snowfall has a deterrent effect on crime rates.
- Precipitation has minimal impact on criminal behavior.
- Seasonal variations significantly influence crime patterns.

For detailed analysis, see the `analysis-report.pdf` in the `project` folder.

---

## Future Work

- **Enhanced Data Integration**:Incorporation of multiple weather station data points
- **Advanced Analytics**: Development of predictive models for crime forecasting
- **Detailed Crime Pattern**:Clear relationship between urban infrastructure and crime locations

---

## References

- **Chicago Crime Data**: [Public Dataset Sources](https://data.cityofchicago.org/Public-Safety/Crimes-2022/9hwr-2zxp/about_data)
- **Chicago Weather Data**: [Public Dataset Sources](https://meteostat.net/en/station/72530?t=2021-01-01/2025-01-0)

---

## License

This project is licensed under the CC0-1.0 license. See the `LICENSE` file for details.




