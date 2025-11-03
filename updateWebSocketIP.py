
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

publicIP= "XXX.X.X.X"

vco_url = 'https://' + 'vcoXXX.velocloud.net' + '/portal/rest/'


headers = {"Content-Type": "application/json", "Authorization": token}


######## VCO API methods
updateSystemProperty = vco_url+'systemProperty/updateSystemProperty'

params = {
        "id": 471,
        "_update": {
            "name": "network.portal.websocket.address",
            "dataType": "STRING",
            "isPassword": 0,
            "isReadOnly": 0,
            "description": "address of the realtime server for websocket requests from the browser",
            "value": publicIP
        }  
}


response = requests.post(updateSystemProperty, headers=headers, data=json.dumps(params), verify=False)

resp_dict=response.json()

f = open("response.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()


