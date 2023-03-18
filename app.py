import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import requests

url1 = 'https://github.com/mehdi-naji/IHBS_dash/raw/main/data/HH_decile_expenditure.csv'
url2 = 'https://github.com/mehdi-naji/IHBS_dash/raw/main/data/HH_decile_shares.csv'

response1 = requests.get(url1)
with open('HH_decile_expenditure.csv', 'wb') as f:
    f.write(response1.content)
# read the CSV file into a DataFrame
df1 = pd.read_csv('HH_decile_expenditure.csv')


response2 = requests.get(url2)
with open('HH_decile_shares.csv', 'w', encoding="utf-8") as f:
    f.write(response2.text)

# read the CSV file into a DataFrame
df2 = pd.read_csv('HH_decile_shares.csv')

# Define the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container([
    html.H1("An Introduction to Iran Household Expenditure and Income Surveys"),
    dcc.Tabs([
        dcc.Tab(label='Intratemporal Facts', children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Choose a year"),
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=[{'label': year, 'value': year} for year in df1['year'].unique()],
                        value=df1['year'].max()
                    ),
                    html.Br(),
                    html.H4("Bar plot of expenditure by category for the chosen year"),
                    dcc.Graph(id='intratemporal-bar')
                ]),
                dbc.Col([
                    html.H4("Treemap of expenditure by category for the chosen year"),
                    dcc.Graph(id='intratemporal-treemap')
                ])
            ])
        ]),
        dcc.Tab(label='Intertemporal Facts', children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Choose an expenditure category"),
                    dcc.Dropdown(
                        id='category-dropdown',
                        options=[{'label': category, 'value': category} for category in df2['variable'].unique()],
                        value=df2['variable'].iloc[0]
                    ),
                    html.Br(),
                    html.H3("Choose a decile"),
                    dcc.Dropdown(
                        id='decile-dropdown',
                        options=[{'label': decile, 'value': decile} for decile in df2['decile'].unique()],
                        value=df2['decile'].iloc[0]
                    ),
                    html.Br(),
                    html.H4("Bar plot of expenditure for the chosen category and decile"),
                    dcc.Graph(id='intertemporal-bar')
                ])
            ])
        ])
    ])
], fluid=True)

# Define the callbacks
@app.callback(
    [dash.dependencies.Output('intratemporal-bar', 'figure'),
     dash.dependencies.Output('intratemporal-treemap', 'figure')],
    [dash.dependencies.Input('year-dropdown', 'value')]
)
def update_intratemporal_plots(selected_year):
    filtered_df = df1[df1['year'] == selected_year]
    bar_fig = px.bar(filtered_df, x='decile', y='value', color='variable', title=f"Expenditure by category for {selected_year}")
    treemap_fig = px.treemap(filtered_df, path=['decile', 'variable'], values='value', title=f"Expenditure by category for {selected_year}")

    return bar_fig, treemap_fig

@app.callback(
    dash.dependencies.Output('intertemporal-bar', 'figure'),
    [dash.dependencies.Input('category-dropdown', 'value'),
     dash.dependencies.Input('decile-dropdown', 'value')]
)
def update_intertemporal_plot(selected_category, selected_decile):
    filtered_df = df2[(df2['variable'] == selected_category) & (df2['decile'] == selected_decile)]
    bar_fig = px.bar(filtered_df, x='year', y='value', title=f"Expenditure for {selected_category} (decile {selected_decile}) over time")
    return bar_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)