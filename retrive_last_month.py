import requests
import json
import pandas as pd
from datetime import datetime
from retrive import output_file, URL, DATASETS_IDS, API_KEY

def data_retrival(startyear, endyear, series_id, API_KEY):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "seriesid": [series_id],
        "startyear": startyear,
        "endyear": endyear,
        "registrationkey": API_KEY
    })
    response = requests.post(URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data for {series_id}: {response.status_code}")

def dataprocessing_save(start_year, output_file, DATASETS_IDS, API_KEY):
    current_year = datetime.now().year
    current_month = datetime.now().month
    all_data = []
    for name, series_id in DATASETS_IDS.items():
        raw_data = data_retrival(start_year, current_year, {name: series_id}, API_KEY)
        records = raw_data.get("Results", {}).get("series", [])[0].get("data", [])
        if not records:
            print(f"No data found for {name} ({series_id})")
            continue
        
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
    last_month_data = combined_data[combined_data["PERIOD"] == str(current_month).zfill(2)]
    if not last_month_data.empty:
        try:
            with pd.ExcelWriter(output_file, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                last_month_data.to_excel(writer, sheet_name=f"Last_Month", index=False, header=False)
            print(f"Last month's data appended to {output_file}")
        except Exception as e:
            print(f"Error appending data: {e}")
    else:
        print(f"No new data for {current_month}.")
start_date = datetime.now().year
dataprocessing_save(start_date, output_file, DATASETS_IDS, API_KEY)
