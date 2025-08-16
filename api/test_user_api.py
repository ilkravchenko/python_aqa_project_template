import base64
import json

from api.base_api import BaseApi


class TestUserAPI(BaseApi):
    """
    A class that extends BaseApi to handle API requests related to Test User API.
    Provides methods for Some business processes and creating Users.
    """

    def start_business_process(self, bp_key: str, request_data: str, **kwargs) -> dict:
        """
        Start a business process by calling the API with the provided business process key and request data.

        Args:
            bp_key (str): The business process definition key to start the process.
            request_data (str): The request data, which must be in Base64 format.
            **kwargs: Additional optional arguments for the API request.

        Returns:
            dict: The JSON response parsed from the API's response.

        Raises:
            ValueError: If the request_data is not in a valid Base64 format.
        """
        # Validate if request_data if Base64-encoded
        if not self._is_base64(request_data):
            raise ValueError('The request_data is not in a valid Base64 format.')

        # Get the authorization token
        token = self.get_token()

        # Define the API endpoint URL
        url = '/apitest/business-process/api/start-bp'

        # Set the headers with the token
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        data = {
            'businessProcessDefinitionKey': bp_key,
            'startVariables': {
                'request_data': request_data
            }
        }

        # Send POST request and get the response
        response = self.post(url=url, data=data, headers=headers, **kwargs)

        # Parse and return the response in JSON format
        return self.parse_response_to_json(response)

    @staticmethod
    def _xml_payload(value: str) -> str:
        # Example XML payload
        return \
            (f"<soapenv:Envelope   xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\""
             f"  \r\n                    xmlns:env="
             f"<value>{value}</value> ")

    def create_test_user_xml(self, request_data: str, full_response: bool = False) -> dict:
        """
        Name of the service

        Purpose of the service:
        Purpose

        Args:
            request_data (str): The request data, which must be in Base64 format.
            full_response

        Returns:
            dict: The JSON response parsed from the API's response.

        Raises:
            ValueError: If the request_data is not in a valid Base64 format.
        """
        # Call the start_business_process with a specific business process definition key
        payload = self._xml_payload(request_data)

        # url
        url = 'URL without base_url'

        # Set the content type to XML as required by the SOAP API
        self.headers['Content-Type'] = 'text/xml;charset=UTF-8'

        # Send the POST request with the payload and print the response
        response = self.post(url, data=payload)
        xml_response = self.parse_xml_to_json(response)['SOAP-ENV:Envelope']['SOAP-ENV:Body']['Response']
        if full_response:
            return xml_response['Result']['Value']

        # Check for Error
        assert xml_response['Result']['Value'][1]['value']['#text'] == '0', \
            xml_response['resultVariables']['entry'][1]['value']['#text']

        response_base64 = xml_response['resultVariables']['entry'][0]['value']['#text']
        return json.loads(base64.b64decode(response_base64).decode('utf-8'))

    @staticmethod
    def _is_base64(s: str) -> bool:
        """
        Check if a given string is valid Base64.

        Args:
            s (str): The string to check.

        Returns:
            bool: True if the string is valid Base64, False otherwise.
        """
        try:
            # Attempt to decode the string and compare to ensure it is valid Base64
            if base64.b64encode(base64.b64decode(s)).decode() == s:
                return True
        except Exception:
            return False
        return False
