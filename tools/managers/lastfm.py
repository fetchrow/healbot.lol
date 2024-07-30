import aiohttp
import json

class Handler:
    def __init__(self, api_key):
        self.session = aiohttp.ClientSession()
