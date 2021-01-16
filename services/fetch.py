
class ImportService:
    def __init__(self, storage, enabled_providers=None):
        super(ImportService, self).__init__()
        self.enabled_providers = enabled_providers
        self.storage = storage

    async def run_import_task(self):
        print(f"*****************")
        print(f"IMPORT DATA")
        print(f"*****************")
        try:
            for provider in self.enabled_providers:
                print(f"RUN SEARCH FROM PROVIDER {provider.source}")
                datasets = await provider.search()
                for dataset in datasets:
                    print(dataset['source']['name'])
                    self.storage.store_object('dataset', dataset['identifier'], dataset['source'])
            return True
        except Exception as ex:
            print(f"*****************")
            print(f"IMPORT DATA EXCEPTION {ex}")
            print(f"*****************")
            raise ex