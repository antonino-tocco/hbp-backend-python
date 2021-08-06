#HBP BACKEND

#INTRO

"HBP BACKEND" is a project developed using Flask for accomplish the goal to retrieve hippocampus data like morphologies, electrophysiologies
and models and serve it by rest api. For this purpose the "HBP BACKEND" store the data retrieved from various sources like neuromorpho.org, hippocampome and ModelDB in an uniforme format.

#SETUP
The project setup is very simple. All the project is Docker based and Docker is the only tool that you must manually install.

After install docker you can run :
`docker-compose up --build` for run the project.

##COMPONENTS

###BACKEND
The backend is built on Flask, a web development framework written in Python.
It was built with dependency injection in mind and for this reason make a large use of Flask-Injector. 
It defines a series of rest api that allow the frontend to retrieve data in an uniforme format.
On the startup the backend perform a fetch job for retrieve data from the external sources and store it on the storage system.

###STORAGE
The storage system is implemented using Elastic Search.
The choice of Elastic Search as the storage system was made with search features in mind.
The rest api, thankful to Elastic Search, make possibile to give full-text search in data with incredible performance.
The storage system provides 2 main index: dataset, model.

####DATASET INDEX
The dataset index contains all the data such as: morphology, electrophysiology and connections.
The data in this index is retrieved from multiple providers such as Neuromorpho, Hippocampome etc.
After some manipulation, the data were stored in an uniform format.


####MODEL INDEX
The model index contains all the model data.
At this moment this data are only retrieved from the ModelDB provider.


##PROJECT STRUCTURE
The project and folder structure follow this scheme:
1. Config: folder that contains configuration files: (one for each external provider)
2. Helpers: folder that contains helper classes and methods. It defines logic for interact with external provider, using the storage system, parse search arguments or download a file
3. Services: folder that contains injectable services that implements business logic.
4. Routes: folder that contains all rest api route definition files.

##PROVIDERS
The external providers from which the backend retrieve data was:
1. Neuromorpho
2. Hippocampome
3. ModelDB

###NEUROMORPHO
The most important key in Neuromorpho provider is the brain_regions.

This array define for which regions make the search.
The other keys define how to filter for data for the given regions.

At this moment is not possibile to add other filter.
The Neuromorpho provider only return morphologies with .asc and swc file.

##HIPPOCAMPOME
The Hippocampome provider have 3 values for filter:
1. Morphologies
2. Layers
3. Markers

You can experiment with this values for found the correct combination.

##MODEL DB
For the ModelDB provider there is only one configuration key "region_key".

It define the region for which run the search.


##API
Follow a list of available api divided by topics

###SEARCH
The search apis is the core api of the backend system.
Its allow to retrieve data to show on the frontend.

Its is divided in 2 main routes:
1. Search all api
2. Paged search api

####SEARCH ALL API
The search all api is available on the path: /search/{index_name}/all. The HTTP methods available for this api is: POST, GET.
It accept a single parameter: `ids` for give a list of all the ids of the object to retrieves. The `ids` parameter can also be empty and in this case the api will returns all the data in the dataset.

The {index_name} parameter give you the possibility to choose from which index retrieve data: dataset or model.
The response is in the form: `{
    items: [item1, item2]
}`

####PAGED SEARCH API
The paged search api is used through all the frontend for showing data. It make possible to retrieve paged data, also with multiple filter capabilities.

The base path for the paged search api is /search/{index_name} but it also allow to specify path params in this form: /search/{index_name}/{page}/{hits_per_page}.
By default page is 0 and hits_per_page is 20.

The paged search api also allow to specify other args and in detail:
`
{
    'data_type': 'morphology'|'electrophysiology'|'connection',
    'query': string, //a text query for make full text search on elastic search
    'filters': {
        'secondary_region': string, //the hippocampus sub region,
        'cell_type': string,
        'species': string[],
        'channels': string[],
        'receptors': string[],
        'layers': string[],
        'implementers': string[],
        'model_concepts': string[]
    }
}
`
By default all the filters are empty.

The response is in this format:
`{
    'total': int, //the total number of results,
    'total_page': int, //the total number of pages based on results and hits per page,
    'items': object[], //the items returned from the storage
    'page': int, //the current page number,
    'size': int //the hits per page
}`

###DOWNLOAD
The download apis are wrappers for make possibible download external files, such as asc files or swc. Using those apis it is possible to download multiple files inside a zip file.


####DOWNLOAD ALL API



####DOWNLOAD API
