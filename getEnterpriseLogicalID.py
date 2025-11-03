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
get_Enterprise = vco_url+'enterprise/getEnterprise'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################
params = {

    "enterpriseId": enterpriseId,
    }

response = requests.post(get_Enterprise, headers=headers, data=json.dumps(params), verify=False)

resp_dict=response.json()

entLogicalId=resp_dict["logicalId"]

print("The Enterprise Logical ID for Enterprise ID of", enterpriseId, "is", entLogicalId)

f = open("enterpriseLogicalID.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()


######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict,indent=2))


