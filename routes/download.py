import asyncio
from flask import request, send_file, Response
from icecream import ic

from dependency import AppModule
from injector import Injector
from services import SearchService, DownloadService
from helpers import parse_query_args, zip_generator
from . import routes_api


@routes_api.route('/download/<index_name>/all', methods=['POST', 'GET'])
def download_all(index_name):
    """
    Download all the files in index_name
    ---
    tags:
    - Download all
    parameters:
      - in: path
        name: index_name
        type: string
      - in: body
        name: body
        schema:
          id: DownloadAllPayload
          properties:
                secondary_region:
                  type: string
                  description: The secondary region of the hippocampus to search. (only for morphologies and electrophysiologies)
                  example: CA1
                cell_type:
                  type: string
                  description: The cell type to search
                  example: principal cell
                species:
                  type: string
                  description: The species to search
                  example: rat, mouse
                channels:
                  type: string
                  description: The channel to search. (only for models)
                  example: I K
                receptors:
                  type: string
                  description: The receptor to search. (only for models)
                  example: AMPA
                layers:
                  type: string
                  description: The layer to search. (only for models)
                  example: CA1:SO
                implementers:
                  type: string
                  description: The implementers of the model. (only for models)
                  example: Migliore
                model_concepts:
                  type: string
                  description: The model concept to search. (only for models)
                  example: Detailed Neuronal Model

    responses:
      200:
        description: 'OK'
    """
    try:
        data = {}
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args.to_dict()
        search_service = Injector(AppModule).get(SearchService)
        data_type, query, region, cell_type, species, layers, channels, receptors, implementers, model_concepts = parse_query_args(
            data)
        results = search_service.get_all_in_index(index_name, query=query, data_type=data_type, secondary_region=region,
                                                  cell_type=cell_type, species=species)
        if results is not None and len(results) > 0:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            file_urls = list(map(lambda x: x['download_link'], results))
            zip_file = loop.run_until_complete(DownloadService.download_files_as_zip(files_url=file_urls))
            return Response(zip_generator(zip_file), mimetype='application/zip',
                            headers={'Content-disposition': 'attachment; filename={}'.format('archive.zip')})
    except Exception as ex:
        ic(f"Exception send file {ex}")
        return f"Exception download all file {ex}"


@routes_api.route('/download/<index_name>', methods=['POST', 'GET'])
def download(index_name):
    """
    Download selected files in index_name
    ---
    tags:
    - Download selected
    parameters:
      - in: path
        name: index_name
        type: string
        example: dataset
      - in: body
        schema:
          id: DownloadSelectedPayload
          properties:
            ids:
              type: array
              items:
                type: string
                description: The ids of the resources to search

    responses:
      200:
        description: 'OK'
    """
    try:
        data = {}
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args.to_dict()
        if 'ids' in data and isinstance(data['ids'], str):
            data['ids'] = data['ids'].split(',')
        else:
            data['ids'] = []
        search_service = Injector(AppModule).get(SearchService)
        ids = data['ids']
        results = search_service.get_all_in_index(index_name, ids=ids)
        if results is not None and len(results) > 0:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            file_urls = list(map(lambda x: x['download_link'], results))
            zip_file = loop.run_until_complete(DownloadService.download_files_as_zip(files_url=file_urls))
            return Response(zip_generator(zip_file), mimetype='application/zip', headers={'Content-disposition':
                'attachment; filename={}'.format(
                    'archive.zip')})
        return results
    except Exception as ex:
        ic(ex)
        return f"Exception download file {ex}"
