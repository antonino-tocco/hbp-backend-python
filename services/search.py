
def search_in_index(storage, index_name, query=''):
    try:
        return storage.search_in_index(index_name)
    except Exception as ex:
        print(ex)
        raise ex
