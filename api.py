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
        except requests.HTTPError:
            return response
        except:
            return response
        return response.json()
    
    @staticmethod
    def Post(url, data):
        response = None
        try:
            response = requests.post(url, data)
            response.raise_for_status()
        except requests.HTTPError:
            return response
        except:
            return response
        return response.json()
    
    @staticmethod
    def PatchWithToken(url, token, data):
        headers = {"Authorization": f"Bearer {token}"}
        response = None
        response = requests.patch(url, json=data, headers=headers)
        return response

    @staticmethod
    def GetWithToken(url, token):
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.HTTPError:
            return response
        except:
            return response
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