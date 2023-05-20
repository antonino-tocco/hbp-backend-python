import aiohttp
import socket

def create_connector():
    conn = aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)
    return conn






