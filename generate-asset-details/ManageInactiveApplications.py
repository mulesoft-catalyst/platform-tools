import requests
import json
import argparse
import csv
import time
import logging
import os
from time import gmtime, strftime
from datetime import datetime, timedelta



class Organization:
    token = ""
    org_id=""
    env_list=[]
    org_hierarchy=[]

    def __init__(self,user_name,password,org_id):
        logging.info('Organization Data Inititializing.. ')
        self.org_id = org_id
        self.getAuthToken(user_name,password)


        #org_details
        url_hierarchy = "https://anypoint.mulesoft.com/accounts/api/organizations/" + self.org_id + "/hierarchy"
        headers2 = {'Authorization': "Bearer " + self.token}
        response2 =  requests.get(url_hierarchy, headers=headers2)
        if response2.status_code == 200:
            response_json=response2.json()
            self.org_hierarchy.append({"org_name":response_json.get("name"), "org_id": response_json.get("id")})
            for subOrganizations in response_json["subOrganizations"]:
                self.org_hierarchy.append({"org_name":subOrganizations.get("name"), "org_id": subOrganizations.get("id")})
        else:
            logging.error("!! Insufficient Permissions to Query Hierarchy Details")
            quit()



        for org in self.org_hierarchy:
            url_env =    "https://anypoint.mulesoft.com/apiplatform/repository/v2/organizations/" + org["org_id"] + "/environments"
            headers2 = {'Authorization': "Bearer " + self.token}
            response2 = requests.get(url_env, headers=headers2)
            if response2.status_code == 200:
                response_json=response2.json()
                for environment in response_json:
                    self.env_list.append({"env_id":environment["id"], "env_name": environment["name"], "org_name": org["org_name"], "org_id": org["org_id"]})
            else:
                logging.error("!! Insufficient Permissions to Query Environment Details")
                quit()



    #############################################################################################################################
    #############################################################################################################################

    def getAuthToken(self,user_name,password):
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

    def generateCHRuntimeDetails(self,requestedTimeSinceLastTraffic,interactive, fileOutput):

        if fileOutput != None:
            inactive_app_data_file = open(fileOutput, 'w')
            csvwriter = csv.writer(inactive_app_data_file)
            keyList=["Organization","Environment","Service","Time (Hours) Elapsed Since Last Event"]
            csvwriter.writerow(keyList)


        url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications"


        for env in self.env_list:
            #logging.info("Generating Details for org, env: " + env.get("org_name") + ":" + env["env_name"])
            headers = {'Authorization': "Bearer " + self.token,"X-ANYPNT-ENV-ID" : env.get("env_id")}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                service_list = response.json()
                for servicenode in service_list:
                    timeSinceLastEvent = 0
                    if servicenode["status"] == "STARTED":
                        timeSinceLastEvent = Organization.getTimeSinceLastEvent(servicenode["domain"],env.get("env_id"), env.get("org_id"),self.token)
                        if timeSinceLastEvent > float(requestedTimeSinceLastTraffic):
                            print("Org Name: " + env.get("org_name") + "   ||    Environment: " + env["env_name"] + '   ||    Service Name: ' + servicenode["domain"] + '   ||    Time (Hours) Elapsed Since Last Event: ' + str(timeSinceLastEvent))
                            if fileOutput != None:
                                currentrecord = [env.get("org_name"),env["env_name"],servicenode["domain"],str(timeSinceLastEvent) ]
                                csvwriter.writerow(currentrecord)
                            if str(interactive).capitalize() == "Y" or str(interactive).capitalize() == "YES":
                                ans = input("Stop Application - " + servicenode["domain"] + " (y/n)? : ")
                                if ans.capitalize() == "Y" or ans.capitalize() == "YES":
                                    print("Stopping Application ----- : " + servicenode["domain"])
                                    if Organization.stopapplication(servicenode["domain"],self.token, env.get("env_id"), env.get("org_id")) == 200:
                                        print("Application Sucessfully Stopped: " + servicenode["domain"])
                                    else:
                                        print("Failed To Stop Application: " + servicenode["domain"])


        logging.info("Service Dashboard Finish")



    #############################################################################################################################
    #############################################################################################################################

    @staticmethod
    def getTimeSinceLastEvent(domainName,env_id,org_id,token):
        current_epoch_time = int(time.time())
        current_epoch_time_ms = int(time.time()) * 1000
        current_gmt_time = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())

        # Fetching details for last 20 days
        time_begining = (datetime.today() - timedelta(20)).strftime("%Y-%m-%dT%H:%M:%SZ")
        #default time if no traffic
        epoch_time_20daysago = current_epoch_time - 1728000

        # After
        url = "https://anypoint.mulesoft.com/cloudhub/api/v2/applications/" + domainName + "/dashboardStats?_=" + str(current_epoch_time_ms) + "&endDate=" + str(current_gmt_time) + "&interval=7200000&startDate=" + time_begining
        #    logging.info(url)
        headers = {'Authorization': "Bearer " + token, "X-ANYPNT-ENV-ID" : env_id, "X-ANYPNT-ORG-ID": org_id}
        dashboard = requests.get(url, headers=headers)
        last_event_epoch = epoch_time_20daysago
        if dashboard.status_code == 200:
            event_list = dashboard.json()["events"]
            for i in sorted(event_list.keys(), reverse=True):
                if(event_list[i] != 0):
                    #print(str(i) + ":" +  str(events[i]));
                    last_event_epoch = int(i)/1000;
                    break

        return (current_epoch_time - last_event_epoch)/(60*60)



    #############################################################################################################################
    #############################################################################################################################

    @staticmethod
    def stopapplication(domainName,token,env_id,org_id):
        url = "https://anypoint.mulesoft.com/cloudhub/api/applications/" + domainName + "/status"
        headers = {'Authorization': "Bearer " + token, "X-ANYPNT-ENV-ID" : env_id, "Content-Type": "application/json"}
        data = {
            "status": "STOP"
        }
        data_json = json.dumps(data)
        response = requests.post(url,data=data_json, headers=headers)
        return response.status_code


#############################################################################################################################
#############################################################################################################################



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--u", required=True, help="username for anypoint platform")
    parser.add_argument("--p", required=True, help="password for anypoint platform")
    parser.add_argument("--o", required=True, help="Organization Name for anypoint platform")
    parser.add_argument("--t", help="Inactive Time e.g 5h (5 hours), 7d (7 days)", default= "14d")
    parser.add_argument("--i", help="Interactive Mode to Stop applications", default= "N")
    parser.add_argument("--f", help="file name to generate output in csv format")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    if args.f != None and ((args.i).capitalize() == "Y" or (args.i).capitalize() == "Yes"):
        logging.error("!! Can't use interactive option with file output")
        quit()



    org = Organization(args.u,args.p,args.o)
    requestedTimeSinceLastTraffic = 0

    if args.t[-1] == "D" or args.t[-1] == "d":
        requestedTimeSinceLastTraffic = float(args.t[:-1]) * 24
    elif args.t[-1] == "h" or args.t[-1] == "H":
        requestedTimeSinceLastTraffic = args.t[:-1]
    else:
        logging.error("!! Error: Invalid Time Format")
        quit()

    org.generateCHRuntimeDetails(requestedTimeSinceLastTraffic, args.i, args.f)



#############################################################################################################################
#############################################################################################################################

if __name__ == "__main__":
    main()
