from typing import Optional, List, Iterable

from mtdata.dataset import Dataset, FetchResult, Row
from mtdata.transformer import Transformer

# Source front-end display: https://www.arcgis.com/apps/MapSeries/index.html?appid=7c34f3412536439491adcc2103421d4b

_URL = "https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/0/query"

# Some of these params could be cleaned up
_PARAMS = {
    "f": "json",
    "where": "Total <> 0",
    "returnGeometry": "false",
    "spatialRel": "esriSpatialRelIntersects",
    "outFields": "*",
    "outSR": "102100",
    "resultOffset": "0",
    "resultRecordCount": "56",
    "cacheHint": "true",
}


class CovidCounts(Dataset):
    @staticmethod
    def name() -> str:
        return "mt_covid_counts"

    @property
    def dedup_facets(self) -> Iterable[str]:
        return ["county"]

    @property
    def dedup_fields(self) -> Iterable[str]:
        # Only save records that reflect changes in the number of cumulative cases reported for the county
        return [
            "cumulative_cases",
            "new_cases",
            "cumulative_deaths",
            "active_cases",
            "recovered_cases",
        ]

    @property
    def transformer(self) -> Transformer:
        return Transformer(
            [
                ("county", "NAMELABEL"),
                ("county_fips", "ALLFIPS"),
                ("fetch_date", "fetch_date"),
                ("cumulative_cases", "Total"),
                ("new_cases", "NewCases"),
                ("cumulative_deaths", "TotalDeaths"),
                ("active_cases", "TotalActive"),
                ("recovered_cases", "TotalRecovered"),
            ]
        )

    def fetch(self) -> FetchResult:
        import requests
        from datetime import date

        resp = requests.get(_URL, _PARAMS)
        raw = resp.json()

        data: List[Row] = [item["attributes"] for item in raw["features"]]

        for row in data:
            row["fetch_date"] = date.today().strftime("%Y-%m-%d")

        return FetchResult(resp.status_code == 200, resp.text, data)
