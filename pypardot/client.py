import requests
from .objects.lists import Lists
from .objects.emails import Emails
from .objects.prospects import Prospects
from .objects.opportunities import Opportunities
from .objects.accounts import Accounts
from .objects.users import Users
from .objects.visits import Visits
from .objects.visitors import Visitors
from .objects.visitoractivities import VisitorActivities
from .objects.campaigns import Campaigns

from .errors import PardotAPIError

try:
    import json
except ImportError:
    import simplejson as json

BASE_URI = 'https://pi.pardot.com'


# As of 2/14/21, Pardot will no longer support id/pw authentication in lieu of Salesforce token authentication.
# Because Salesforce supports lots of different methods for getting a valid token, this package won't try to solve
# them all. Instead it will accept an already established token.
class PardotAPI(object):
    def __init__(self, salesforce_token, salesforce_business_unit):
        assert salesforce_token, AttributeError("salesforce_token is a required attribute")
        self.salesforce_token = salesforce_token
        self.salesforce_business_unit = salesforce_business_unit

        self.lists = Lists(self)
        self.emails = Emails(self)
        self.prospects = Prospects(self)
        self.opportunities = Opportunities(self)
        self.accounts = Accounts(self)
        self.users = Users(self)
        self.visits = Visits(self)
        self.visitors = Visitors(self)
        self.visitoractivities = VisitorActivities(self)
        self.campaigns = Campaigns(self)

    def post(self, object_name, path=None, params=None, retries=0, data=None):
        """
        Makes a POST request to the API. Checks for invalid requests that raise PardotAPIErrors. If the API key is
        invalid, one re-authentication request is made, in case the key has simply expired. If no errors are raised,
        returns either the JSON response, or if no JSON was returned, returns the HTTP response status code.
        """
        if params is None:
            params = {}
        params.update({'format': 'json'})

        try:
            request = requests.post(self._full_path(object_name, path), params=params, data=data, headers=self.headers)
            response = self._check_response(request)
            return response
        except PardotAPIError as err:
            if err.message == 'Invalid API key or user key':
                response = self._handle_expired_api_key(err, retries, 'post', object_name, path, params)
                return response
            else:
                raise err

    def get(self, object_name, path=None, params=None, retries=0):
        """
        Makes a GET request to the API. Checks for invalid requests that raise PardotAPIErrors. If the API key is
        invalid, one re-authentication request is made, in case the key has simply expired. If no errors are raised,
        returns either the JSON response, or if no JSON was returned, returns the HTTP response status code.
        """
        if params is None:
            params = {}
        params.update({'format': 'json'})
        try:
            request = requests.get(self._full_path(object_name, path), params=params, headers=self.headers)
            response = self._check_response(request)
            return response
        except PardotAPIError as err:
            if err.message == 'Invalid API key or user key':
                response = self._handle_expired_api_key(err, retries, 'get', object_name, path, params)
                return response
            else:
                raise err

    @staticmethod
    def _full_path(object_name, path=None, version=3):
        """Builds the full path for the API request"""
        full = '{0}/api/{1}/version/{2}'.format(BASE_URI, object_name, version)
        if path:
            return full + '{0}'.format(path)
        return full

    @staticmethod
    def _check_response(response):
        """
        Checks the HTTP response to see if it contains JSON. If it does, checks the JSON for error codes and messages.
        Raises PardotAPIError if an error was found. If no error was found, returns the JSON. If JSON was not found,
        returns the response status code.
        """
        if response.headers.get('content-type') == 'application/json':
            json = response.json()
            error = json.get('err')
            if error:
                raise PardotAPIError(json_response=json)
            return json
        else:
            return response.status_code

    @property
    def headers(self):
        return {'Authorization': "Bearer {}".format(self.salesforce_token),
                'Pardot-Business-Unit-Id': self.salesforce_business_unit}
