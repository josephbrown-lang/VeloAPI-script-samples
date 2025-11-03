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

vco_url = 'https://' + 'vcoXXX.velocloud.net' + '/portal/rest/'

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_EntList = vco_url+'monitoring/getEnterpriseEdgeLinkStatus'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################


params = {

  'links': False

}

response = requests.post(get_EntList, headers=headers, data=json.dumps(params), verify=False)

resp_dict=response.json()

f = open("enterpriseList.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()

######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict,indent=2))

