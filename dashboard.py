import streamlit as slt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from retrive import main, CSV_FILE

slt.title("US Bureau of Labor Statistics Dashboard")


slt.sidebar.header("Filters")
slt.sidebar.markdown("Use the filters below to select your date range.")

current_date = datetime.now()
max_start_date = current_date - timedelta(days=365)
start_date = slt.sidebar.date_input("Start Date", min_value=datetime(2000, 1, 1), max_value=max_start_date, value=datetime(2023, 1, 1))
end_date = slt.sidebar.date_input("End Date", min_value=datetime(2000, 1, 1), max_value=current_date, value=current_date)

if start_date and end_date:
    data = pd.read_csv(CSV_FILE)
    slt.write(f"Total records in the dataset: {data.shape[0]}")
    if slt.sidebar.button('Retrieve'):
        main(start_date, end_date)
    grouped_data = data.groupby(['SERIES_NAME', 'YEAR'])['VALUE'].sum().reset_index()
    slt.write("Grouped Data (sum of 'VALUE' per 'SERIES_NAME' and 'YEAR'):")
    for series_name in grouped_data['SERIES_NAME'].unique():
        series_data = grouped_data[grouped_data['SERIES_NAME'] == series_name]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(series_data['YEAR'].astype(str), series_data['VALUE'], marker='o', color='tab:blue', linestyle='-', linewidth=2, markersize=6)
        ax.set_xlabel('Year', fontsize=12, labelpad=10)
        ax.set_ylabel('Total Value', fontsize=12, labelpad=10)
        ax.set_title(f"Total Value for {series_name} by Year", fontsize=14, pad=15)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.set_xticks(series_data['YEAR'].astype(str))  
        plt.tight_layout()
        slt.pyplot(fig)

