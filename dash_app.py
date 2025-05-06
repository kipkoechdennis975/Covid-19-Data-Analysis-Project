import dash
from dash import dcc, html, Input, Output, Dash
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_csv("owid-covid-data.csv", parse_dates=["date"])

# Initialize Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("COVID-19 Interactive Dashboard", style={'textAlign': 'center'}),
    
    # Country dropdown
    html.Div([
        html.Label("Select Countries"),
        dcc.Dropdown(
            id="country-dropdown",
            options=[{"label": c, "value": c} for c in sorted(df["location"].unique())],
            value=["United States", "India"],
            multi=True,
            style={'width': '100%'}
        )
    ], style={'padding': '20px'}),
    
    # Date range picker
    html.Div([
        html.Label("Select Date Range"),
        dcc.DatePickerRange(
            id="date-range",
            min_date_allowed=df["date"].min(),
            max_date_allowed=df["date"].max(),
            start_date=df["date"].min(),
            end_date=df["date"].max(),
            display_format='YYYY-MM-DD'
        )
    ], style={'padding': '20px'}),
    
    # Cases graph
    dcc.Graph(id="cases-graph"),
    
    # Deaths graph
    dcc.Graph(id="deaths-graph"),
    
    # Vaccination graph (if data exists)
    dcc.Graph(id="vaccination-graph")
])

# Callback for updating graphs
@app.callback(
    [Output("cases-graph", "figure"),
     Output("deaths-graph", "figure"),
     Output("vaccination-graph", "figure")],
    [Input("country-dropdown", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date")]
)
def update_graphs(selected_countries, start_date, end_date):
    if not selected_countries:
        return px.line(), px.line(), px.line()
    
    filtered_df = df[
        (df["location"].isin(selected_countries)) &
        (df["date"] >= start_date) &
        (df["date"] <= end_date)
    ]
    
    # Cases plot
    cases_fig = px.line(
        filtered_df,
        x="date",
        y="total_cases",
        color="location",
        title="Total Cases Over Time",
        labels={"total_cases": "Total Cases", "date": "Date"}
    )
    
    # Deaths plot
    deaths_fig = px.line(
        filtered_df,
        x="date",
        y="total_deaths",
        color="location",
        title="Total Deaths Over Time",
        labels={"total_deaths": "Total Deaths", "date": "Date"}
    )
    
    # Vaccination plot (if column exists)
    if 'people_vaccinated_per_hundred' in df.columns:
        vaccination_fig = px.line(
            filtered_df,
            x="date",
            y="people_vaccinated_per_hundred",
            color="location",
            title="Vaccination Progress (% Population)",
            labels={"people_vaccinated_per_hundred": "% Vaccinated", "date": "Date"}
        )
    else:
        vaccination_fig = px.line(title="Vaccination Data Not Available")
    
    return cases_fig, deaths_fig, vaccination_fig

if __name__ == "__main__":
    app.run(debug=True)  # Changed from app.run_server()