import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime
from typing import List


def get_qol_index_by_country_by_year(year: str) -> pd.DataFrame:
    url = f"https://www.numbeo.com/quality-of-life/rankings_by_country.jsp?title={year}"
    response = requests.get(url)

    if response.status_code == 200:
        logging.warning(f"Processing year {year}...")
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "t2"})
        rows = table.find_all("tr")

        data = []
        for row in rows[1:]:
            cells = row.find_all("td")
            row_data = [cell.text.strip() for cell in cells[1:]]  # skip rank
            data.append(row_data)

        # Create a DataFrame using the extracted data
        df = pd.DataFrame(
            data,
            columns=[
                "country",
                "quality_of_fife_index",
                "purchasing_power_index",
                "safety_index",
                "health_care_index",
                "cost_of_living_index",
                "property_price_to_income_ratio",
                "traffic_commute_time_index",
                "pollution_index",
                "climate_index",
            ],
        )

        return df.assign(
            year=year,
            report_date=datetime.today().strftime("%Y-%m-%d"),
        ).reset_index(drop=True)

    else:
        logging.error(
            f"Failed to retrieve the webpage: Status code {response.status_code}"
        )


def get_qol_index_by_country_all_years(years: List) -> None:
    data = []
    for year in years:
        tmp_df = get_qol_index_by_country_by_year(year)
        time.sleep(2)
        data.append(tmp_df)
    df = pd.concat(data)
    df.replace("N/A", pd.NA, inplace=True)
    df.replace("-", 0, inplace=True)
    df.to_csv("quality_of_life_index_by_country.csv", index=False)


if __name__ == "__main__":
    years = [
        2012,
        2013,
        2014,
        2015,
        2016,
        2017,
        2018,
        2019,
        2020,
        2021,
        2022,
        2023,
        2024,
    ]
    get_qol_index_by_country_all_years(years)
