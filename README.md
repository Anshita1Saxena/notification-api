# notification-api
This project demonstrates the interconnection of pods running on Kubernetes (k8s) cluster. Whenever the exception is raised by any microservice, then it will throw the alert on Slack and email.

## Description
This project is based on APIs. It shows the inconnection between several microservices running on cluster. There are three microservices implemented through this project listed as follows:

1. Validation: This API helps in validating the fields passed from the requested API. The validation covers date format checks, email checks through regex (regular expression), and total fields checking.
2. Slack: This API helps in posting message exceptions received from several microservices to Slack. It helps in proactive error and exception handling and remediation of problems occurred.
3. Email: This API helps in sending message exception received from several microservices to Email. It helps in proactive error and exception handling and remediation of problems occurred.

The other microservices calls the slack and email APIs in order to send the alerts on slack and email. The steps listed below are followed:
1. The request goes to two APIs: Slack and Email.
2. Slack and Email APIs send the message to the Validate API for the validation of fields, emails and date.
3. Validate API send the message back to Slack and Email APIs to post the exception as an alert and as a mail.
4. If the request is successfully validated, then the message send to Slack and Email. If the request is not successfully validated, then it will send the descriptive message along with the errors to user for correction of message.

Pictorial Representation of API Design:

![Pictorial Representation of API Design](https://github.com/Anshita1Saxena/notification-api/blob/main/demo-image/API%20Design.JPG)

Pictorial Representation of API Functionality:

![Pictorial Representation of API Functionality](https://github.com/Anshita1Saxena/notification-api/blob/main/demo-image/API%20Functionality.JPG)

Response Codes:

![Response Codes](https://github.com/Anshita1Saxena/notification-api/blob/main/demo-image/Response%20Codes.JPG)

