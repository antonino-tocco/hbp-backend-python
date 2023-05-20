import aiohttp

def create_connector():
    conn = aiohttp.TCPConnector(verify_ssl=False)
    return conn






