from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import dash
import logging
import subprocess
from pathlib import Path

app = dash.Dash(__name__)


def create_plot():
    df_all_years = pd.read_csv("quality_of_life_index_by_country.csv", index_col=0)
    countries = sorted(df_all_years["Country"].unique())
    metrics = [
        "Purchasing Power Index",
        "Safety Index",
        "Health Care Index",
        "Cost of Living Index",
        "Property Price to Income Ratio",
        "Traffic Commute Time Index",
        "Pollution Index",
        "Climate Index",
    ]

    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Label("Select Countries:"),
                    dcc.Dropdown(
                        id="country-dropdown",
                        options=[
                            {"label": country, "value": country}
                            for country in countries
                        ],
                        value=["United States"],  # Set default value(s)
                        multi=True,  # Allow multiple selections
                    ),
                ]
            ),
            html.Div(
                [
                    html.Label("Select Metric:"),
                    dcc.Dropdown(
                        id="metric-dropdown",
                        options=[
                            {"label": metric, "value": metric} for metric in metrics
                        ],
                        value="Purchasing Power Index",  # Set a default value
                    ),
                ]
            ),
            dcc.Graph(id="metric-graph"),
        ]
    )

    @app.callback(
        Output("metric-graph", "figure"),
        [Input("country-dropdown", "value"), Input("metric-dropdown", "value")],
    )
    def update_graph(selected_countries, selected_metric):
        if not selected_countries:
            # If no countries are selected, display an empty figure
            return go.Figure()

        # Filter the DataFrame for the selected countries
        filtered_df = df_all_years[df_all_years["Country"].isin(selected_countries)]

        # Sort the DataFrame based on the selected metric and Year to ensure that
        # the lines are correctly ordered in the graph
        filtered_df = filtered_df.sort_values(
            by=["Year", selected_metric], ascending=[True, False]
        )

        # Create a line chart using Plotly Express
        fig = px.line(
            filtered_df,
            x="Year",
            y=selected_metric,
            color="Country",  # Differentiate lines by country
            title=f"{selected_metric} Over Time",
            labels={"Country": "Country"},
            category_orders={"Country": list(filtered_df["Country"].unique())},
            hover_data={"rank": True, selected_metric: True},
        )

        # Update hover template to display year, metric value, and rank
        fig.update_traces(
            hovertemplate=(
                "Year: %{x}<br>"
                f"{selected_metric}: " + "%{y:.2f}<br>"
                "Rank: %{customdata[0]}<extra></extra>"
            )
        )
        return fig


if __name__ == "__main__":

    csv_file_path = Path(__file__).parent / "quality_of_life_index_by_country.csv"
    script_path = Path(__file__).parent / "quality_of_life_index_by_country.py"

    # checks if the csv file exists, if not, runs the script to create it
    if not csv_file_path.is_file():
        logging.warning(f"{csv_file_path.name} not found.\nCollecting data...")
        subprocess.run(["python", script_path], check=True)

    create_plot()
    app.run_server(debug=True)
