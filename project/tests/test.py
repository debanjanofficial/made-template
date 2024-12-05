import os
import pandas as pd
from pipeline import fetch_data, transform_data, save_data, run_pipeline, DATA_DIR

# Mocked data for unit tests
MOCK_CRIME_DATA = pd.DataFrame({
    "Date": ["2023-01-01", "2022-12-31", "2021-07-15", "2024-11-10"],
    "Primary Type": ["THEFT", "BATTERY", "BURGLARY", "ROBBERY"],
    "Description": ["OVER $500", "SIMPLE", "FORCED ENTRY", "ARMED"],
    "Location Description": ["STREET", "RESIDENCE", "APARTMENT", "SIDEWALK"]
})

MOCK_WEATHER_DATA = pd.DataFrame({
    "time": ["2022-01", "2022-02", "2022-03"],
    "tavg": [30.2, 31.1, 42.5],
    "tmin": [20.0, 19.1, 30.0],
    "tmax": [40.1, 43.5, 50.0]
})


def test_fetch_data(monkeypatch):
    # Mock data sources
    def mock_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, text):
                self.text = text
            def json(self):
                return self.text
        if "chicago" in args[0]:
            return MockResponse("Date,Primary Type,Description,Location Description\n" + 
                                "2023-01-01,THEFT,OVER $500,STREET\n2022-12-31,BATTERY,SIMPLE,RESIDENCE\n")
        elif "meteostat" in args[0]:
            return MockResponse("time,tavg,tmin,tmax\n2022-01,30.2,20.0,40.1\n")
        return MockResponse("")
    monkeypatch.setattr("requests.get", mock_requests_get)

    datasets = fetch_data()
    assert "Chicago Data Portal" in datasets
    assert not datasets["Chicago Data Portal"].empty
    assert "Meteostat" in datasets
    assert not datasets["Meteostat"].empty


def test_transform_data():
    datasets = {"Chicago Data Portal": MOCK_CRIME_DATA, "Meteostat": MOCK_WEATHER_DATA}
    transformed = transform_data(datasets)
    assert "Chicago Data Portal" in transformed
    assert transformed["Chicago Data Portal"].shape[0] == 4
    assert "Meteostat" in transformed
    assert not transformed["Meteostat"].isnull().values.any()


def test_save_data(tmpdir):
    temp_dir = tmpdir.mkdir("data")
    datasets = {"Chicago Data Portal": MOCK_CRIME_DATA}
    save_data(datasets)
    output_file = os.path.join(DATA_DIR, "Chicago Data Portal.sqlite")
    assert os.path.exists(output_file)


def test_pipeline_end_to_end():
    run_pipeline()
    output_file = os.path.join(DATA_DIR, "Chicago Data Portal.sqlite")
    assert os.path.exists(output_file)
    weather_file = os.path.join(DATA_DIR, "Meteostat.sqlite")
    assert os.path.exists(weather_file)
