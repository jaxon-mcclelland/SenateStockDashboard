import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
from getSenatorData import getSenatorData

global reportDF 
reportDF = getSenatorData('https://efdsearch.senate.gov').report

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in reportDF.columns],
    data=reportDF.to_dict('records'),
)


if __name__ == '__main__':

    app.run_server(debug=True)