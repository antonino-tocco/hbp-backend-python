from .provider import Provider

class ModelDbProvider(Provider):
    def __init__(self):
        super(ModelDbProvider, self).__init__()

    def search(self, start=0, hits_per_page=50):
        pass
    def map_items(self, items=[]):
        pass