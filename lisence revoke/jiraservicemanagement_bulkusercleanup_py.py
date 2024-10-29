#Description: Script to revoke Confluence user licenses
#Usage instructions: Create a CSV file containing the Confluence user IDs. The file needs to be stored in the same directory where this script will run. Execute this script. Enter the filename and API key when prompted. 
#Author: Abhishek Kambli
#Date: 22-03-2024

import requests
import json
import csv
import re
import time
import datetime
import getpass

# Set Org ID and Confluence user group ID in Atlassian API URL
url = "https://api.atlassian.com/admin/v1/orgs/0b5448b2-995d-4a3a-a60c-163bd88355b1/directory/groups/c62f8d19-367f-4ee6-a568-4550c8a8f158/memberships/"

# Header for Authentication. Generate API key from Site Administration for bearer token.  

#apikey = input("Enter API key: ")
apikey = getpass.getpass(prompt='Enter API key: ')
apipattern = '^.{50,250}$'
if not(re.match(apipattern, apikey)):
    input("Invalid API Key. Please verify the API key and try again. Press Enter to exit.")
else:
 #apikey = getpass(prompt='Enter API key: ') 
 auth = 'Bearer ' + str(apikey)

 headers = {
   "Accept": "application/json",
   'Authorization': auth
 }   

 print (headers)

# Loop user IDs from CSV file to generate dynamic API URLs for revoking user licenses

 retries=0
 retry_limit = 3
 errors=0
 while retries < retry_limit:
  try:
   file_name = input("Enter the name of CSV file containing user IDs: ")
   with open(file_name) as fp:
    current_time = datetime.datetime.now()
    logfile = open('log.txt','a')
    print("", file=logfile)
    print("Jira Service Management license cleanup. Started on:", current_time, file=logfile)
    print("Jira Service Management license cleanup. Started on:", current_time)
    print('Reading file')
    time.sleep(1)
    for i in csv.reader(fp):
         pattern = '^([A-Za-z0-9]{6}:[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12})$'
         pattern2 = '^[a-zA-Z0-9]{24}$'
         id= ''.join(i)
         if 'sa_' in id:
             logfile = open('log.txt','a')
             print('Service account detected ' + str(*i) + ' . Account excluded from cleanup.')
             print('Service account detected ' + str(*i) + ' . Account excluded from cleanup.', file=logfile)
         if not(id):
             logfile = open('log.txt','a')
             print('Null value found. Skipping ' + str(*i))
             print('Null value found. Skipping ' + str(*i), file=logfile)
         elif (re.match(pattern, id)) or (re.match(pattern2, id)):
 #           print (*i)
             req = url + str(*i)
             logfile = open('log.txt','a')
             print ('Revoking access for user ' + str(*i))
             print ('Revoking access for user ' + str(*i), file=logfile)
             response = requests.request(
             "DELETE",
             req,
             headers=headers)
             print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
         else:
            logfile = open('log.txt','a')
            errors=1
            print('Invalid ID ' + str(*i))
            print('Invalid ID ' + str(*i), file=logfile)
   print()
   if errors==1:
       input("License cleanup completed with errors. Please check log file for details. Press Enter to exit.")       
   else:
       input("License cleanup completed. Press any key to exit.")
   break
 
  except Exception as e:
   print('File does not exist. ')
   retries += 1
   if retries == retry_limit:
    print('Aborting. Please verify whether the file exists and try again.')
    break
