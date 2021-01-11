from abc import ABC, abstractmethod
from injector import Module

class Storage:
    @abstractmethod
    def store_object(self, index, identifier, obj):
        pass

    @abstractmethod
    def get_object(self, index, identifier):
        pass

    @abstractmethod
    def search(self, index, start=0, hits_per_page=20, query='', ids=[], secondary_region=None, cell_type=None, species=None):
        pass
