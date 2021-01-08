
def search_in_index(storage, index_name, query='', start=0, hits_per_page=20):
    try:
        return storage.search_in_index(index_name, start, hits_per_page)
    except Exception as ex:
        print(ex)
        raise ex
