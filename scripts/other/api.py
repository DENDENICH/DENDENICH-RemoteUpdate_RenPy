from urllib3 import PoolManager
import json

URL = 'https://cloud-api.yandex.net/v1/disk/resources/download'
TOKEN = 'y0_AgAAAABjYJz5AADLWwAAAAEcaCO9AABn_2laLfpDPYQrZGeUXXLXBiDimg'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'OAuth {TOKEN}'
}

http = PoolManager()

def get_download_href(
        url: str
):
    try:
        response = http.request('GET', url, headers=headers)
        if response.status == 200:
            data = response.data.decode('utf-8')
            json_data = json.loads(data)
            href = json_data['href']
            return href
        else:
            print(f'Error: {response.status} - {response.reason}')
            return None
    except Exception as e:
        print(f'Error: {e}')
        return None

def download(
        url: str,
):
    """"""
    response = http.request('GET', url, headers=headers)
    if response.status == 200:
        data = response.data.decode()
        return data


download_url = get_download_href(
    url=f'{URL}?path=/game/version.txt'
)

file = download(url=download_url)
print(file)