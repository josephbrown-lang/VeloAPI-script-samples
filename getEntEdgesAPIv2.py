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

enterpriseLogicalID = "XXX"

vco_url = 'https://' + 'vcoXXX.velocloud.net' + '/api/sdwan/v2/'

headers = {"Content-Type": "application/json", "Authorization": token}


######## VCO API methods

get_entEdges = vco_url+'enterprises/'+ enterpriseLogicalID+ '/edges?include=site.*'


######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

response = requests.get(get_entEdges, headers=headers)

resp_dict=response.json()

f = open("edgeData.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()



######## Debugging

#respData=resp_dict["data"][5]
#respSite=respData["site"]

#print(respSite)

#print(get_entEdges)