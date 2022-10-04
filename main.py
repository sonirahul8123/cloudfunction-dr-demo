from pprint import pprint
import json
import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

def hello_pubsub(event, context):
    
    credentials = GoogleCredentials.get_application_default()

    service = discovery.build('compute', 'v1', credentials=credentials)

    #  # Project ID for this request.
    project = "PROJECT_ID" 
    zone='asia-south2-c'
    maxResults=0
    orderBy = "creationTimestamp desc"
    web_instance_name= 'dr-web-server'

    request = service.snapshots().list(project=project, orderBy=orderBy, maxResults=maxResults)
    websnap= ''
    while request is not None:
         response = request.execute()
         # pprint(response)
         temp= []

         for snapshot in response['items']:
              # TODO: Change code below to process each `snapshot` resource:
              #pprint(snapshot)
              json_str = json.dumps(snapshot)
              resp = json.loads(json_str)    
              temp.append(resp['name'])
          # pprint(temp[0]) 
         snapname= temp 
          # pprint (snapname)
         f=[]
         webCount=0
         for i in temp:
              t=(i.split("-"))   
              # update below line according to your snapshot names
              if t[0]=="primary" and t[1]=="web":                                
                if webCount==0:
                    f.append(i)
                    webCount+=1
                    # pprint(f)
                    websnap= f[0]
                    pprint('web:')
                    pprint(websnap)           
          
         request = service.snapshots().list_next(previous_request=request, previous_response=response)
         
    instance_body1 = {                  
         
         "name": web_instance_name,
         "machineType": f"projects/{project}/zones/{zone}/machineTypes/e2-standard-2",
         "disks": [
         {         
         "boot": "true",
         "deviceName": web_instance_name,
         "diskEncryptionKey": {},
         "initializeParams": {
              "diskSizeGb": "10",
              "diskType": f"projects/{project}/zones/{zone}/diskTypes/pd-standard",
              "labels": {},
              "sourceSnapshot": f"projects/{project}/global/snapshots/{websnap}"
         },
         "mode": "READ_WRITE",
         "type": "PERSISTENT"
         }
    ],
    "networkInterfaces": [
         {
         "networkIP": "10.190.0.10",
         "stackType": "IPV4_ONLY",
         "subnetwork": f"projects/{project}/regions/asia-south2/subnetworks/default"
         }
    ]
    }     

    if websnap !='':
         request = service.instances().insert(project=project, zone=zone, body=instance_body1)
         response = request.execute()
