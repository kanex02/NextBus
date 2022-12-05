########### Python 3.2 #############
import urllib.request, json

try:
    url = "https://apis.metroinfo.co.nz/rti/siri/v1/et?routecode=140"

    hdr ={
    # Request headers
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': 'e07580007da54afb8647568c731548bd',
    }

    req = urllib.request.Request(url, headers=hdr)

    req.get_method = lambda: 'GET'
    response = urllib.request.urlopen(req)
    print(response.getcode())
    print(response.read())
except Exception as e:
    print(e)
####################################