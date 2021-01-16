
class ImportService:
    def __init__(self, storage, enable_providers):
        super(ImportService, self).__init__()
        self.storage = storage
        self.enable_providers = enable_providers

    async def run_import_task(self):
        print(f"*****************")
        print(f"IMPORT DATA")
        print(f"*****************")
        try:
            for provider in self.enabled_providers:
                print(f"RUN SEARCH FROM PROVIDER {provider.source}")
                datasets = await provider.search()
                for (identifier, dataset) in datasets:
                    print(dataset['name'])
                    self.storage.store_object('dataset', identifier, dataset)
            return True
        except Exception as ex:
            print(f"*****************")
            print(f"IMPORT DATA EXCEPTION {ex}")
            print(f"*****************")
            raise ex