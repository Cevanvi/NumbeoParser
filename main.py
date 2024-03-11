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
    metrics = {
        "Purchasing Power Index": "(higher is better)",
        "Safety Index": "(higher is better)",
        "Health Care Index": "(higher is better)",
        "Climate Index": "(higher is better)",
        "Pollution Index": "(lower is better)",
        "House Price to Income Ratio": "(lower is better)",
        "Cost of Living Index": "(lower is better)",
        "Traffic Commute Time Index": "(lower is better)",
    }

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
                        value=["Finland"],  # Set default value(s)
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
                            {"label": metric, "value": metric}
                            for metric in metrics.keys()
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
            return go.Figure()

        filtered_df = df_all_years[df_all_years["Country"].isin(selected_countries)]

        filtered_df = filtered_df.sort_values(
            by=["Year"],
            ascending=[
                True,
            ],
        )

        fig = px.line(
            filtered_df,
            x="Year",
            y=selected_metric,
            color="Country",
            title=f"{selected_metric} {metrics[selected_metric]}",
            labels={"Country": "Country"},
            hover_data={
                selected_metric: True,
            },
        )
        fig.update_traces(
            hovertemplate=("Year: %{x}<br>" f"{selected_metric}: " + "%{y:.2f}<br>")
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
