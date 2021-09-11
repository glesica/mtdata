from typing import Optional, List

from mtdata.dataset import Dataset, FetchStatus, Row

URL = 'https://www.airnowapi.org/aq/data/'
PARAMS = {
    'parameters': 'PM25',
    'BBOX': '-116.160889,44.298048,-103.416748,49.172497',
    'dataType': 'A',
    'format': 'application/json',
    'verbose': '1',
    'nowcastonly': '0',
    'includerawconcentrations': '0',
    'API_KEY': '40F0E34D-07B2-4DF3-B8B8-8563AD479DE3',
}


class AirQuality(Dataset):
    @property
    def name(self) -> str:
        return 'air_quality'

    def fetch(self, out_path: str) -> Optional[FetchStatus]:
        import json
        import requests
        from os import path

        output_path = path.join(out_path, f'{self.name}.json')

        try:
            with open(output_path, 'r') as data_file:
                old_data: List[Row] = json.load(data_file)
        except FileNotFoundError:
            old_data: List[Row] = []

        resp = requests.get(URL, PARAMS)
        data: List[Row] = resp.json()

        # TODO: These need to be properly spliced / updated
        new_data = old_data + data

        with open(output_path, 'w') as data_file:
            json.dump(new_data, data_file, indent=2, sort_keys=True)

        return FetchStatus(resp.status_code == 200, resp.text)
