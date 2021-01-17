import sys
sys.path[0] += "\\site-packages"
from google.cloud import bigquery_datatransfer
from google.cloud import bigquery
from google.oauth2 import service_account
import uuid
import google.auth
import datetime
import time
import pprint
import asyncio
import json
import datetime
import pytz
import time
import os
pp = pprint.PrettyPrinter(indent=4, compact=True, width=1)
# end

# import and intalize the library also give youself drive access
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
        "create_external_table":False,
        "create_temp_external_table":False,
        "drive_create_external_table":False,
        "drive_create_temp_external_table":True
    }
    #

    # setup
    dataset_names = [
        "External_Query_Dataset"
    ]
    #


    def execute(self, data):

        #setup 
        client = self.client
        bigquery = self.bigquery
        datetime = self.datetime 
        pytz = self.pytz        
        time = self.time 
        name = data.get("titleName")
        emails = data.get("emails")
        query = data.get("query")
        table = ""
        #

        # create a dataset first if needed
        dataset_main = self.make_dataset()
        table_id = "{}.{}".format(dataset_main, name) 
        #    


                

        # create external table
        if(self.env.get("create_external_table")):
            try:
                # Configure the external data source
                dataset_id = dataset_main
                table_id = "{}.{}".format(dataset_main, query) 
                schema = [
                    bigquery.SchemaField("name", "STRING"),
                    bigquery.SchemaField("post_abbr", "STRING"),
                ]
                table = bigquery.Table(table_id, schema=schema)
                external_config = bigquery.ExternalConfig("CSV")
                external_config.source_uris = [
                    "gs://cloud-samples-data/bigquery/us-states/us-states.csv"
                ]
                external_config.options.skip_leading_rows = 1  # optionally skip header row
                table.external_data_configuration = external_config

                # Create a permanent table linked to the GCS file
                table = client.create_table(table)  # API request

                # Example query to find states starting with 'W'
                sql = 'SELECT * FROM `{}` WHERE name LIKE "W%"'.format( table_id)

                query_job = client.query(sql)  # API request

                w_states = list(query_job)  # Waits for query to finish
                return "There are {} states with names starting with W. we pulled the data from us-states.csv in cloud storage".format(len(w_states))                
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'
        #

        # create temp external table
        elif(self.env.get("create_temp_external_table")):
            try:
                schema = ["filename","name"]
                # Configure the external data source and query job.
                external_config = bigquery.ExternalConfig("CSV")
                external_config.source_uris = [
                    "gs://cloud-samples-data/bigquery/us-states/us-states.csv"
                ]
                external_config.schema = [
                    bigquery.SchemaField("name", "STRING"),
                    bigquery.SchemaField("post_abbr", "STRING"),
                ]
                external_config.options.skip_leading_rows = 1
                table_id = "usa_states"
                job_config = bigquery.QueryJobConfig(table_definitions={table_id: external_config})

                # Example query to find states starting with 'W'.
                sql = """
                SELECT _FILE_NAME AS {},{} FROM `{}` WHERE name LIKE "W%"
                
                """.format(schema[0],schema[1],table_id)
                query_job = client.query(sql, job_config=job_config)  # Make an API request.
                query_job.result()
                return json.dumps({
                    "schema":[{"field":x} for x in schema],
                    "data":[
                        # Row values can be accessed by field name or index.
                        {
                            schema[0]:row[schema[0]],
                            schema[1]:row[schema[1]] 
                        }
                        for row in query_job
                    ]
                })
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'
        #

        # drive create external table
        elif(self.env.get("drive_create_external_table")):
            try:
                dataset_id = dataset_main

                # Configure the external data source.
                dataset = client.get_dataset(dataset_id)
                table_id = query
                schema = [
                    bigquery.SchemaField("name", "STRING"),
                    bigquery.SchemaField("post_abbr", "STRING"),
                ]
                table = bigquery.Table(dataset.table(table_id), schema=schema)
                external_config = bigquery.ExternalConfig("GOOGLE_SHEETS")
                # Use a shareable link or grant viewing access to the email address you
                # used to authenticate with BigQuery (this example Sheet is public).
                sheet_url = (
                    "https://docs.google.com/spreadsheets/d/1i_QCL-7HcSyUZmIbP9E6lO_T5u3HnpLe7dnpHaijg_E/edit?usp=sharing"
                )
                external_config.source_uris = [sheet_url]
                external_config.options.skip_leading_rows = 1  # Optionally skip header row.
                external_config.options.range = (
                    "us-states!A20:B49"  # Optionally set range of the sheet to query from.
                )
                table.external_data_configuration = external_config

                # Create a permanent table linked to the Sheets file.
                table = client.create_table(table)  # Make an API request.

                # Example query to find states starting with "W".
                sql = 'SELECT * FROM `{}.{}` WHERE name LIKE "W%"'.format(dataset_id, table_id)

                query_job = client.query(sql)  # Make an API request.

                # Wait for the query to complete.
                w_states = list(query_job)
                return "There are {} states with names starting with W in the selected range. this data came from google drive".format(
                        len(w_states)
                    )
                             
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'
        #

        # drive create temp external table
        elif(self.env.get("drive_create_temp_external_table")):
            try:
                schema = ["name","post_abbr"]
                # Configure the external data source and query job.
                external_config = bigquery.ExternalConfig("GOOGLE_SHEETS")
                sheet_url = (
                    "https://docs.google.com/spreadsheets"
                    "/d/1i_QCL-7HcSyUZmIbP9E6lO_T5u3HnpLe7dnpHaijg_E/edit?usp=sharing"
                )
                external_config.source_uris = [sheet_url]
                external_config.schema = [
                    bigquery.SchemaField("name", "STRING"),
                    bigquery.SchemaField("post_abbr", "STRING"),
                ]
                external_config.options.skip_leading_rows = 1  # Optionally skip header row.
                external_config.options.range = (
                    "us-states!A20:B49"  # Optionally set range of the sheet to query from.
                )
                table_id = "usa_states"
                job_config = bigquery.QueryJobConfig(table_definitions={table_id: external_config})

                # Example query to find states starting with 'W'.
                sql = """
                SELECT * FROM `{}` WHERE name LIKE "W%"
                """.format(table_id)
                query_job = client.query(sql, job_config=job_config)  # Make an API request.
                query_job.result()
                [print(row) for row in query_job ]
                return json.dumps({
                    "schema":[{"field":x} for x in schema],
                    "data":[
                        # Row values can be accessed by field name or index.
                        {
                            schema[0]:row[schema[0]],
                            schema[1]:row[schema[1]] 
                        }
                        for row in query_job
                    ]
                })                
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'
        #


        return "Check the backend env dictionary you did set it so the backend didnt do anything"


    def make_table(self,id):
        try:
            table_ref = bigquery.Table(id)
            return client.create_table(table_ref)  # Make an API request.
        except BaseException:
            "table exists"
            return client.get_table(id)
        # return"Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)        

    def make_dataset(self):
        try:
            dataset_main = self.dataset_names[0]      
            dataset_id = self.make_dataset_id(dataset_main)
            dataset_init = bigquery.Dataset(dataset_id)
            dataset = client.create_dataset(dataset_init, timeout=30)
        except BaseException:
            print("dataset exists")
        finally:
            return "{}.{}".format(client.project,dataset_main)


    def make_dataset_id(self, name):
        if(name == ""):
            raise IndexError
        return "{}.{}".format(client.project, name)






