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


#enterpriseId = (XXX)

vco_url = 'https://' + 'vcoXXX.velocloud.net' + '/portal/rest/'

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods

get_ent_list_status = vco_url + 'monitoring/getEnterpriseEdgeLinkStatus'


params_ent_list = {'links': True, 'detailed': True}

response_ent_list = requests.post(get_ent_list_status, headers=headers, data=json.dumps(params_ent_list), verify=False)


resp_dict=response_ent_list.json()

f = open("getEnterpriseLinkStatus.txt", "w")
f.write(json.dumps(resp_dict,indent=2))
f.close()

