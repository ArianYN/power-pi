import requests

class API:
    def __init__(self):
        pass

    @staticmethod
    def Get(url):
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def GetWithToken(url, token):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()