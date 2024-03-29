from icecream import ic


class ImportService:
    def __init__(self, storage, enabled_dataset_providers=None, enabled_model_providers=None):
        super(ImportService, self).__init__()
        self.enabled_dataset_providers = enabled_dataset_providers
        self.enabled_model_providers = enabled_model_providers
        self.storage = storage

    async def run_import_task(self):
        print(f"*****************")
        print(f"IMPORT DATA")
        print(f"*****************")
        try:
            for provider in self.enabled_dataset_providers:
                ic(f"RUN SEARCH FROM PROVIDER {provider.source}")
                datasets = await provider.search_datasets()
                if datasets:
                    ic(f"STORE {len(datasets)} from {provider.source}")
                    for dataset in datasets:
                        self.storage.store_object('dataset', dataset['identifier'], dataset['source'])
            for provider in self.enabled_model_providers:
                ic(f"RUN SEARCH FROM PROVIDER {provider.source}")
                models = await provider.search_models()
                for model in models:
                    self.storage.store_object('model', model['identifier'], model['source'])
            return True
        except Exception as ex:
            print(f"*******************")
            print(f"IMPORT DATA EXCEPTION {ex}")
            print(f"*****************")
            raise ex