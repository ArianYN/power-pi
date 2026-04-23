import requests

class API:
    def __init__(self):
        pass

    @staticmethod
    def Get(url):
        response = requests.get(url)
        response.raise_for_status()
        return response.json()