import aiohttp
import zipstream
import threading


class DownloadService:
    def __init__(self):
        super(DownloadService, self).__init__()

    @staticmethod
    async def download_files_as_zip(files_url=[]):
        zip_file = zipstream.ZipFile()
        try:
            for (url, name) in files_url:
                file_name = name if name is not None else url.split('/')[-1]
                file_content = await DownloadService.__download_file__(url)
                if file_content is not None:
                    tmp_file_name = f"/tmp/{file_name}"
                    with open(tmp_file_name, 'wb') as f:
                        f.write(file_content)
                        f.close()
                    zip_file.write(tmp_file_name, file_name)
            return zip_file
        except Exception as ex:
            raise ex

    @staticmethod
    async def __download_file__(url):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            if response.status == 200:
                return await response.read()
            return None
