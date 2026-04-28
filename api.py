import requests

class API:
    def __init__(self):
        pass

    @staticmethod
    def Get(url):
        response = None
        try:
            response = requests.get(url)
            response.raise_for_status()
        except:
            return None
        return response.json()
    
    @staticmethod
    def GetWithToken(url, token):
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.HTTPError:
            return response.status_code
        except:
            return response.status_code
        return response.json()
    
    @staticmethod
    def PostXAdminKey(url, key, service, audience, scopes, old_jti):
        headers = {
            "X-Admin-Key": key
            }
        
        body = {
            "service": service,
            "audience": audience,
            "scopes": scopes,
            "old_jti": old_jti
        }

        response = requests.post(url, headers=headers, json=body)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            return response.status_code
        return response.json()