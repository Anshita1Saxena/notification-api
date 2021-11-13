"""
This program validates the messages based on the null field,
authorization and forbidden request.
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

# Import configparser to parse the INI parameter file
import configparser

# Import regex (Regular Expression)
import re

# Import package for date and time
from datetime import datetime

# Create an instance of Flask
app = flask_api.FlaskAPI(__name__)

# Parsing the INI file
CONFIG = configparser.ConfigParser()

# Read the application.ini parameter file
CONFIG.read('application.ini')

# Initialize the api key variable
api_key = CONFIG['ApplicationParams']['api_key']
api_key = str(api_key)

# Initialize the channel name list variable
slack_channel_name = CONFIG['ApplicationParams']['channelName']
channelName = str(slack_channel_name)
slack_channel_name = channelName.split(",")

# Import for exception handling
from werkzeug.exceptions import BadRequest, InternalServerError


# route decorator is used for creating URL
@app.route('/api/tpd/v1/validation', methods=['POST'])
def validation():
    resp = {}
    message = ""
    valid = True
    field = ""

    # Saving the json sent as request from another API
    full_content = request.json

    # Extract api key and content from the request
    message_api_key = full_content['header']
    content = full_content['data']

    # If request json is not empty, then perform the below steps
    if content != {}:
        id = ""
        title = ""
        message_text = ""
        exception_details = ""
        date_and_time = ""
        message_type = ""
        channel_name = ""
        distribution_list = ""
        attempt = ""
        distribution_split_list = []

        # Null check for all the fields of data content in request header
        if "id" in content.keys():
            id = content['id']
        if "title" in content.keys():
            title = content['title']
        if "messageText" in content.keys():
            message_text = content['messageText']
        if "exceptionDetails" in content.keys():
            exception_details = content['exceptionDetails']
        if "dateAndTime" in content.keys():
            date_and_time = content['dateAndTime']
        if "messageType" in content.keys():
            message_type = content['messageType']
        if "attempt" in content.keys():
            attempt = content['attempt']
        if "distributionList" in content.keys():
            distribution_list = content['distributionList']
            distribution_split_list = distribution_list.split(",")
        if "channelName" in content.keys() or (
                                "channelName" in content.keys() and (
                                    "distributionList" not in content.keys() or
                                    distribution_list == "")):
            channel_name = content['channelName']

        # Construction of missed names of fields for error message
        resp_fields = ""
        resp_field_set = []
        # Error Message if the fields do not pass the validation
        error_message = ""
        # true_channel becomes true if channel name exists in request
        true_channel = False
        if "@" not in distribution_list:
            # If there is no @ symbol means distribution list belongs to slack
            valid, field, true_channel = slack_check(
                                                channel_name,
                                                distribution_split_list,
                                                slack_channel_name)
        elif "channelName" not in content.keys():
            # If channel name does not exist means function belongs to mail
            valid, field = email_check(distribution_split_list)
        elif "@" in distribution_list:
            # If @ exists in distribution list and holds the channel name also
            valid, field, true_channel = slack_check(channel_name,
                                                     distribution_split_list,
                                                     slack_channel_name)
        if id == "" or title == "" or message_text == "" or \
                message_type == "" or date_and_time == "" or \
                (channel_name == "" and distribution_list == ""):
            """
            If required fields are empty then store them in field set
            to show proper message to user
            """
            if id == "":
                resp_field_set.append("id")
            if title == "":
                resp_field_set.append("title")
            if message_text == "":
                resp_field_set.append("messageText")
            if date_and_time == "":
                resp_field_set.append("dateAndTime")
            if message_type == "":
                resp_field_set.append("messageType")
            if field != "":
                resp_field_set.append(field)
        if date_and_time != "":
            # Check the format of date
            try:
                datetime.strptime(str(date_and_time), "%Y-%m-%dT%H"
                                                      ":%M:%S.%fZ")
            except ValueError:
                resp_field_set.append("dateAndTime")
                error_message = "Incorrect Date Format. Should be: " \
                                "YYYY-mm-ddTHH:MM:SS.ffffffZ."

        # Create an appropriate error message having all the missing fields
        if len(resp_field_set) >= 1 and resp_field_set[0] != "":
            resp_fields = resp_field_set[0]
            resp['field'] = resp_fields
        if len(resp_field_set) >= 2:
            for field in resp_field_set[1:]:
                resp_fields = resp_fields + ", " + field
            resp['field'] = resp_fields
        if "field" in resp.keys() and resp['field'] != "" and (
                                                resp_fields != "dateAndTime"):
            error_message = error_message + "Fields should not be empty."

        # Return appropriate codes as 400, 401, 403
        if "field" in resp.keys():
            """
            Bad request with error message constructed above
            if there is any missing field
            """
            resp['errorCode'] = "400"
            resp['errorMessage'] = error_message
            return resp, status.HTTP_400_BAD_REQUEST
        elif api_key != message_api_key:
            # Return the invalid request error if api key is incorrect
            resp['errorCode'] = "401"
            resp['errorMessage'] = "Invalid Credentials."
            return resp, status.HTTP_401_UNAUTHORIZED
        elif not valid:
            # If the distribution list (email id/ slack message id) is invalid
            resp['errorCode'] = "403"
            resp['errorMessage'] = "Due to invalid " + field + \
                                   ", request has been blocked."
            return resp, status.HTTP_403_FORBIDDEN
        else:
            """
            If all the required fields are valid,
            then check the optional fields
            Construct the full message that needs to be send
            after validation of required and optional fields
            """
            if "attempt" in content.keys() and \
                    "exceptionDetails" in content.keys():
                # Keep number of attempts taken by API to retry
                # Keep exception details thrown by the requested API
                message = str(title) + '\n' + str(message_text) + \
                          '\n`Date And Time:` ' + date_and_time + \
                          ',    `Id:` ' + str(id) + \
                          ',    `attempt:` ' + str(attempt) + \
                          '\n`Message Type:` ' + str(message_type) + \
                          '\n`Exception Details:` ```' + \
                          str(exception_details) + '```\n'
            elif "attempt" not in content.keys() and \
                    "exceptionDetails" not in content.keys():
                # If there is no attempt and exception details fields
                message = str(title) + '\n' + str(message_text) + \
                          '\n`Date And Time:` ' + date_and_time + \
                          ',    `Id:` ' + str(id) + \
                          '\n`Message Type:` ' + str(message_type)
            elif "attempt" not in content.keys():
                # If only exception details field is present
                message = str(title) + '\n' + str(message_text) + \
                          '\n`Date And Time:` ' + date_and_time + \
                          ',    `Id:` ' + str(id) + \
                          '\n`Message Type:` ' + str(message_type) + \
                          '\n`Exception Details:` ```' + \
                          str(exception_details) + '```\n'
            elif "exceptionDetails" not in content.keys():
                # If there is only attempt field is present
                message = str(title) + '\n' + str(message_text) + \
                          '\n`Date And Time:` ' + date_and_time + \
                          ',    `Id:` ' + str(id) + \
                          ',    `attempt:` ' + str(attempt) + \
                          '\n`Message Type:` ' + str(message_type)

            # Construct response of this API
            resp['title'] = "Message Delivered Successfully."
            resp['id'] = id
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            resp['dateAndTime'] = dt_string

            if true_channel is False:
                """
                If channel name is not present
                then do not include the channel name in the response message
                """
                final_resp = {'res': resp, 'message': message}
                return final_resp, status.HTTP_200_OK
            elif true_channel is True:
                """
                If channel name is present
                then include the channel name in the response message
                """
                final_resp = {'res': resp,
                              'message': message,
                              'true_channel': true_channel}
                return final_resp, status.HTTP_200_OK


def slack_check(channel_name, distribution_split_list, slack_channel_name):
    """
    Checking regex for slack member ids and slack channel name
    valid is for returning that channel and/or distribution list is valid
    true_channel is for returning channel name exists or not
    field is for the name for field name to be returned
    """
    valid = True
    true_channel = False
    regex = '^[a-zA-Z0-9]*$'
    field = ""
    # Checking whether only distributionList exists
    if ((len(distribution_split_list) == 0) or (
                                    len(distribution_split_list) > 0 and
                                    distribution_split_list[0] == "")) \
            and channel_name == "":
        field = "channelName/distributionList"

    """
    If there is invalid channel name and distribution list exists
    or distribution list doesn't match the regex
    """
    if channel_name not in slack_channel_name and channel_name != "":
        if len(distribution_split_list) == 0 or (
                                    len(distribution_split_list) > 0 and
                                    distribution_split_list[0] == ""):
            valid = False
        elif len(distribution_split_list) > 0 \
                and distribution_split_list[0] != "":
            for ids in distribution_split_list:
                if len(ids) != 9 or not re.search(regex, ids):
                    valid = False
                    break
    """
    If there is no channel name and distribution list exists
    or distribution list doesn't match the regex
    """
    if (channel_name == "") and (len(distribution_split_list) > 0 and
                                 distribution_split_list[0] != ""):
        for ids in distribution_split_list:
            if len(ids) != 9 or not re.search(regex, ids):
                valid = False
                break

    # If valid channel name and invalid distribution list
    if channel_name in slack_channel_name and (
                                    len(distribution_split_list) > 0 and
                                    distribution_split_list[0] != ""):
        valid = True
        for ids in distribution_split_list:
            if len(ids) != 9 or not re.search(regex, ids):
                true_channel = True
                break
    return valid, field, true_channel


def email_check(distribution_split_list):
    """
    Checking regex for email ids
    valid is for returning if distribution list is valid
    field is for the name for field name to be returned
    """
    valid = True
    field = ""

    "Possible regex types"
    regex_type1 = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    regex_type2 = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+[.]\w{2,3}$'

    # Extracting the email id list from list
    # Format for this value, abc <abc@xyz.com>
    email_ids = set()
    for ids in distribution_split_list:
        name, id = str(ids).split(" <")
        id = str(id).replace(">", "")
        email_ids.add(id)

    # Validating the regex for email ids
    if len(distribution_split_list) > 0 and distribution_split_list[0] == "":
        field = "distributionList"
    else:
        for ids in email_ids:
            # Validating against regex1
            if not re.search(regex_type1, ids):
                valid = False
                # Validating against regex1
                if not re.search(regex_type2, ids):
                    valid = False
                    break
                else:
                    valid = True
    return valid, field


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
    app.run(host='0.0.0.0', port=2000)
