from typing import Optional, Any, Dict, List

from mtdata.dataset import Dataset, FetchStatus, Row

URL = 'https://apps.missoulacounty.us/dailypublicreport/pinpoints.ashx'


def api_to_json(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'agency': payload['Agency'],
        'cfs_number': payload['CFSNumber'],
        'latitude': payload['Latitude'],
        'longitude': payload['Longitude'],
        'timestamp': payload['Description'].split(' / ')[0].strip(),
        'title': payload['Title'],
    }


class Missoula911(Dataset):
    @property
    def name(self) -> str:
        return 'missoula_911'

    def fetch(self, out_path: str) -> Optional[FetchStatus]:
        from datetime import datetime, timedelta
        import json
        import requests
        from os import path

        start = datetime.today() - timedelta(days=7)
        end = datetime.today()

        params = {
            'startdate': f'{start.month}/{start.day}/{start.year}',
            'enddate': f'{end.month}/{end.day}/{end.year}',
        }

        output_path = path.join(out_path, f'{self.name}.json')

        try:
            with open(output_path, 'r') as data_file:
                old_data: List[Row] = json.load(data_file)
        except FileNotFoundError:
            old_data: List[Row] = []

        resp = requests.get(URL, params)
        data: List[Row] = [api_to_json(p) for p in resp.json()]

        # Find the last old in the current data
        # Take only the current data after that index
        if len(old_data) == 0:
            new_data = data
        else:
            splice = old_data[-1]
            splice_index = 0
            for index in range(len(data)):
                if splice['cfs_number'] == data[index]['cfs_number']:
                    splice_index = index + 1
                    break
            new_data = old_data + data[splice_index:]

        with open(output_path, 'w') as data_file:
            json.dump(new_data, data_file, indent=2, sort_keys=True)

        return FetchStatus(resp.status_code == 200, resp.text)
