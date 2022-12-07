import urllib.request, json, zipfile
import os
from dotenv import load_dotenv
load_dotenv()


try:
    url = "https://apis.metroinfo.co.nz/rti/gtfs/v1/gtfs.zip"

    hdr ={
    # Request headers
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': os.environ.get('metro_api_token'),
    }

    req = urllib.request.Request(url, headers=hdr)

    req.get_method = lambda: 'GET'
    response = urllib.request.urlopen(req)
    print(response.getcode())
    binary_file_path = 'static.zip' 
    with open(binary_file_path, 'wb') as f:
        f.write(response.read())
    zip = zipfile.ZipFile('static.zip')
    zip.extractall('./gtfs_static')
except Exception as e:
    print(e)