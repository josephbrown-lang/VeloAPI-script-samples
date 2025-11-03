import ssl
import argparse
import json
import os
import sys
from copy import deepcopy
import requests

########## VCO info and credentials

#Replace XXX with the actual token
token = "Token XXX"

edgeId = (XXX)
enterpriseId = (XXX)

vco_url = 'https://' + 'vcoXXX.velocloud.net' + '/portal/rest/'

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_edgeLinkSeries = vco_url+'metrics/getEdgeLinkSeries'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################
params = {

    "edgeId": edgeId,
    "enterpriseId": enterpriseId,

    "interval":
{
    "start": 1748419509417,
    "end": 1748462709417
}

    }

response = requests.post(get_edgeLinkSeries, headers=headers, data=json.dumps(params), verify=False)

resp_dict=response.json()

f = open("getEdgeLinkSeries.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()


######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict,indent=2))


