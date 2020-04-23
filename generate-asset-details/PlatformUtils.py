import requests
import json
import argparse
import csv
import time
import logging


class Organization:
    token = ""
    org_id=""
    env_list={}
    inv_env_list={}

    def __init__(self,user_name,password,org_id,env_requested):
        logging.info('Organization Data Inititializing.. ')
        self.org_id = org_id
        auth_url = "https://anypoint.mulesoft.com/accounts/login"
        data = {
           "username" : user_name,
           "password" : password
           }
        data_json = json.dumps(data)
        headers = {'Content-type': 'application/json'}
        response = requests.post(auth_url,data=data_json, headers=headers)
        if response.status_code == 200:
            self.token =  response.json()['access_token']
        else:
            logging.error("!! Error: Invalid Credentials")
            quit()
        #initialize environment maps
        url_env =    "https://anypoint.mulesoft.com/apiplatform/repository/v2/organizations/" + self.org_id + "/environments"
    #    print(url)
        headers2 = {'Authorization': "Bearer " + self.token}
    #    print(headers)
        response2 = requests.get(url_env, headers=headers2)

        if response2.status_code == 200:
            response_json=response2.json()
            for environment in response_json:
                self.env_list.update({environment["id"]:environment["name"]})
                self.inv_env_list.update({environment["name"]:environment["id"]})
        else:
            logging.error("!! Insufficient Permissions to Query Environment Details")
            quit()


        if env_requested is not None and self.inv_env_list.get(env_requested,None) is None:
            logging.error("!! Error: Non Existing Environment")
            quit()
        elif env_requested is not None:
            self.env_list = {key:value for key, value in self.env_list.items() if value == env_requested}


#############################################################################################################################
#############################################################################################################################

    @staticmethod
    def flattenjson( b, delim ):
        val = {}
        for i in b.keys():
            if isinstance( b[i], dict ):
                get = Organization.flattenjson( b[i], delim )
                for j in get.keys():
                    val[ i + delim + j ] = get[j]
            else:
                val[i] = b[i]
        return val

#############################################################################################################################
#############################################################################################################################

    def generateRuntimeDetails(self):
        logging.info('Generating Runtime Applications Details for environment' + ' : [' + ','.join(org.env_list.values()) + ']')
        url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"

        service_data = open('RuntimeManagerDetails.csv', 'w')
        csvwriter = csv.writer(service_data)
        keyList=["Environment","Service","Status","URL","Worker Type","Worker Count","Mule Version","Monitoring Enabled","Support End Date"]
        csvwriter.writerow(keyList)

        for env in self.env_list.keys():
            headers = {'Authorization': "Bearer " + self.token,"X-ANYPNT-ENV-ID" : env}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                service_list = response.json()
                for service in service_list:
                    if isinstance( service, dict ):
                        servicenode = Organization.flattenjson(service,"_")
                        currentrecord = [self.env_list[env],servicenode["domain"],servicenode["status"],
                        servicenode["fullDomain"],
                        servicenode["workers_type_cpu"],
                        servicenode["workers_amount"],
                        servicenode["muleVersion_version"],
                        servicenode.get("properties_anypoint.platform.config.analytics.agent.enabled","false"),
                        time.strftime('%Y-%m-%d', time.localtime(servicenode["muleVersion_endOfSupportDate"]/1000))]
                        csvwriter.writerow(currentrecord)
            else:
                logging.error('Insufficient Permissions to Query for RuntimeManagerDetails/Environment :: ' + self.env_list[env])
        service_data.close()
        logging.info("RuntimeManagerDetails sucessfuly created")

#############################################################################################################################
#############################################################################################################################

    def generateAPIManagerDetails(self):
        logging.info('Generating APIManager Details for environment ' + ' : [' + ','.join(org.env_list.values()) + ']')
        api_data = open('APIManagerDetails.csv', 'w')
        csvwriter = csv.writer(api_data)
        keyList=["Environment","API Name","AssetId","Created Date","API Instance Count", "API ID's"]
        csvwriter.writerow(keyList)

        for env in self.env_list.keys():
            headers = {'Authorization': "Bearer " + self.token}
            url = "https://anypoint.mulesoft.com/apimanager/api/v1/organizations/" + self.org_id + "/environments/" + env + "/apis"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                api_list = response.json()["assets"]
                for api in api_list:
                 if isinstance( api, dict ):
                     apinode = Organization.flattenjson(api,"_")
                     id = ""
                     for instance in api["apis"]:
                         id = id + ", " + str(instance["id"]) + ": " + ("" if instance.get("endpointUri") is None else instance.get("endpointUri",""))
                     currentrecord = [self.env_list[env],apinode["exchangeAssetName"],apinode["assetId"],apinode["audit_created_date"],apinode["totalApis"],id[1:]]
                     csvwriter.writerow(currentrecord)
            else:
                logging.error('Insufficient Permissions to Query for APIManagerDetails/Environment :: ' + self.env_list[env])
        api_data.close()
        logging.info("APIManagerDetails sucessfuly created")

#############################################################################################################################
#############################################################################################################################


    def getRoleDetails(self,user):
        logging.info('Getting roles for user ' + user)
        url = "http://anypoint.mulesoft.com/accounts/api/organizations/" + self.org_id + "/users/" + user + "/rolegroups"
        headers = {'Authorization': "Bearer " + self.token}
        userRoles = requests.get(url, headers=headers)

        if userRoles.status_code != 200:
            logging.error('Insufficient Permissions to Query for RoleDetails in OrgId:: ' + self.org_id)
            quit()

        roles = ""
        for role in userRoles.json()["data"]:
            roles = roles + "," + role.get("name")
        return roles


#############################################################################################################################
#############################################################################################################################


    def generateUserDetails(self):
        logging.info('Generating Users and Roles Details.... ')
        url = "http://anypoint.mulesoft.com/accounts/api/organizations/" + self.org_id + "/members"

        headers = {'Authorization': "Bearer " + self.token}
        userDetails = requests.get(url, headers=headers)
        if userDetails.status_code != 200:
            logging.error('Insufficient Permissions to Query for UserDetails in OrgId:: ' + self.org_id)
            quit()

        userDataFile = open('UserDetails.csv', 'w')
        csvwriter = csv.writer(userDataFile)
        keyList=["Name","UserName","Email","ID Provider","Created","Last Logged", "Roles"]
        csvwriter.writerow(keyList)
        for user in userDetails.json()["data"]:
            currentrecord = [
            user.get("firstName","") + " " + user.get("lastName",""),
            user.get("username",""),
            user.get("email",""),
            user.get("idprovider_id",""),
            user.get("createdAt",""),
            user.get("lastLogin",""),
            self.getRoleDetails(user.get("id"))[1:]
            ]
            csvwriter.writerow(currentrecord)

        userDataFile.close()
        logging.info("UserDetails sucessfuly created")


#############################################################################################################################
#############################################################################################################################



parser = argparse.ArgumentParser()
parser.add_argument("--u", required=True, help="username for anypoint platform")
parser.add_argument("--p", required=True, help="password for anypoint platform")
parser.add_argument("--o", required=True, help="Organization Name for anypoint platform")
parser.add_argument("--e", help="Environment Name for anypoint platform")
parser.add_argument("--d", help="Details Requested -- Possible Values, APIManager, RuntimeManager, UserDetails")

args = parser.parse_args()
logging.basicConfig(level=logging.INFO)

#if args.u is None or args.p is None or args.o is None:
#    logging.error("***Username, Password and Organization Required fields")
#    quit()

org = Organization(args.u,args.p,args.o,args.e)
logging.info("Environment List for Organization " + args.o + ' : [' + ','.join(org.inv_env_list.keys()) + ']')

if args.d == 'APIManager':
    org.generateAPIManagerDetails()
elif args.d == 'RuntimeManager':
    org.generateRuntimeDetails()
elif args.d == 'UserDetails':
    org.generateUserDetails()
elif args.d == None:
    org.generateAPIManagerDetails()
    org.generateRuntimeDetails()
    org.generateUserDetails()
else:
    logging.error("Valid Values of -d : APIManager, RuntimeManager, UserDetails")
    quit()
