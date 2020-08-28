# hercules-challenge-protocols
Code related to the Experimental Protocols track from Hercules challenge

## Directory layout
* __data__: Directory with the input dataset for this track.
* __notebooks__: Jupyter notebooks with the process taken for the creation and training of the topic extraction system.
* __results__: Output of the notebooks and scripts from the system. This folder contains a variety of files (pickled models, dataframes, track output...).
* __scripts__: Scripts provided to run the final system and obtain predictions for the track.
* __src__: Track-specific source code regarding the parsing and handling of protocols.

## Dependencies
In order to run the code from this repository, Python 3.7 or greater is required. Experiments were executed in Python 3.7.8, and that is the preferred version for the execution of the models. 

Instructions to install Python 3.7.8 are available at the [official website](https://www.python.org/downloads/release/python-378/). 

Once Python has been installed, it is preferrable to create a [environment] before installing the dependencies. To create a new python environment, the following command can be used:
```python
python -m venv edma_env
```

This environment can be then used with the following command:
```bash
souce edma_env/bin/activate
```

Finally, we can install the dependencies of the system with pip:
```python
pip install -r requirements.txt
```

## Exploring the creation of the systems
In the notebooks directory we provide a series of Jupyter notebooks that can be executed to explore how the systems were created and get more information about them or finetune their hyperparameters. In this section we will explain how to run those notebooks and provide some advice on how they should be executed.

If you have followed the steps from the previous section to install Python and the project dependencies, the [jupyter package](https://pypi.org/project/jupyter/) should already be installed. In order to run the Jupyter client, go to the notebooks directory and run the _jupyter notebook_ command:
```bash
cd notebooks
jupyter notebook
```

This will open a new tab in your browser with the Jupyter explorer where the different files can be explored:
![](./results/notebook_example.PNG)

If the browser was not automatically opened, you can connect to the Jupyter client through localhost on port 8888 ([localhost:8888](http://localhost:8888)).

Now you can click on any of the notebooks to explore its content or even rerun and modify the cells. Instructions on how to do this are provided in the [official Notebook docs](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Notebook%20Basics.html).

It is recommended to run the notebooks in a sequential manner, in the order indicated by their first filename number (i.e. notebook _1_data_fetching.ipynb_ should be run before _2_Data_Exploration.ipynb_ and so on). Non-sequential execution is not recommended and should be avoided, since the execution of one notebook may depend on outputs produced by the previous ones.

## How to run the systems
> __Note__: In order to run the systems you must first obtain the models used to perform the topic extraction. Due to size constraints, they are not included in these repositories. There are two main alternatives to obtain the models: the first one is the execution of every notebook to retrain and build the systems from scratch, but this may take some time; the second alternative is to go to the [complete_system directory](./results/6_complete_system) and follow the instructions to download the trained models.
Several scripts are provided in the _scripts_ folder to execute the systems and reproduce the results obtained for this track. In the following sections we will explain the main functionality of each script and how they can be executed.

### Compute track results
The script _run_track_predictions.py_ can be used to obtain at once all the topics assigned to every protocol from the dataset. The following parameters can be passed to the script:
| Name | Description | Compulsory | Allowed Values |
| ---- | ----------- | ---------- | ------ |
| -f --format | Output format of the results. If no output format is specified, results are returned in JSON by default. | No | One of _csv_, _json_, _jsonld_, _n3_, _rdf/xml_ or _ttl_ |
| -o --output | Name of the file where the results will be saved. If no output file is specified, results will be written to the console instead. | No | Any valid filename. |

For more additional information about how to run the script, you can execute the following command:
```bash
python scripts/run_track_predictions.py -h
```

In the following example, we will be running the script twice. The first execution will print the results in console and in json format (default values). The second one will save the results to the file _results.ttl_ in the turtle format:
```bash
python scripts/run_track_predictions.py
python scripts/run_track_predictions.py -o results.ttl -f ttl
```

### Predict protocol topics
The script _predict_protocol.py_ can be used to obtain the topics for a given protocol or list of protocols. The following parameters can be passed to the string:
| Name | Description | Compulsory | Allowed Values |
| ---- | ----------- | ---------- | ------ |
| input | URL of the protocol to extract the topics from. If the --file flag is set, file with the urls of the protocols. | __Yes__ | Any protocol url or file. |
| --isFile | If present, this flag indicates that the input passed to the script is a file with the ids of each protocols delimited by newlines. | No | True or False |
| -f --format | Output format of the results. If no output format is specified, results are returned in JSON by default. | No | One of _csv_, _json_, _jsonld_, _n3_ or _ttl_ |
| -o --output | Name of the file where the results will be saved. If no output file is specified, results will be written to the console instead. | No | Any valid filename. |

For more additional information about how to run the script, you can execute the following command:
```bash
python scripts/predict_protocol.py -h
```

In the following example, we will be running the script twice. The first execution will print the results in console and in json format (default values). The second one we will use the list of protocol urks from the [script directory](./scripts/test.txt) to predict the topics for those protocols. After that, we will save the results to the file _results.ttl_ in the turtle format:
```bash
python scripts/predict_protocol.py https://bio-protocol.org/e16
python scripts/predict_protocol.py scripts/test.txt --isFile -o results.ttl -f ttl
```

### Obtain protocol summaries
The script _run_track_summaries.py_ can be used to obtain the summaries of each protocol from the dataset. The following parameters can be passed to the script:
| Name | Description | Compulsory | Allowed Values |
| ---- | ----------- | ---------- | ------ |
| -m --model | Summarization model to be used to compute the summaries. If no model is set, _distilbart_cnn_protocols_ is used by default. | No | One of _distillbart_cnn_protocols_, _distillbart_xsum_protocols_ or _facebook/bart-large-cnn_ |
| -f --format | Output format of the results. If no output format is specified, results are returned in JSON by default. | No | One of _csv_, _json_, _jsonld_, _n3_, _rdf/xml_ or _ttl_ |
| -o --output | Name of the file where the results will be saved. If no output file is specified, results will be written to the console instead. | No | Any valid filename. |

For more additional information about how to run the script, you can execute the following command:
```bash
python scripts/run_track_summaries.py -h
```

In the following example, we will be running the script twice. The first execution will print the results in console and in json format (default values). The second one will save the results to the file _results.ttl_ in the turtle format:
```bash
python scripts/run_track_summaries.py
python scripts/run_track_summaries.py -o results.ttl -f ttl
```

## Using the demo API
An API has been deployed at http://edma-challenge.compute.weso.network/ where the different functionality of the system can be tested out without needing to manually run the scripts with Python.

For the protocols track, we provide the __api/protocol/topics__ GET endpoint to predict the topics of a given protocol. The following parameters can be sent in the JSON body:
| Name | Description | Compulsory | Allowed Values |
| ---- | ----------- | ---------- | ------ |
| input | Url of the protocol to extract the topics from (e.g. https://bio-protocol.org/e16) | __Yes__ | Any protocol URL. |
| format | Output format of the results. If no output format is specified, results are returned in JSON by default. | No | One of _json_, _jsonld_, _n3_ or _ttl_ |

An example body passed to the API could be as follows:
```json
{
  "input": "https://bio-protocol.org/e16",
  "format": "json"
}
```

The response will be as follows:
```json
{
  "task_id": "YOUR_TASK_ID"
}
```

A task identifier will be returned. We can query the __api/prediction/<task_id>__ endpoint to get the status of our task.

The GET endpoint __api/protocol/summary__ is also provided to compute the summary of the protocol. The following parameters can be sent in the JSON body:
| Name | Description | Compulsory | Allowed Values |
| ---- | ----------- | ---------- | ------ |
| model | Summarization model to be used to compute the summaries. If no model is set, _distilbart_cnn_protocols_ is used by default. | No | One of _distillbart_cnn_protocols_, _distillbart_xsum_protocols_ or _facebook/bart-large-cnn_ |
| format | Output format of the results. If no output format is specified, results are returned in JSON by default. | No | One of _csv_, _json_, _jsonld_, _n3_, _rdf/xml_ or _ttl_ |

## Results obtained
The results obtained for the track dataset can be found in the [script_results folder](./results/9_scripts_results). These results are provided in multiple formats (_.csv_, _.json_, _.jsonld_, and _.ttl_).
