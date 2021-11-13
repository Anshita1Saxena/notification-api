"""
This program sends the message to Mail,
post validating via validation functionality.
"""
__author__ = "Anshita Saxena"
__copyright__ = "(c) Copyright IBM 2020"
__credits__ = ["BAT DMS IBM Team"]
__email__ = "anshita333saxena@gmail.com"
__status__ = "Production"

# Import all the required libraries
# Import Flask API for building REST APIs
import flask_api
from flask_api import status
from flask import request

# Importing this library for Mail and Message
from flask_mail import Mail, Message

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
# Read the emailapp.ini parameter file
CONFIG.read('emailapp.ini')
# Initialize the Mail Server variable
mail_server = CONFIG['ApplicationParams']['mail_server']
# Initialize the port variable
mail_port = CONFIG['ApplicationParams']['mail_port']
# Casting port to integer
mail_port = int(mail_port)
# Initialize the username variable
mail_user = CONFIG['ApplicationParams']['mail_user']
# Initialize the password variable
mail_pass = CONFIG['ApplicationParams']['mail_pass']

# Set the configuration in mail instance
app.config['MAIL_SERVER'] = mail_server
app.config['MAIL_PORT'] = mail_port
app.config['MAIL_USERNAME'] = mail_user
app.config['MAIL_PASSWORD'] = mail_pass
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Sender email id
sender_email = 'XXXX.XXXX@XXXX.com'


# route decorator is used for creating URL
@app.route('/api/tpd/v1/alerts/email', methods=['POST'])
def email_alert():
    try:
        # Saving the json sent as request from another API
        content = request.json
        send_data = {'header': request.headers['X-Api-Key'],
                     'data': request.json}

        # If request json is not empty, then perform the below steps
        if content != {}:

            # Initialise the list holding email addresses
            distribution_list_split = []
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
                message_on_mail = real_dict['message']

                # Store the response
                resp = real_dict['res']

                # Checking Date and Time as it is required field
                if 'dateAndTime' in resp.keys():
                    if len(distribution_list_split) >= 1 and \
                            distribution_list_split[0] != "":
                        for email_id in distribution_list_split:
                            name, id = str(email_id).split(" <")
                            id = str(id).replace(">", "")

                            # Send the message to Email
                            msg = Message(
                                         'Message Subject',
                                         sender=sender_email,
                                         recipients=[id]
                                         )

                            # Attaching the mail message
                            msg.body = message_on_mail

                            # Sending the mail
                            mail.send(msg)

                    # Return the successful response
                    resp = real_dict['res']
                    return resp, status.HTTP_200_OK

            # If response is 500, then return the error response
            if response.__dict__['status_code'] == 500:
                resp = json.loads(
                                response.__dict__['_content'].decode(
                                                                'utf-8'))
                return resp, status.HTTP_500_INTERNAL_SERVER_ERROR

    # If the exception occurred, then send internal server error response
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
    app.run(host='0.0.0.0', port=4000)
