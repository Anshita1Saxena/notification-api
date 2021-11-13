"""
This program sends the message to the Slack post validating
via validation functionality.
"""
__author__ = "Anshita Saxena"
__copyright__ = "(c) Copyright IBM 2020"
__credits__ = ["BAT DMS IBM Team"]
__email__ = "anshita333saxena@gmail.com"
__status__ = "Production"

# Import all the required libraries
# Import Flask API for building REST APIs
import flask_api
from flask import request
from flask_api import status

# Import configparser to parse the INI parameter file
import configparser

# HTTP library
import requests

# Import Json
import json

# Import for exception handling
from requests.exceptions import ConnectionError, Timeout, ConnectTimeout, ReadTimeout
from werkzeug.exceptions import BadRequest, InternalServerError

# Create an instance of Flask
app = flask_api.FlaskAPI(__name__)

# Parsing the INI file
CONFIG = configparser.ConfigParser()
# Read the mainapp.ini parameter file
CONFIG.read('mainapp.ini')
# Initialize the slack token variable
slack_token = CONFIG['ApplicationParams']['slack_token']
slack_token = str(slack_token)


# route decorator is used for creating URL
@app.route('/api/tpd/v1/alerts/slack', methods=['POST'])
def slack_alert():
    try:
        # Saving the json sent as request from another API
        content = request.json
        send_data = {'header': request.headers['X-Api-Key'],
                     'data': request.json}

        # If request json is not empty, then perform the below steps
        if content != {}:
            channel_name = ""

            # Initialise the list holding slack member id
            distribution_list_split = []
            # Null check for Channel Name
            if "channelName" in content.keys():
                channel_name = content['channelName']
            # Null check for Slack Member ID
            if "distributionList" in content.keys():
                distribution_list = content['distributionList']
                distribution_list_split = distribution_list.split(",")

            # Post the request to validation API for performing data checks
            # Setting timeout for 6 seconds
            response = requests.post(
                url='http://10.175.226.107:30361/api/tpd/v1/validation',
                json=send_data, timeout=6.0)

            """If status code is 400,
            then store the response received from validation API
            Send the required responses with HTTP codes
            """
            if response.__dict__['status_code'] == 400:
                resp = json.loads(
                                response.__dict__['_content'].decode(
                                                                'utf-8'))
                return resp, status.HTTP_400_BAD_REQUEST
            if response.__dict__['status_code'] == 401:
                resp = json.loads(
                                response.__dict__['_content'].decode(
                                                                'utf-8'))
                return resp, status.HTTP_401_UNAUTHORIZED
            if response.__dict__['status_code'] == 403:
                resp = json.loads(
                                response.__dict__['_content'].decode(
                                                                'utf-8'))
                return resp, status.HTTP_403_FORBIDDEN

            # If status code is 200, then perform the steps written below
            if response.__dict__['status_code'] == 200:

                # Loading response content to dictionary
                real_dict = json.loads(response.__dict__['_content'])

                # Store the message
                message_on_slack = real_dict['message']

                # Store the response
                resp = real_dict['res']

                """
                Checking whether Channel name exist in request or not
                as it is optional
                """
                true_channel = False
                if "true_channel" in real_dict.keys():
                    true_channel = True

                # Checking Date and Time as it is required field
                if 'dateAndTime' in resp.keys():
                    # If Slack Member ID exist and channel name exists
                    if len(distribution_list_split) >= 1 and \
                            distribution_list_split[0] != "":
                        for member_id in distribution_list_split:
                            # Send the message to Slack Members via Slack API
                            data = {
                                'token': slack_token,
                                'channel': member_id,
                                'text': message_on_slack
                            }
                            requests.post(
                                url='https://slack.com/api/chat.postMessage',
                                data=data)
                    else:
                        # Send the message to Slack Channel via Slack API
                        data = {
                            'token': slack_token,
                            'channel': channel_name,
                            'text': message_on_slack
                        }
                        requests.post(
                            url='https://slack.com/api/chat.postMessage',
                            data=data)
                    if true_channel is True:
                        """
                        If only channel name exists
                        then send the message to Slack Channel
                        """
                        data = {
                            'token': slack_token,
                            'channel': channel_name,
                            'text': message_on_slack
                        }
                        requests.post(
                            url='https://slack.com/api/chat.postMessage',
                            data=data)

                    # Return the 200 response directly
                    resp = real_dict['res']
                    return resp, status.HTTP_200_OK

            # If response is 500, then return the error response
            if response.__dict__['status_code'] == 500:
                resp = json.loads(
                                response.__dict__['_content'].decode(
                                                                'utf-8'))
                return resp, status.HTTP_500_INTERNAL_SERVER_ERROR
    except (ConnectionError, Timeout, ConnectTimeout, ReadTimeout,
            ConnectionRefusedError):
        resp = {}
        resp['errorCode'] = 500
        resp['errorMessage'] = 'Internal Server Error'
        return resp, status.HTTP_500_INTERNAL_SERVER_ERROR


@app.errorhandler(BadRequest)
def handle_exception(e):
    """
    app decorator for registering a function to handle errors or exceptions for
    400 response code
    """
    resp = {}
    resp['errorCode'] = 400
    resp['field'] = 'BAD JSON'
    resp['errorMessage'] = 'Bad Request'
    return resp, status.HTTP_400_BAD_REQUEST


@app.errorhandler(InternalServerError)
def handle_500(e):
    """
    app decorator for registering a function to handle errors or exceptions for
    500 response code
    """
    resp = {}
    resp['errorCode'] = 500
    resp['errorMessage'] = 'Internal Server Error'
    return resp, status.HTTP_500_INTERNAL_SERVER_ERROR


# Main function
if __name__ == '__main__':

    # Run the flask application on specific port
    app.run(host='0.0.0.0', port=3000)
