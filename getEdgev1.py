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

enterpriseId = (XXX)

vco_url = 'https://' + 'vcoXXX.velocloud.net' + '/portal/rest/'

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_Edges = vco_url+'edge/getEdge'



######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

params = {
        "id": XXX,
        "enterpriseId": XXX,
        "with": [
            "links",
            "recentLinks",
            "site",
            "serviceGroups",
            "configuration"
        ]
}



response = requests.post(get_Edges, headers=headers, data=json.dumps(params), verify=False)

resp_dict=response.json()

f = open("getEdge.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()


######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict,indent=2))


