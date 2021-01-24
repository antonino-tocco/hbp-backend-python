class Provider:
    def __init__(self):
        super(Provider, self).__init__()
        self.source = 'Provider'

    def search_datasets(self, start=0, hits_per_page=50):
        return []

    def search_models(self, start=0, hits_per_page=50):
        return []

    def map_datasets(self, items=[]):
        return []

    def map_models(self, items=[]):
        return []

