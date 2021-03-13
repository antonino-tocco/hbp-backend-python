#HBP BACKEND

##CONFIGURATION

The folder config contains 3 configuration files(in json format), one for each data provider.

Each configuration files contains self explained key for values.

###NEUROMORPHO
The most important key in Neuromorpho provider is the brain_regions.

This array define for which regions make the search.
The other keys define how to filter for data for the given regions.

At this moment is not possibile to add other filter.
The neuromorpho provider only return morphologies with .asc file.

##HIPPOCAMPOME
The hippocampome provider have 3 values for filter:
1.Morphologies
2.Layers
3.Markers

You can experiment with this values for found the correct combination.

##MODEL DB
For the model db provider there is only one configuration key "region_key".

It define the region for which run the search.