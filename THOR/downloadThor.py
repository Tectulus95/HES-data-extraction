import configparser
import os
from urllib3.exceptions import HttpError

import requests

dirname = os.path.dirname(__file__)
configloc = os.path.join(dirname, 'config.ini')
filename = os.path.join(dirname, 'thor_data_vietnam.csv')

url = "https://api.data.world/v0/file_download/datamil/vietnam-war-thor-data/thor_data_vietnam.csv"

config = configparser.ConfigParser()
config.read(configloc)

auth = "Bearer " + config['dataworld']['token']

headers = {
    "accept": "*/*",
    "authorization": auth
}

def download_thor():
    response = requests.get(url, headers=headers, stream=True)
    print(response.headers)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=2048):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    print(f"{(downloaded)/1024:.2f}MB", end='\r')
    else:
        raise HttpError(response.status_code)

def main():
    download_thor()

if __name__ == "__main__":
    main()