import time
import requests

class BallChasingClient:
    def __init__(self, token: str, base_url: str="https://ballchasing.com/api", timeout: int=15):
        self._token = token
        self._base_url = base_url
        self._timeout = timeout
    
    def _request(self, method: str, path: str | None = None, params: dict = None, json: dict = None, files: dict = None, retrys: int = 3) -> dict:
        # Make request to api
        url = f"{self._base_url}/{path}" if path else self._base_url
        headers = {
            "Authorization": self._token
        }
        try:
            response = requests.request(method, url, params=params, json=json, files=files, headers=headers, timeout=self._timeout)
        except Exception as e:
            # Just return the exception like a api response
            # TODO: Need to look at how this api response to replicate it.
            return {"error": str(e)}
        
        for _ in range(1, retrys, 1):
            # check if response is successful
            if response.status_code >= 200 and response.status_code < 300:
                return response.json()
            elif response.status_code == 401:
                return {"error": "Unauthorized, please make sure the client was initialized with a valid token"}
            elif response.status_code == 429:
                # We are getting rate limited, not sure if i should handle this here or let the caller handle it.
                # try waiting after timeout and retying up to 'retrys' times
                time.sleep(self._timeout)
                response = requests.request(method, url, params=params, json=json, files=files, headers=headers, timeout=self._timeout)
            else:
                return {"error": response.text}
        else:
            return {"error": "Max retries exceeded"}

    def ping(self):
        return self._request("GET")

    def get_replays(self):
        pass
