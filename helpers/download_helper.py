import os
import zipstream
from io import BytesIO
import requests
from icecream import ic


def zip_generator(zip_file:zipstream.ZipFile):
    for chunk in zip_file:
        yield chunk


def download_image(url=None, source=None):
    assert(url is not None)
    assert(source is not None)
    if url is None or url.strip() == "":
        return None
    response = requests.get(url)
    if response.status_code == 200:
        image_name = url.split('/')[-1]
        buffer_image = BytesIO(response.content)
        buffer_image.seek(0)
        static_dir = os.getenv('STATIC_DIR')
        image_dir = f"{os.getenv('IMAGES_DIR')}/{source.lower()}"
        image_dir_full_path = f"{static_dir}/{image_dir}"
        if not os.path.exists(image_dir_full_path):
            os.makedirs(image_dir_full_path)
        image_file_name = f"{image_dir_full_path}/{image_name}"
        with open(image_file_name, 'wb') as image_file:
            try:
                image_file.write(buffer_image.getvalue())
                image_file.close()
                return f"{image_dir}/{image_name}"
            except Exception as ex:
                ic(f'Exception storing image file {ex}')
    return None