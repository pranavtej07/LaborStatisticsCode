import streamlit as slt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from retrive import main, CSV_FILE, DATASETS_IDS
import plotly.express as px
import matplotlib.cm as cm
import numpy as np
import plotly.graph_objects as go

slt.set_page_config(layout="wide")

slt.title("US Bureau of Labor Statistics Dashboard")


slt.sidebar.header("Filters")
slt.sidebar.markdown("Use the filters below to select your date range.")

local_timezone = pytz.timezone("America/New_York")

current_date = datetime.now(local_timezone)
max_start_date = current_date - timedelta(days=365)
start_date = slt.sidebar.date_input("Start Date", min_value=datetime(2000, 1, 1), max_value=max_start_date, value=datetime(2023, 1, 1))
end_date = slt.sidebar.date_input("End Date", min_value=datetime(2000, 1, 1), max_value=current_date, value=current_date)
main(start_date, end_date)

if start_date and end_date:
    if slt.sidebar.button('Retrieve'):
         main(start_date, end_date)
    data = pd.read_csv(CSV_FILE)
    data['FOOTNOTES'] = data['FOOTNOTES'].fillna('No footnotes')
    filtered_data = {}
    for key in DATASETS_IDS.keys():
        filtered_series = data[data['SERIES_NAME'] == key]
        filtered_series = filtered_series.sort_values(by='YEAR_MONTH')
        filtered_data[key] = filtered_series 
        
    #ploting the line graph for the civilian_unemployment_rate_data
    civilian_unemployment_rate_data = filtered_data['Unemployment Rate']
    fig_line = px.line(
        civilian_unemployment_rate_data,
        x='YEAR_MONTH',  
        y='VALUE',  
        title='Civilian Unemployment Rate Over Time',
        labels={'YEAR_MONTH': 'Year-Month', 'VALUE': 'Unemployment Rate (%)'},
        template='plotly_white',
        line_shape='linear',  
        color_discrete_sequence=['#FF5733']  
    )
    fig_line.update_layout(
        autosize=True,
        height=600,
        title_font_size=20,
        xaxis_title='Year-Month',
        yaxis_title='Unemployment Rate (%)',
        margin=dict(l=40, r=40, t=50, b=40),
    )
    slt.subheader("Civilian Unemployment Rate Over Time")
    slt.plotly_chart(fig_line, use_container_width=True)       
    
    #ploting the pie chart for the civilian_unemployment_force_data
    civilian_unemployment_force_data = filtered_data['Civilian Unemployment']
    civilian_unemployment_force_data['YEAR'] = civilian_unemployment_force_data['YEAR_MONTH'].str[:4].astype(int)
    yearly_unemployment_data = civilian_unemployment_force_data.groupby('YEAR')['VALUE'].sum().reset_index()
    fig_pie = px.pie(
        yearly_unemployment_data,
        names='YEAR',  
        values='VALUE',  
        title='Civilian Unemployment Distribution by Year',
        color='YEAR',  
        color_discrete_sequence=px.colors.qualitative.Set2  
    )
    slt.subheader("Civilian Unemployment Distribution by Year")
    slt.plotly_chart(fig_pie, use_container_width=True)
    
    #ploting the area graph for the Civilian Labor Force
    civilian_labor_force_data = filtered_data['Civilian Labor Force']
    fig = px.area(civilian_labor_force_data, x='YEAR_MONTH', y='VALUE', title='Civilian Labor Force Over Time', labels={'YEAR_MONTH': 'Date', 'VALUE': 'Value'},template='plotly_white',  
    line_shape='linear')
    fig.update_traces(
        fill='tozeroy',  
        line_color='red', 
        fillcolor='green',
        marker=dict(color=civilian_labor_force_data['VALUE'], colorscale='Plasma')  
    )

    fig.update_layout(autosize=True, height=600, title_font_size=20, xaxis_title='Date', yaxis_title='Labor Force Value',margin=dict(l=20, r=20, t=50, b=20),showlegend=False)
    slt.subheader("Interactive Area Graph: Civilian Labor Force")
    slt.plotly_chart(fig, use_container_width=True)
    
    #ploting the scattered for the Total Nonfarm Employment
    civilian_Nonfarm_force_data = filtered_data['Total Nonfarm Employment']
    civilian_Nonfarm_force_data['YEAR_MONTH'] = pd.to_datetime(civilian_Nonfarm_force_data['YEAR_MONTH'], format='%Y-%m-%d', errors='coerce')
    x = civilian_Nonfarm_force_data['YEAR_MONTH'].apply(lambda date: date.timestamp())  
    y = civilian_Nonfarm_force_data['VALUE']
    norm_x = (x - x.min()) / (x.max() - x.min())
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=civilian_Nonfarm_force_data['YEAR_MONTH'], 
        y=y, 
        mode='markers',
        marker=dict(color='blue', size=8),
        name='Employment Data'
    ))
    fig.add_trace(go.Scatter(
        x=civilian_Nonfarm_force_data['YEAR_MONTH'], 
        y=y, 
        mode='lines',
        line=dict(color='green', width=2, dash='solid'),
        name='Trend Line'
    ))
    fig.update_layout(
        title='Total Nonfarm Employment Over Time',
        xaxis_title='Year-Month',
        yaxis_title='Total Nonfarm Employment',
        template='plotly_white',
        height=600,
        title_font_size=16,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    slt.subheader("Total Nonfarm Employment Over Time with Gradient Green Line")
    slt.plotly_chart(fig, use_container_width=True)
    
    
    #ploting the bar graph graph for the Civilian Employment
    civilian_employment_force_data = filtered_data['Civilian Employment']
    fig = px.bar(
        civilian_employment_force_data,
        x='YEAR_MONTH',
        y='VALUE',
        title='Civilian Employment Over Time',
        labels={'YEAR_MONTH': 'Date', 'VALUE': 'Employment Count'},
        template='plotly_white',  
        color='VALUE',  
        color_continuous_scale='Viridis'  
    )

    fig.update_layout(
        autosize=True,
        height=600,  
        title_font_size=20,
        xaxis_title='Date',
        yaxis_title='Employment Count',
        margin=dict(l=20, r=20, t=50, b=20),
        coloraxis_colorbar=dict(
            title="Employment Count",
            tickvals=[civilian_employment_force_data['VALUE'].min(), civilian_employment_force_data['VALUE'].max()],
            ticktext=["Low", "High"]
        )
    )

    slt.subheader("Interactive Bar Graph: Civilian Employment")
    slt.plotly_chart(fig, use_container_width=True)
    
    
    slt.subheader("Retrevival of the top 12 of each datasets")
    slt.write("Civilian_unemployment_rate_data")
    slt.write(civilian_unemployment_rate_data.head(12))
    
    slt.write("Civilian_unemployment_force_data")
    slt.write(civilian_unemployment_force_data.head(12))
    
    slt.write("Civilian Labor Force")
    slt.write(civilian_labor_force_data.head(12))
    
    slt.write("Total Nonfarm Employment")
    slt.write(civilian_Nonfarm_force_data.head(12))
    
    slt.write("Civilian Employment")
    slt.write(civilian_employment_force_data.head(12))
    

