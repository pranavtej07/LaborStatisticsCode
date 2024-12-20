import pandas as pd
import json
from datetime import datetime
import requests as re
import os

API_KEY = "93ee8e3a1d66428298ca51eceb0fca71"
URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

DATASETS_IDS = {
    "Civilian Labor Force" : "LNS11000000",
    "Civilian Employment" : "LNS12000000",
    "Civilian Unemployment" : "LNS13000000",
    "Unemployment Rate" : "LNS14000000",
    "Total Nonfarm Employment" : "CES0000000001"
}
print(DATASETS_IDS.keys())

def data_retrival(startyear, endyear, DATASETS_IDS, API_KEY):
    headers = {"Content-Type": "application/json"}
    for value in DATASETS_IDS.values():
        data = json.dumps({"seriesid": [value],"startyear":startyear, "endyear":endyear, "registrationkey": API_KEY})
    response = re.post(URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data for {DATASETS_IDS.keys()}: {response.status_code}")


def dataprocessing_save(start_year, end_year, output_file, DATASETS_IDS, API_KEY):   
    all_data = []
    for name, series_id in DATASETS_IDS.items():
        raw_data = data_retrival(start_year, end_year, {name: series_id}, API_KEY)
        records = raw_data.get("Results", {}).get("series", [])[0].get("data", [])
        df = pd.DataFrame(records)
        df["SERIES_NAME"] = name
        df["SERIES_ID"] = series_id
        df["YEAR"] = df["year"]
        df["PERIOD"] = df["period"]
        df["PERIODNAME"] = df["periodName"]
        df["VALUE"] = pd.to_numeric(df["value"], errors="coerce")
        df["FOOTNOTES"] = df["footnotes"]
        df = df[["SERIES_NAME", "YEAR", "PERIOD", "PERIODNAME", "VALUE", "FOOTNOTES", "SERIES_ID"]]
        all_data.append(df)

    combined_data = pd.concat(all_data, ignore_index=True)
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for year in combined_data["YEAR"].unique():
            year_data = combined_data[combined_data["YEAR"] == year]
            year_data.to_excel(writer, sheet_name=f"Year_{year}", index=False)
            
CSV_FILE = "data/Retrived_data.csv"
output_file = "data/Retrived_data.xlsx"          
def main(start_year, end_year):
    start_year =start_year.year
    end_year = end_year.year
    dataprocessing_save(start_year, end_year, output_file, DATASETS_IDS, API_KEY)
    data = pd.read_excel(output_file, sheet_name=None)
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    df_combined = pd.concat(data.values(), ignore_index=True)
    df_combined["YEAR_MONTH"] = df_combined["YEAR"].astype(str) + "-" + df_combined["PERIOD"].str[1:]
    df_combined["YEAR_MONTH"] = pd.to_datetime(df_combined["YEAR_MONTH"], format="%Y-%m")
    df_cleaned = df_combined.dropna(subset=["VALUE", "SERIES_NAME"])
    df_cleaned['YEAR'] = df_cleaned['YEAR_MONTH'].dt.year
    df_cleaned.to_csv(CSV_FILE, index=False)
    
