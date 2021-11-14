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

## Advantages

1. Proactive actions on exceptions
2. Quick remediation of problems (raised errors and exceptions)
3. Reduced login to the servers
4. Reduced time for investigation of exceptions

## Environment Details
Validation, Slack, and Email APIs are deployed on Kubernetes(k8s) cluster as a pod. The following high level steps are listed below:

1. These APIs are developed in Flask framework.
2. APIs are wrapped in docker containers.
3. Docker Images are pushed in JFrog Artifactory.
4. Prepared Deployment yaml files for running as pods on Kubernetes
5. Deployed these services on Kubernetes

Base python version for docker container is 3.6
All three services are placed in `validation`, `slack`, and `email` directories with the `Dockerfile` file for creating the docker images, `.ini` files for properties required to run an application, `requirements.txt` file with required packages, and `.py` files for python application, and `.yaml` files are deployment files for deploying the application on k8s cluster.
Kubernetes cluster runs on Red Hat bare metal servers. Docker is installed on bare metal to build, tag, and push the images to JFrog Artifactory or Docker Hub. This project is currently working in Production and JFrog Artifactory is used for keeping docker images in the repository.

## Working Details
This implementation deployed three replicas of these three microservices on three different for supporting high availability.
For deploying these services on top of kubernetes, there are two main steps listed below:

1. Docker Images: Build, tag, and push docker images into the repository
2. Kubernetes Commands: Deploy the services on k8s cluster with the help of secret command, service.yaml file, and deployment.yaml file.

**1. Docker Images:**

1. Build the docker image:

    * Validation- `docker build -t validationservice:latest .`
    * Slack- `docker build -t slackservice:latest .`
    * Email- `docker build -t emailservice:latest .`

2. Login to the Docker Hub or JFrog Artifactory.

    * For JFrog Artifactory, command is written below:
    
    `docker login -u <your-user-name> -p <your-password> https://<your-repository-domain>`

    * For docker.io, command is written below:
     
    `docker login docker.io --username=<your-user-name> --password=<your-password> --email=<your-email-address>`

3. Tagging the images:

    * Validation- `docker tag validationservice:latest <your-repository-domain>/validationservice:latest`
    * Slack- `docker tag slackservice:latest <your-repository-domain>/slackservice:latest`
    * Email- `docker tag emailservice:latest <your-repository-domain>/emailservice:latest`

4. Pushing the images to the Docker Hub or JFrog Artifactory.

    * Validation- `docker push <your-repository-domain>/validationservice:latest`
    * Slack- `docker push <your-repository-domain>/slackservice:latest`
    * Email- `docker push <your-repository-domain>/emailservice:latest`

**2. Kubernetes Commands:**
1. Creating and viewing namespace in kubernetes:

    `kubectl create namespace alerts`
    
    `kubectl get namespaces`

2. Create all three different directories:

    * Validation- `mkdir validation`
    * Slack- `mkdir slack`
    * Email- `mkdir email`

3. Keep `.ini` file for creating secrets, `service.yaml` file for creating service, and `deployment.yaml` file for creating deployments.

4. Creating and viewing secrets:
    
    *Creating Secrets-*

    * Validation- `kubectl create secret generic application.ini --from-file application.ini -n alerts`
    * Slack- `kubectl create secret generic mainapp.ini --from-file mainapp.ini -n alerts`
    * Email- `kubectl create secret generic emailapp.ini --from-file emailapp.ini -n alerts`

    *Viewing Secrets-*

    `kubectl get secrets -n alerts`

5. Creating and viewing services:

    *Creating Services-*

    * Validation- `kubectl create -f service.yaml -n alerts`
    * Slack- `kubectl create -f service.yaml -n alerts`
    * Email- `kubectl create -f service.yaml -n alerts`

    *Viewing Services-*

    `kubectl get svc -n alerts`

6. Creating and viewing deployments:

    *Creating deployments-*

    * Validation- `kubectl create -f deployment.yaml -n alerts`
    * Slack- `kubectl create -f deployment.yaml -n alerts`
    * Email- `kubectl create -f deployment.yaml -n alerts`

    *Viewing deployments-*

    `kubectl get deployments -n alerts`

7. Get all kinds existed under `alerts` namespace-

    `xxxxxxxxx-xxxxx`and `xxxxxxxxx` signify the id assigned by kubernetes while creation of pod in `pod/email-python`, `pod/slack-python`, `pod/validation-python` and creation of replicasets in `replicaset.apps/email-python`, `replicaset.apps/slack-python`, `replicaset.apps/validation-python`. Cluster-IP is the ip address assigned to services by kubernetes. 

        kubectl get all -n alerts
        NAME                                    READY   STATUS    RESTARTS   AGE
        pod/email-python-xxxxxxxxx-xxxxx        1/1     Running   0          79s
        pod/email-python-xxxxxxxxx-xxxxx        1/1     Running   0          79s
        pod/email-python-xxxxxxxxx-xxxxx        1/1     Running   0          79s
        pod/slack-python-xxxxxxxxx-xxxxx        1/1     Running   0          79s
        pod/slack-python-xxxxxxxxx-xxxxx        1/1     Running   0          79s
        pod/slack-python-xxxxxxxxx-xxxxx        1/1     Running   0          79s
        pod/validation-python-xxxxxxxxx-xxxxx   1/1     Running   0          79s
        pod/validation-python-xxxxxxxxx-xxxxx   1/1     Running   0          79s
        pod/validation-python-xxxxxxxxx-xxxxx   1/1     Running   0          79s


        NAME                     TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
        service/email-app        NodePort   10.107.24.16     <none>        80:30308/TCP   8m30s
        service/slack-app        NodePort   10.110.175.227   <none>        80:30307/TCP   8m30s
        service/validation-app   NodePort   10.101.107.57    <none>        80:30306/TCP   8m30s


        NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
        deployment.apps/email-python        3/3     3            3           79s
        deployment.apps/slack-python        3/3     3            3           79s
        deployment.apps/validation-python   3/3     3            3           79s

        NAME                                          DESIRED   CURRENT   READY   AGE
        replicaset.apps/email-python-xxxxxxxxx        3         3         3       79s
        replicaset.apps/slack-python-xxxxxxxxx        3         3         3       79s
        replicaset.apps/validation-python-xxxxxxxxx   3         3         3       79s

## Highlights
1. Python Microservices
2. Dockerization and Containerization Concepts
3. Integration of Mail and Slack
4. Deployment of interconnected APIs on Kubernetes (k8s)

## Demo Screenshots
Slack Alert API Screenshot:
![Slack Message Alert by API.JPG](https://github.com/Anshita1Saxena/notification-api/blob/main/demo-image/Slack%20Message%20Alert%20by%20API.JPG)

Email Alert API Screenshot:
![Mail Alert by API.JPG](https://github.com/Anshita1Saxena/notification-api/blob/main/demo-image/Mail%20Alert%20by%20API.JPG)
