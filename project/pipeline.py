import os
import subprocess
import pandas as pd
import sqlite3
import io
from io import StringIO
import requests
import json

class HelperService:
    def load_json(self, path: str) -> dict:
        with open(path, 'r') as file:
            return json.load(file)

class DataExtractor:
    def __init__(self, source_info: dict):
        self.source_info = source_info
        self.extracted_data = {}

    def extract(self) -> None:
        os.makedirs(self.source_info['data_dir'], exist_ok=True)
        for source in self.source_info['data_sources']:
            print(f"Fetching data from {source['source_name']}...")
            if "api_endpoint" in source:
                try:
                    response = requests.get(source['api_endpoint'])
                    df = pd.read_csv(io.StringIO(response.text), delimiter=',', encoding='utf-8', on_bad_lines='skip')
                    df.to_csv(os.path.join(self.source_info['data_dir'], source['file_name']), index=False)
                    self.extracted_data[source['source_name']] = df
                except Exception as e:
                    print(f"Error loading data from API endpoint {source['source_name']}: {e}")
            elif "kaggle_dataset" in source:
                try:
                    subprocess.run([
                        'kaggle', 'datasets', 'download',
                        '-d', source['kaggle_dataset'],
                        '--path', self.source_info['data_dir'],
                        '--unzip'
                    ], check=True)
                    df = pd.read_csv(os.path.join(self.source_info['data_dir'], source['file_name']))
                    self.extracted_data[source['source_name']] = df
                except Exception as e:
                    print(f"Error downloading Kaggle dataset {source['source_name']}: {e}")


class DataTransformer:
    def __init__(self, datasets):
        self.datasets = datasets
        self.transformed_data = {}

    def transform(self):
        for name, df in self.datasets.items():
            print(f"Transforming data for {name}...")

            # General cleanup: Drop missing values
            df = df.dropna()

            #if name == 'CrimeData':
                #print("Applying CrimeData-specific transformations...")
                #crime_data = crime_data.dropna()  # Remove rows with missing values
                # Ensure 'date' column is in datetime format
                #df['date'] = pd.to_datetime(df['date'], errors='coerce')
                # Filter rows for the date range 2021-2024
                #df = df[(df['date'] >= '2021-01-01') & (df['date'] <= '2024-12-31')]
                #print("Filtered CrimeData for 2021-2024.")

            if name == 'WeatherData':
                print("Applying WeatherData-specific transformations...")
                #weather_data = weather_data.dropna()  # Remove rows with missing values
                # Fill missing TMAX and TMIN values with their respective medians
                df['tmax'] = df['tmax'].fillna(df['tmax'].median())
                df['tmin'] = df['tmin'].fillna(df['tmin'].median())
                print("Filled missing TMAX and TMIN values.")

            # Save the transformed dataset
            self.transformed_data[name] = df
            print(f"Preview of transformed {name}:")
            print(df.head())


class DataLoader:
    def __init__(self, transformed_data: dict, db_path: str):
        self.transformed_data = transformed_data
        self.db_path = db_path

    def load(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            for name, df in self.transformed_data.items():
                df.to_sql(name, conn, if_exists='replace', index=False)
                print(f"Data for '{name}' saved to database.")

class DataPipeline:
    def __init__(self, config_path: str):
        self.helper_service = HelperService()
        self.source_info = self.helper_service.load_json(config_path)
        self.extractor = DataExtractor(self.source_info)
        self.transformer = DataTransformer(self.extractor.extracted_data)
        self.loader = DataLoader(self.transformer.transformed_data, self.source_info['db_path'])

    def run(self) -> None:
        self.extractor.extract()
        self.transformer.transform()
        self.loader.load()
        print("ETL pipeline execution completed successfully.")

if __name__ == "__main__":
    config_path = "project/source_info.json"  # Adjust this path as necessary
    pipeline = DataPipeline(config_path)
    pipeline.run()