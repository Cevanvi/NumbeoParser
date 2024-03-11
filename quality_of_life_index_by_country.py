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
        headers = [header.text.strip() for header in rows[0].find_all("th")]

        data = []
        for row in rows[1:]:
            cells = row.find_all("td")
            row_data = [cell.text.strip() for cell in cells]
            data.append(row_data)

        # Create a DataFrame using the extracted data
        df = pd.DataFrame(data, columns=headers)

        return (
            df.assign(
                Year=year,
                report_date=datetime.today().strftime("%Y-%m-%d"),
                rank=df.index + 1,
            )
            .reset_index(drop=True)
            .drop("Rank", axis=1)
        )

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
    df = pd.concat(data, ignore_index=True)
    df.to_csv("quality_of_life_index_by_country.csv")


if __name__ == "__main__":

    # Execute only when need to generate the new CSV file
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
