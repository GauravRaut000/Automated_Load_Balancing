#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# pip install jupyter-dash
import dash
import plotly.express as px
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import plotly.graph_objs as go
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import heapq
import os

# Load Data
data = pd.read_csv (r'dataset/final_forecast_2021.csv',header=0,skiprows=[1])

df=data.iloc[-25:]

df.reset_index(drop=True,inplace=True)
df["Time [hour]"] = pd.DataFrame({"Time [hour]":np.arange(1,25)})


# define flexible range
def flexRange(start=0,stop=23):
    signal = pd.DataFrame(np.zeros((24, 1)),columns=["userinput"])
    #print(stop-start)
    if (stop-start) >= 2:
        signal.loc[start:stop,'userinput']=1
        return(signal)
    else:
        signal.loc[0:23,'userinput']=1
        return(signal)

# Build App

#app = JupyterDash(__name__)
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    
    html.H1("Automated Load Balancing System",style={"color":"blue","text-align":"center"}),
             
    dcc.Graph(id='time_load',
          
              figure=px.line(df,
                         x='Time [hour]',
                         y='Load [MWh]',
                         title='Load on Electricity Grid for 31.10.2021(Spain)',
                         width=1500,
                         height=600,
                         template='plotly_dark',
                         labels={
                         "Time [hour]": "Time [hour]",
                         "Load [MWh]": "Grid Load [MWh]"
                                 },   
                            )
             ),
    
    html.Br(),
    dcc.Graph(id='time_price',
          
              figure=px.line(df,
                         x='Time [hour]',
                         y='Price [Euro/kWh]',
                         title='Day ahead price of electricity for 31.10.2021 (Spain)',
                         width=1500,
                         height=600,
                         template='plotly_dark',
                         labels={
                         "Time [hour]": "Time [hour]",
                         "Price [Euro/kWh]": "Price [Euro/kWh]"
                                 },
                            )
             ),

    html.Br(), 
    
    html.H1("Signals to shift the demand for the next day's 3 hours block for Wood grinding machine",style={"color":"blue","text-align":"center"}),
         
    html.Div(id='slider-output-container1'),           
    
    html.I("Please select value between 1 and 24 for automatic control"),
    html.Br(),
    dcc.Input(id="input1", type="number", placeholder="",value='1',min="1",max="24" ),
    dcc.Input(id="input2", type="number", placeholder="",value='24',min="1",max="24"),
    html.Div(id="output1"),
        
    dcc.Graph(id='comp1_on', figure={}),
    
    html.Br(),
    html.Div(id='slider-output-container2'),
    html.I("Please select value between 1 and 24 for automatic control"),
    html.Br(),
    dcc.Input(id="input3", type="number", placeholder="",value='1',min="1",max="24" ),
    dcc.Input(id="input4", type="number", placeholder="",value='24',min="1",max="24"),
    html.Div(id="output2"),
    
    dcc.Graph(id='comp1_off',figure={}),
    
    
    
    html.Br(),
    html.H1("Forecasting of Load and Price from January_2021 to October_2021",style={"color":"blue","text-align":"center"}),
    dcc.Graph(id='forecast_load',
          
              figure=px.line(data,
                         x='Time [hour]',
                         y='Load [MWh]',
                         title='Electricity load forecast from January_2021 to October_2021 (Spain)',
                         width=1500,
                         height=600,
                         template='plotly_dark',
                         labels={
                         "Time [hour]": "Time [hour]",
                         "Price [Euro/kWh]": "Load [MWh]"
                                 },
                            )
              
             ),
    
    html.Br(),
    
    dcc.Graph(id='forecast_price',
          
              figure=px.line(data,
                         x='Time [hour]',
                         y='Price [Euro/kWh]',
                         title='Electricity price forecast from January_2021 to October_2021 (Spain)',
                         width=1500,
                         height=600,
                         template='plotly_dark',
                         labels={
                         "Time [hour]": "Time [hour]",
                         "Price [Euro/kWh]": "Price [Euro/kWh]"
                                 },
                            )
             ),
    
    
])

@app.callback([Output("comp1_on", "figure"),
              Output("comp1_off", "figure")],
    Input("input1", "value"),
    Input("input2", "value"),
    Input("input3", "value"),
    Input("input4", "value"),
            )

def update_figure1(input1, input2,input3, input4):
    df2=df.copy()
  
    input1_int=int(input1)
    input2_int=int(input2)
    ON_signal = flexRange(input1_int-1,input2_int-1)
    ON_signal=ON_signal.rename(columns={"userinput":"EV_charging_points_1_to_5_ON"})
    price=df2["Price [Euro/kWh]"]
    price=price.multiply(ON_signal['EV_charging_points_1_to_5_ON'], axis=0)
    price=price.replace(0.0, 100000)

    minindex=[i
             for x, i
             in heapq.nsmallest(
                 3,
                 ((x, i) for i, x in enumerate(price)))]
    #print(minindex)
    
    ON_signal_zero = pd.DataFrame(np.zeros((24, 1)),columns=["EV_charging_points_1_to_5_ON"])
    ON_signal_zero.iloc[minindex[0]]['EV_charging_points_1_to_5_ON'] = 1
    ON_signal_zero.iloc[minindex[1]]['EV_charging_points_1_to_5_ON'] = 1
    ON_signal_zero.iloc[minindex[2]]['EV_charging_points_1_to_5_ON'] = 1
    EV_charging_points_1_to_5_ON=ON_signal_zero
    df2=pd.concat([df2,EV_charging_points_1_to_5_ON], axis=1)
    time = pd.DataFrame(df2,columns=["Time [hour]"])
    df3=pd.concat([time,EV_charging_points_1_to_5_ON], axis=1)    
    figure=px.line(df3, x='Time [hour]',
                         y='EV_charging_points_1_to_5_ON',
                         title='Signal to turn ON the Wood Grinding Machine',
                         width=1500,
                         height=300,
                         template='plotly_dark',
                         labels={
                         "Time [hour]": "Time [hour]",
                         "EV_charging_points_1_to_5_ON": "Signal for automatic control"
                                 },
                      )
   
    df4=df.copy()
    input3_int=int(input3)
    input4_int=int(input4)
    OFF_signal = flexRange(input3_int-1,input4_int-1)
    OFF_signal=OFF_signal.rename(columns={"userinput":"EV_charging_points_1_to_5_ON"})
    
    load=df4["Load [MWh]"]
    load=load.multiply(OFF_signal['EV_charging_points_1_to_5_ON'], axis=0)
    #load=load.replace(0.0, 100000)
    maxindex=[i
             for x, i
             in heapq.nlargest(
                 3,
                 ((x, i) for i, x in enumerate(load)))]       
    
    OFF_signal_zero = pd.DataFrame(np.zeros((24, 1)),columns=["EV_charging_points_1_to_5_OFF"])
    OFF_signal_zero.iloc[maxindex[0]]['EV_charging_points_1_to_5_OFF'] = 1
    OFF_signal_zero.iloc[maxindex[1]]['EV_charging_points_1_to_5_OFF'] = 1
    OFF_signal_zero.iloc[maxindex[2]]['EV_charging_points_1_to_5_OFF'] = 1
    EV_charging_points_1_to_5_OFF=OFF_signal_zero  
    df4=pd.concat([df4,EV_charging_points_1_to_5_OFF], axis=1)
    time1 = pd.DataFrame(df4,columns=["Time [hour]"])
    df5=pd.concat([time1,EV_charging_points_1_to_5_OFF], axis=1)
    
    figure1=px.line(df5,x='Time [hour]',
                         y='EV_charging_points_1_to_5_OFF',
                         title='Signal to turn OFF the Wood Grinding Machine',
                         width=1500,
                         height=300,
                         template='plotly_dark',
                         labels={
                         "Time [hour]": "Time [hour]",
                         "EV_charging_points_1_to_5_OFF": "Signal for automatic control"
                                 },
                      )    
    
    return figure,figure1

# Run app and display result inline in the notebook
#app.run_server(mode='inline')

if __name__ == '__main__':
    app.run_server(debug=True)

