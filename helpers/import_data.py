from . import enabled_providers

def import_data():
    for provider in enabled_providers:
        provider.search(query_text='')
        print(provider)
