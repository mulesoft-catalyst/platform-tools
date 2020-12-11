# platform-tools

Scripts to perform common platform related tasks. <br/>
(**System requirements : Python 2.X**)

This script works only with Cloudhub. It works at org level and in its simplest form it takes anypoint credentials and org id. Successful execution of script generates 3 CSV files in same
folder. ["RuntimeManagerDetails.csv", "APIManagerDetails.csv", "UserDetails.csv"]. 
If operator doesn't have permission in any particular environment then its skipped.

```
vsharma-ltm1:Utils vikas.sharma$ python PlatformUtils.py --u "username" --p "password" -- o "org_id" 
INFO:root:Organization Data Inititializing..

INFO:root:Environment List for Organization ************************* : [Development,QA,Training,Production,UAT] 
INFO:root:Generating APIManager Details for environment : [Training,Production,UAT,QA,Development] 
ERROR:root:Insufficient Permissions to Query for APIManagerDetails/Environment :: Training 
INFO:root:APIManagerDetails sucessfuly created 
INFO:root:Generating Runtime Applications Details for environment : [Training,Production,UAT,QA,Development] 
ERROR:root:Insufficient Permissions to Query for RuntimeManagerDetails/Environment :: Training 
INFO:root:RuntimeManagerDetails sucessfuly created 
INFO:root:Generating Users and Roles Details.... 
INFO:root:Getting roles for user ************************************* 
ERROR:root:Insufficient Permissions to Query for RoleDetails in OrgId:: ********************************* 
vsharma-ltm1:Utils vikas.sharma$ 

```

There are some filter options available with the script. They can be explored using help like: [Note that username,password and org_id is mandatory].


```
vsharma-ltm1:general vikas.sharma$ python PlatformUtils.py --h usage: PlatformUtils.py [-h] [--u U] [--p P] [--o O] [--e E] [--d D] 
optional arguments:
 -h, --help show this help message and exit 
--u U --p P --o O --e E --d D 
username for anypoint platform password for anypoint platform Organization Name for anypoint platform 
Environment Name for anypoint platform
 Details Requested -- Possible Values, APIManager, 
RuntimeManager, UserDetails vsharma-ltm1:general vikas.sharma$ 
```

You may further filter the results by specific details [APIManager, RuntimeManager or UserDetails] or by environment name.
e.g below query will generate only RuntimeManagerDetails.csv for Production environment.

```
vsharma-ltm1:general vikas.sharma$ python PlatformUtils.py --u username --p password --o "********************************" --e "Production" --d "RuntimeManager" 
INFO:root:Organization Data Initializing.. 
INFO:root:Environment List for Organization ******************************* : [Development,QA,Training,Production,UAT] 
INFO:root:Generating Runtime Applications Details for environment : [Production] INFO:root:RuntimeManagerDetails successfully created
 vsharma-ltm1:general vikas.sharma$ ls -l RuntimeManagerDetails.csv
 -rw-r--r--@ 1 vikas.sharma 454177323 9511 Dec 11 15:38 RuntimeManagerDetails.csv 
 ```
 
 
 
 
 # ManageInactiveApplications.py
 
 This is a utility to list down and stop stale applications if required. It produces output of inactive applications and takes threshold as input [like 20h  or 7d ]. This works in 2 modes. 
 
 - In non interactive mode, it will produce output which lists applications which have not received any traffic since last provided threshold limit. e.g list of apps inactive for last N days or N hours.
 
 ``` > python ManageInactiveApplications.py --u username --p pwd --o org-id --t 5d ``` [   Inactive apps for last 5 days].  
 ``` > python ManageInactiveApplications.py --u 'username' --p pwd --o 'org-id' --t 48h ``` [Inactive apps for last 48 hours ]. 
 
 
 - Interactive mode, In addition to providing above list, for each application it will ask if user wants to stop the running application. Upon confirmation it stops the running application. 
 
 ``` > python ManageInactiveApplications.py --u username --p pwd --o org-id --t 5d --i y ```
 
 
 
 
 
 Alternatively, you can pull this docker image to run the utility. Its useful in scenerios where python dependencies are not installed on host system.

 ``` 
 vsharma-ltm1:manage-stale-apps-docker-build vikas.sharma$ docker pull vs193928/mulesoft:manage-stale-apps
manage-stale-apps: Pulling from vs193928/mulesoft
Digest: sha256:6c84ba6ad9aed58c93064129e8cbd50035819a4fdc2d9ea641513dc8d010761e
Status: Image is up to date for vs193928/mulesoft:manage-stale-apps
docker.io/vs193928/mulesoft:manage-stale-apps
vsharma-ltm1:manage-stale-apps-docker-build vikas.sharma$ docker images
REPOSITORY               TAG                 IMAGE ID            CREATED             SIZE
vs193928/mulesoft        manage-stale-apps   575ec6b064d3        2 hours ago         893MB
----
----
----


vsharma-ltm1:manage-stale-apps-docker-build vikas.sharma$ docker run vs193928/mulesoft:manage-stale-apps --u vikas_mule --p xxxx --o [ORG_ID]
INFO:root:Organization Data Inititializing.. 
Org Name: XXXXXXX   ||    Environment: Design   ||    Service Name: web-pqdj   ||    Time (Hours) Elapsed Since Last Event: 480.0
Org Name: XXXXXXX   ||    Environment: Design   ||    Service Name: XXX   ||    Time (Hours) Elapsed Since Last Event: 480.0
Org Name: XXXXXXX   ||    Environment: DEV   ||    Service Name: XXXX   ||    Time (Hours) Elapsed Since Last Event: 480.0
Org Name: XXXXXXX   ||    Environment: DEV   ||    Service Name: XXXX   ||    Time (Hours) Elapsed Since Last Event: 480.0
Org Name: XXXXXXX   ||    Environment: DEV   ||    Service Name: XXXX   ||    Time (Hours) Elapsed Since Last Event: 480.0
Org Name: XXXXXXX   ||    Environment: PROD   ||    Service Name: XXXX   ||    Time (Hours) Elapsed Since Last Event: 480.0
Org Name: XXXXXXX   ||    Environment: PROD   ||    Service Name: XXXX   ||    Time (Hours) Elapsed Since Last Event: 480.0

```

 
 
 
 
 
 
 
