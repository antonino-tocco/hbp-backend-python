class Provider:
    def __init__(self):
        super(Provider, self).__init__()

    def get_config(self):
        return ""

    def get_search_url(self):
        return ""

    def get_search_method(self):
        return ""

    def search(self, start, hits_per_page):
        return []

    def map_items(self):
        return []

