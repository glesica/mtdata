from typing import List, Iterable

from mtdata.dataset import Dataset, FetchResult, Row
from mtdata.transformer import Transformer

_URL = "https://www.airnowapi.org/aq/data/"

_PARAMS = {
    "parameters": "PM25",
    "BBOX": "-116.160889,44.298048,-103.416748,49.172497",
    "dataType": "A",
    "format": "application/json",
    "verbose": "1",
    "nowcastonly": "0",
    "includerawconcentrations": "0",
    "API_KEY": "40F0E34D-07B2-4DF3-B8B8-8563AD479DE3",
}


class AirQuality(Dataset):
    """
    Air quality data for Montana.
    """

    @staticmethod
    def name() -> str:
        return "air_quality"

    @property
    def dedup_facets(self) -> Iterable[str]:
        return ["site_name"]

    @property
    def dedup_fields(self) -> Iterable[str]:
        return ["utc_timestamp"]

    @property
    def transformer(self) -> Transformer:
        return Transformer(
            [
                ("aqi", "AQI"),
                ("agency_name", "AgencyName"),
                ("category", "Category"),
                ("full_aqs_code", "FullAQSCode"),
                ("intl_aqs_code", "IntlAQSCode"),
                ("latitude", "Latitude"),
                ("longitude", "Longitude"),
                ("parameter", "Parameter"),
                ("site_name", "SiteName"),
                ("utc_timestamp", "UTC"),
                ("unit", "Unit"),
            ]
        )

    def fetch(self) -> FetchResult:
        import requests

        resp = requests.get(_URL, _PARAMS)
        data: List[Row] = resp.json()

        return FetchResult(resp.status_code == 200, resp.text, data)
