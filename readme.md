#HBP BACKEND

#INTRO

"HBP BACKEND" is a project developed using the Flask micro-web environment with the goal to retrieve hippocampus related data such as morphologies, electrophysiology traces/metadata and neural models and make them available through rest api calls. For this purpose the "HBP BACKEND" store the data retrieved from various sources (such as neuromorpho.org, hippocampome.org and ModelDB) in an uniform format.

##SETUP
The project setup is very simple. All the project is Docker based and Docker is the only tool that you must manually install.

After installing docker you can run :
`docker-compose up --build` for run the project.

##ARCHITECTURE
The architecture reflects the following diagram.
The Flask Backend fetches external data source and store data (transformed to use a uniform format) in elastic search.
When the frontend perform a request, the backend retrieves the needed information from the Elastic Search Storage.

![architecture](architecture.jpg)

##COMPONENTS

###BACKEND
The backend is built in Flask, a Python-based web development framework.
It was built with dependency injection in mind and for this reason it makes a large use of Flask-Injector. 
It defines a series of rest api that allow the frontend to retrieve data in an uniform format.
Upon starting up, the backend runs a fetch job for retrieving data from the external sources and store them in the storage system.

###STORAGE
The storage system is implemented using Elastic Search thanks to its search inspired engine.
The rest apis, thanks to Elastic Search, make it possibile to give full-text search in data with very high throughput.
The storage system provides 2 main indices: dataset and model.

####DATASET INDEX
The dataset index contains all the data such as: morphology, electrophysiology and connections.
The data in this index is retrieved from multiple providers such as Neuromorpho and Hippocampome.
After some manipulation, the data are stored in a uniform format.


####MODEL INDEX
The model index contains all the model data.
At this moment this data are only retrieved from the ModelDB provider.


##PROJECT STRUCTURE
The project and folder structure follows this scheme:
1. Config: folder that contains configuration files (one for each external provider)
2. Helpers: folder that contains helper classes and methods. It defines the logic for interacting with external providers, using the storage system, parsing search arguments or downloading a file
3. Services: folder that contains injectable services that implements business logic.
4. Routes: folder that contains all rest api route definition files.

##PROVIDERS
The external providers from which the backend retrieves data are:
1. Neuromorpho
2. Hippocampome
3. ModelDB
4. Internal

###NEUROMORPHO
The main key on which the search in Neuromorpho is based, is the brain region (key name: brain_regions), which allows to filter out all the data related to brain regions different than the hippocampus.

The other keys define how to filter the hippocampus-related data.

The retrieved morphology files are either in the .asc or the .swc format.

##HIPPOCAMPOME
The data retrieved from the Hippocampome portal are filtered according to the following keys:
1. Morphologies
2. Layers
3. Markers


##MODEL DB
For the ModelDB provider there is only one configuration key "region_key".

##API
Follow a list of available api divided by topics:

1. SEARCH APIS
2. DOWNLOAD APIS
3. FILTER APIS

Swagger documentation for all apis is available on https://facility-hub.cineca.it/apidocs/
