from functools import reduce
from icecream import ic
from .provider import Provider

BASE_URL = 'http://hippocampome.org/php/search_engine_json.php?query_str='

MORPHOLOGIES = ['Axons', 'Soma', 'Dendrites']
LAYERS = {
    'DG': {
        'key': 'DG',
        'layers': '????'
    },
    'CA3': {
        'key': 'CA3',
        'layers': '?????'
    },
    'CA2': {
        'key': 'CA2',
        'layers': '????'
    },
    'CA1': {
        'key': 'CA1',
        'layers': '????'
    },
    'SUB': {
        'key': 'SUB',
        'layers': '???'
    },
    'EC': {
        'key': 'EC',
        'layers': '??????'
    }
}
MARKERS = ['CB','CR','PV','Mus2R','5HT-3','Gaba-a-alpha','mGluR1a','vGluT3','CCK','SOM','nNOS','PPTA','vGluT2','CGRP','mGluR2/3','mGluR5','Prox1','GABAa \delta',
           'MUS1R','Mus3R','Mus4R','Cam','AMPAR 2/3','Disc1','BONG','p-CREB','Neuropilin2'
           ]


class HippocampomeProvider(Provider):

    def __init__(self):
        super(HippocampomeProvider, self).__init__()

    def search_models(self, start=0, hits_per_page=50):
        markers_str = ' OR '.join([f'I±{marker}' for marker in MARKERS])
        try:
            layers_repr = [f"{LAYERS[x]['key']}:{LAYERS[x]['layers']}" for x in LAYERS.keys()]
            morphologies_str = ' OR ' .join([f"{morphology}:{layer}" for morphology in MORPHOLOGIES for layer in layers_repr])
            url = BASE_URL + f'Connection:(Presynaptic:(Markers:({markers_str}) AND Morphology:({morphologies_str}), Postsynaptic:(Markers:({markers_str}) AND Morphoplogy:({morphologies_str}))'
            ic(f'url to call {url}')
        except Exception as ex:
            ic(f'Exception on creating query {ex}')

    def map_models(self, items=[]):
        pass