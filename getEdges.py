import ssl
import argparse
import json
import os
import sys
from copy import deepcopy
import requests

########## VCO info and credentials

#replace XXX with the actual token
token = "Token XXX"


enterpriseId = (XXX)

vco_url = 'https://' + 'vcoXXX.velocloud.net' + '/portal/rest/'

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_entEdges = vco_url+'enterprise/getEnterpriseEdges'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

params = {

    "enterpriseId": enterpriseId,
    'edgeIds':[
     5064
    ],
    'with': [
       'configuration'
            ]
    }

response = requests.post(get_entEdges, headers=headers, data=json.dumps(params), verify=False)

resp_dict=response.json()

f = open("edgeDataExport.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()


######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict,indent=2))


