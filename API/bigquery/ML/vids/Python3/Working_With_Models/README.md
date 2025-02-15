# Working with Bigquery ML

<!-- ## [Youtube Walkthrough]() -->


* after the lab your file should look like template.final.py 
* if issues copy and paste from template.start.py


### Start the Angular App

* download the frontend [here](https://downgit.github.io/#/home?url=https://github.com/WindMillCode/Google/tree/master/API/bigquery/ML/AngularApp)
open a terminal and head to project root and run this command
```ps1
npm install -s
npx ng serve -c=bigqueryML --open=true
```

### Setup the Python Backend 
* download the backend [here](https://downgit.github.io/#/home?url=https://github.com/WindMillCode/Google/tree/master/API/bigquery/ML/vids/Python3/Working_With_Models)
in a terminal in the folder root
    * target makes it a local package, do not make it global, it might replace your packages
    * if you make a mistake or believe a corruption happened delete site-packages and try again
```ps1
pip install -r requirements.txt --upgrade --target .\site-packages
python .\tornado_server.py
```

* open template.py and in your code editor,

* this is a subpar navigation however if you click on the words they take you different parts of this lab

### Setup Cloud Credentials
* in order for the Python Backend to work the GOOGLE_APPLICATION_CREDENTIALS must be set
* follow the gifs in order to get this to work, (windows only)

![](./images/create_creds.gif)

### List Models

|permissions|
|:------|
|bigquery.dataViewer
|bigquery.dataEditor
|bigquery.dataOwner
|bigquery.metadataViewer
|bigquery.user
|bigquery.admin|


* in 'list models' paste this code
```py
        if( env == "list_models"):
            try:
                models = client.list_models(dataset_main[0])  
                schema = [
                    "project",
                    "dataset_id",
                    "model_id"
                ]
                # for model in models:
                #     print(model.reference.project)
                result = {
                    "schema":[{"field":x} for x in schema],
                    "data":[
                        # Row values can be accessed by field name or index.
                        {
                            schema[0]:row.reference.project,
                            schema[1]:row.reference.dataset_id,
                            schema[2]:row.reference.model_id  
                        }
                        for row in models
                    ]
                }
                if(len(result["data"]) == 0):
                    result["data"] = [
                        {
                            schema[0]:"No",
                            schema[1]:"Models",
                            schema[2]:"Here"
                        }
                        for row in [None]
                    ]

                return json.dumps(result)                 
                
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print(e)
                return 'an error occured check the output from the backend'                 
        #
```

### Get Model Metadata
|permissions|
|:------|
|bigquery.dataViewer
|bigquery.dataEditor
|bigquery.dataOwner
|bigquery.metadataViewer
|bigquery.admin


* in 'get model metadata' paste this code
```py
        elif(env == "get_model_metadata"):
            try:
                model_id = "{}.{}".format(dataset_main[0], name) 
                model = client.get_model(model_id)
                

                return """\nModel id is {} 
                Model friendly name is {}
                Model created on {}
                Model location {}
                Model description {}""".format(model.model_id,model.friendly_name,model.created,model.location,model.description)
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print(e)
                return 'an error occured check the output from the backend'              
        #
```

### Update Model Metadata

|permissions|
|:----|
|bigquery.dataEditor
|bigquery.dataOwner
|bigquery.admin

* in 'update model metadata' paste this code
```py
        elif(env == "update_model_metadata"):
            try:
                model_id = "{}.{}".format(dataset_main[0], name) 
                model = client.get_model(model_id)  # Make an API request.
                model.description = query
                model = client.update_model(model, ["description"])  # Make an API request.

                full_model_id = "{}.{}.{}".format(model.project, model.dataset_id, model.model_id)
                return  "Updated model '{}' with description '{}'.".format(
                        full_model_id, model.description
                    )
                                
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'    
        #
```

### Copy model
* to rename a model you must also copy a model

* in 'copy a model' paste this code
```py
        elif(env == "copy_model"):
            try:
                
                job_config = bigquery.job.CopyJobConfig(
                    create_disposition  ="CREATE_IF_NEEDED",
                    write_disposition  ="WRITE_TRUNCATE",
                )
                job = bigquery.job.CopyJob(
                    job_config=job_config,
                    sources = [
                        bigquery.table.TableReference(
                            dataset_ref = client.get_dataset(dataset_main[0]),
                            table_id = name                    
                        )]
                    ,
                    destination = 
                        bigquery.table.TableReference(
                            dataset_ref = client.get_dataset(dataset_main[0]),
                            table_id = dest_name                
                        )
                    ,
                    client= client,
                    job_id = "my_copy_{}".format(uuid.uuid4())
                )
                job.result()  # Wait for the job to complete.
                return "A copy of the model created."             
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'
        #
```

### Export a Model
* extract job

only export folllowing model types
|property|value|data|
|:------|:------:|------|
|AUTOML_CLASSIFIER|Tensorflow (tf 1.15)
|AUTOML_REGRESSOR|Tensorflow (tf 1.15)
|BOOSTED_TREE_CLASSIFIER|Tensorflow (tf 1.15)
|BOOSTED_TREE_REGRESSOR|Tensorflow (tf 1.15)
|DNN_CLASSIFIER|Tensorflow (tf 1.15)
|DNN_REGRESSOR|Tensorflow (tf 1.15)
|KMEANS|Tensorflow (tf 1.15)
|LINEAR_REG|Tensorflow (tf 1.15)
|LOGISTIC_REG|Tensorflow (tf 1.15)
|MATRIX_FACTORIZATION|Tensorflow (tf 1.15)
|TENSORFLOW (imported TensorFlow models)| Booster(xgboost 0.82)
|XGBOOST (imported XGBoost models)| (tensorflow saved model)

* doesnt work with ARRAY, TIMESTAMP, or GEOGRAPHY columns

* in 'extract a model' paste this code
```py
        elif(env == "extract_model"):
            try:
                model_id = "{}.{}".format(dataset_main[0], name) 
                model = client.get_model(model_id)

                print(storage_buckets)
                job = bigquery.job.ExtractJob(
                    client= client,
                    job_id = "my_copy_{}".format(uuid.uuid4()),
                    source = model,
                    destination_uris = storage_buckets,
                    job_config= bigquery.job.ExtractJobConfig(
                        destination_format="ML_TF_SAVED_MODEL" # ML_TF_SAVED_MODEL or ML_XGBOOST_BOOSTER                        
                    )
                )
                job.result()
                return "model {} export has been completed".format(name)
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'
        #
```

### Deleteing models
* only one at a time
in 'delete a model' paste this code
```py
        elif(env == "delete_model"):
            try:
                for name in models:
                    model_id = "{}.{}".format(dataset_main[0], name)
                    client.delete_model(model_id)  # Make an API request.
                return "Deleted all models as requested"          
            except BaseException as e:
                print('my custom error\n')
                print(e.__class__.__name__)
                print('\n')
                print(e)
                return 'an error occured check the output from the backend'   
```