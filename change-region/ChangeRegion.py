import requests
import json
import argparse
import logging
import sys


class Organization:
    token = ""
    org_id = ""
    service_list=[]


    def __init__(self,client_id,client_secret,org_id,env_requested):
        logging.debug('Environment Data Inititializing.. ')
        self.org_id = org_id
        auth_url = "https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token"
        data = {
           "client_id" : client_id,
           "client_secret" : client_secret,
           "grant_type": "client_credentials"
           }

        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(auth_url,data=data, headers=headers)
        if response.status_code == 200:
            self.token =  response.json()['access_token']
        else:
            logging.error("!! Error: Invalid Credentials")
            quit()


        url_service_details = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"
        headers3 = {"X-ANYPNT-ENV-ID":env_requested, 'Authorization': "Bearer " + self.token}
        response3 = requests.get(url_service_details, headers=headers3)
        if response3.status_code == 200:
            response_json=response3.json()
            for service in response_json:
                self.service_list.append({"domain": str(service.get("domain")),"status":str(service.get("status"))})




#############################################################################################################################
#############################################################################################################################

    def changeRegion(self,new_region,env_requested):
        logging.info("****** Changing Region for all services in Environment to :: " + new_region)
        url_part = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications/"

        headers = {'Authorization': "Bearer " + self.token,
        'X-ANYPNT-ENV-ID': env_requested,
        'X-ANYPNT-ORG-ID': self.org_id
        }



        files = {'name': (None, None, None, None)}


        for service in self.service_list:
            if(service.get("status") == "STARTED"):
                updateResponse = requests.put((url_part + service.get("domain")),headers=headers,data= {'appInfoJson': '{"region":' +  new_region + '}',
                'autoStart': 'true'}, files=files)
            if(service.get("status") == "UNDEPLOYED"):
                updateResponse = requests.put((url_part + service.get("domain")),headers=headers,data= {'appInfoJson': '{"region":' +  new_region + '}',
                'autoStart': 'false'}, files=files)
            if updateResponse.status_code == 200:
                    logging.info("****** Sucessfully Changed region for service :: " + service.get("domain"))
            else:
                    logging.error("****** Update Failed for service :: " + service.get("domain"))
                    logging.error(updateResponse)





######################################################################  ###################################  ###################################
###################################  ###################################  ###################################  ###################################

parser = argparse.ArgumentParser()
parser.add_argument("--c", required=True, help="client_id for connected app with manage settings permission")
parser.add_argument("--s", required=True, help="client_secret for connected app with manage settings permission")
parser.add_argument("--o", required=True, help="Organization id for anypoint platform")
parser.add_argument("--e", help="Environment id for anypoint platform")
parser.add_argument("--r", help="new region")

valid_regions = [
  "us-east-1",
  "us-east-2",
  "us-west-1",
  "us-west-2",
  "ca-central-1",
  "eu-west-1",
  "eu-central-1",
  "eu-west-2",
  "ap-northeast-1",
  "ap-southeast-1",
  "ap-southeast-2",
  "sa-east-1"
]

args = parser.parse_args()
logging.basicConfig(level=logging.INFO)


if args.r not in valid_regions:
    logging.error("Invalid Region Specified. Valid List of regions " + str(valid_regions))
    sys.exit()


org = Organization(args.c,args.s,args.o,args.e)
logging.info("service list List for environment " + json.dumps(org.service_list, indent=2))
logging.info("Total Number of Services in environment:: " + str(len(org.service_list)))

ans = raw_input("Do you want to change their region to " + args.r + " (n) ::")

if ans.lower() not in ('y','yes'):
    logging.info("***** Exiting without any change *****")
else:
    org.changeRegion(args.r,args.e)
