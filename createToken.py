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

publicIP= "x.x.x.x"

vco_url = 'https://' + publicIP + '/portal/rest/'


headers = {"Content-Type": "application/json", "Authorization": token}


######## VCO API methods
createToken = vco_url+'network/createApiToken'


params = {
        "name": "UserName",
        "description": "",
        "lifetimeMs": 31536000000,
        "operatorUserId": 2
    }


response = requests.post(createToken, headers=headers, data=json.dumps(params), verify=False)

resp_dict=response.json()

f = open("responseTokenCreate.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()


