from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import dash
import logging
import subprocess
from pathlib import Path
from typing import List

app = dash.Dash(__name__)


def create_plot():
    df_all_years = pd.read_csv("quality_of_life_index_by_country.csv", delimiter=",")
    countries: List[str] = sorted(df_all_years["country"].unique())
    metrics = {
        "quality_of_fife_index": {
            "rank": "(higher is better)",
            "ascending": False,
        },
        "purchasing_power_index": {
            "rank": "(higher is better)",
            "ascending": False,
        },
        "safety_index": {
            "rank": "(higher is better)",
            "ascending": False,
        },
        "health_care_index": {
            "rank": "(higher is better)",
            "ascending": False,
        },
        "cost_of_living_index": {
            "rank": "(lower is better)",
            "ascending": True,
        },
        "property_price_to_income_ratio": {
            "rank": "(lower is better)",
            "ascending": True,
        },
        "climate_index": {
            "rank": "(higher is better)",
            "ascending": False,
        },
        "pollution_index": {
            "rank": "(lower is better)",
            "ascending": True,
        },
        "traffic_commute_time_index": {
            "rank": "(lower is better)",
            "ascending": True,
        },
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
                        value=[
                            "Finland",
                            "Sweden",
                            "Norway",
                            "Denmark",
                            "Netherlands",
                        ],  # Set default values
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
                        value="climate_index",  # Set a default value
                    ),
                ]
            ),
            dcc.Graph(id="metric-graph"),
        ]
    )

    @app.callback(
        Output("metric-graph", "figure"),
        [
            Input("country-dropdown", "value"),
            Input("metric-dropdown", "value"),
        ],
    )
    def update_graph(selected_countries: List[str], selected_metric: str):
        if not selected_countries:
            return go.Figure()

        df_all_years["rank"] = df_all_years.groupby("year")[selected_metric].rank(
            method="min", ascending=metrics[selected_metric]["ascending"]
        )

        filtered_df = df_all_years[df_all_years["country"].isin(selected_countries)]

        filtered_df.sort_values(by=["year", "rank"], inplace=True)

        fig = px.line(
            filtered_df,
            x="year",
            y=selected_metric,
            color="country",
            title=f"{selected_metric} {metrics[selected_metric]['rank']}",
            hover_data={"rank": True, "country": True, selected_metric: True},
            markers=True,
        )

        fig.update_xaxes(dtick="1")  # step 1 year
        fig.update_traces(
            hovertemplate=(
                "year: %{x}<br>"
                f"{selected_metric}: " + "%{y:.2f}<br>"
                "rank: %{customdata[0]}<br>"
                "country: %{customdata[1]}"
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
