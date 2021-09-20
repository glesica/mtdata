from typing import List, Iterable

from mtdata.dataset import Dataset, FetchResult, Row
from mtdata.transformer import Transformer

_URL = "https://apps.missoulacounty.us/dailypublicreport/pinpoints.ashx"

_transformer = Transformer()


class Missoula911(Dataset):
    """
    Record of 911 events for Missoula city and county in Montana.
    """

    @property
    def dedup_facets(self) -> Iterable[str]:
        return []

    @property
    def dedup_fields(self) -> Iterable[str]:
        return ["cfs_number"]

    @property
    def transformer(self) -> Transformer:
        return Transformer(
            [
                ("agency", "Agency"),
                ("cfs_number", "CFSNumber"),
                ("latitude", "Latitude"),
                ("longitude", "Longitude"),
                ("timestamp", "Description", lambda x: x.split(" / ")[0].strip()),
                ("title", "Title"),
            ]
        )

    @staticmethod
    def name() -> str:
        return "missoula_911"

    def fetch(self) -> FetchResult:
        from datetime import datetime, timedelta
        import requests

        start = datetime.today() - timedelta(days=7)
        end = datetime.today()
        params = {
            "startdate": f"{start.month}/{start.day}/{start.year}",
            "enddate": f"{end.month}/{end.day}/{end.year}",
        }

        resp = requests.get(_URL, params)
        data: List[Row] = resp.json()

        return FetchResult(resp.status_code == 200, resp.text, data)
