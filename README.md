# platform-tools
Scripts to perform common platform related tasks

This script works only with Cloudhub. It works at org level and in its simplest form it takes anypoint credentials and org id. Successful execute of script generates 3 CSV files in same
folder. ["RuntimeManagerDetails.csv", "APIManagerDetails.csv", "UserDetails.csv"]. If operator doesn't have permission in any particular environment then its skipped.

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

e.g You may further filter the results by details [APIManager, RuntimeManager or UserDetails] or by environment name.
e.g below query will generate only RuntimeManagerDetails.csv for Production environment.


```
vsharma-ltm1:general vikas.sharma$ python PlatformUtils.py --u username --p password --o "********************************" --e "Production" --d "RuntimeManager" 
INFO:root:Organization Data Initializing.. 
INFO:root:Environment List for Organization ******************************* : [Development,QA,Training,Production,UAT] 
INFO:root:Generating Runtime Applications Details for environment : [Production] INFO:root:RuntimeManagerDetails successfully created
 vsharma-ltm1:general vikas.sharma$ ls -l RuntimeManagerDetails.csv
 -rw-r--r--@ 1 vikas.sharma 454177323 9511 Dec 11 15:38 RuntimeManagerDetails.csv 
 ```
