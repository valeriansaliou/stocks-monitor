import json, requests


class MtGox(object):
    def __init__(self):
        self.__api_base = 'https://data.mtgox.com/api/2'

    def __post_request(self, path):
        response = requests.get(self.__api_base + path)

        if response.status_code != 200:
            raise Exception('Bad Status Code (Not 200)')
        if not 'application/json' in response.headers.get('content-type', ''):
            raise Exception('Bad Content Type (Not JSON)')
        else:
            return json.loads(response.text)

    def request(self, path):
        result = self.__post_request(path)

        return result.get('data', {})
