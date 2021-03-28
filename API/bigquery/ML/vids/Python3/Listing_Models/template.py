import sys
sys.path[0] += "\\site-packages"
from google.cloud import bigquery_datatransfer
from google.cloud import bigquery
import uuid
import datetime
import time
import pprint
import asyncio
import json
import datetime
import pytz
import time
pp = pprint.PrettyPrinter(indent=4, compact=True, width=1)
# end

# import and intalize the library
client = bigquery.Client()
#

class my_bigquery_client():

    def __init__(self):
        self.client = client
        self.bigquery = bigquery
        self.datetime = datetime
        self.pytz = pytz
        self.time = time 

    # paste env dictionary here
    env=  {
        "list_models":True
    }
    #

    # setup
    dataset_names = [
        "Models_Dataset",
    ]
    #


    def execute(self, data):

        #setup 
        client = self.client
        bigquery = self.bigquery
        datetime = self.datetime 
        pytz = self.pytz        
        time = self.time 
        name = data.get("titleName") if data.get("titleName")  else "My_Target_Table"
        emails = data.get("emails") if data.get("emails") else ["data_analysts@example.com"]
        query = data.get("query")
        source_url = data.get("sourceURL")  if data.get("titleName") else "gs://cloud-samples-data/bigquery/us-states/us-states.csv"
        emails = data.get("emails")
        table = ""
        #

        # create a dataset first if needed
        dataset_main = self.make_dataset()
        table_id = "{}.{}".format(dataset_main[0], name) 
        #    

        #create a table if needed
        # table= self.make_table(table_id,"load")
        #
                

        # list models
        if(self.env.get("list_models")):
            try:
                models = client.list_models(dataset_main[0])  
                schema = [
                    "project",
                    "dataset_id",
                    "model_id"
                ]
                result = {
                    "schema":[{"field":x} for x in schema],
                    "data":[
                        # Row values can be accessed by field name or index.
                        {
                            schema[0]:row[schema[0]],
                            schema[1]:row[schema[1]],
                            schema[2]:row[schema[2]]  
                        }
                        for row in models
                    ]
                }
                if(len(result["data"]) == 0):
                    result["data"] = [
                        {
                            schema[0]:"gcp-data-certs",
                            schema[1]:"Models_Dataset",
                            schema[2]:"My_model"
                        }
                        for row in [None,None,None]
                    ]

                return json.dumps(result)                 
                
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'                 
        #

        return "Check the backend env dictionary you did set it so the backend didnt do anything"


    def make_table(self,id,type=None,source_url=None):
        try:
            table_ref = bigquery.Table(id)
            if(type == "load"):
                job_config = bigquery.LoadJobConfig(
                    skip_leading_rows=1,
                    source_format=bigquery.SourceFormat.CSV,
                    schema=[
                        bigquery.SchemaField("name", bigquery.SqlTypeNames.STRING),
                        bigquery.SchemaField("post_abbr", bigquery.SqlTypeNames.STRING),
                    ],
                )

                job = client.load_table_from_uri(
                    [source_url],
                    table_ref,
                    job_config=job_config,
                )

                job.result()  # Waits for the job to complete.

                return  client.get_table(table_ref)  # Make an API request.            
            return client.create_table(table_ref)  # Make an API request.
        except BaseException:
            print("table exists")
            return client.get_table(id)
        # return"Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)        

    def make_dataset(self):
        try:
            for dataset_main in self.dataset_names:  
                try:
                    dataset_id = self.make_dataset_id(dataset_main)
                    dataset_init = bigquery.Dataset(dataset_id)
                    dataset = client.create_dataset(dataset_init, timeout=30)
                except:
                    pass
        except BaseException:
            print("dataset exists")
        finally:
            # print(["{}.{}".format(client.project,self.make_dataset_id(dataset_main)) for dataset_main in self.dataset_names ])
            return [self.make_dataset_id(dataset_main) for dataset_main in self.dataset_names ]


    def make_dataset_id(self, name):
        if(name == ""):
            raise IndexError
        return "{}.{}".format(client.project, name)







