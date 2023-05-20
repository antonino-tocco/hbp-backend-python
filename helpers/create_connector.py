import aiohttp
import ssl
import certifi

def create_connector():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)
    return conn