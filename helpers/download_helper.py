import zipstream


def zip_generator(zip_file:zipstream.ZipFile):
    for chunk in zip_file:
        yield chunk