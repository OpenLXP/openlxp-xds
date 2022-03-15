# Enterprise Course Catalog: OPENLXP-XDS


# Prerequisites
`Python >=3.7` : Download and install python from here [Python](https://www.python.org/downloads/).

`Docker` : Download and install Docker from here [Docker](https://www.docker.com/products/docker-desktop).

`XML Security Headers` : Download and install XML Security Headers for your operating system (`libxml2-dev` and `libxmlsec1-dev` in some linux distros).


## Environment Variables

The list of required variables is below

`DB_NAME` - The name to give the database

`DB_USER` - The name of the user to use when connecting to the database.
When testing use root to allow the creation of a test database

`DB_PASSWORD` - The password for the user to access the database

`DB_ROOT_PASSWORD` - The password for the root user to access the database, should be the same as `DB_PASSWORD` if using the root user

`DB_HOST` - The host name, IP, or docker container name of the database

`DJANGO_SUPERUSER_USERNAME` - The username of the superuser that will be created in the application

`DJANGO_SUPERUSER_PASSWORD` - The password of the superuser that will be created in the application

`DJANGO_SUPERUSER_EMAIL` - The email of the superuser that will be created in the application

`AWS_ACCESS_KEY_ID` - The Access Key ID for AWS

`AWS_SECRET_ACCESS_KEY` - The Secret Access Key for AWS

`AWS_DEFAULT_REGION` - The region for AWS

`SECRET_KEY_VAL` - The Secret Key for Django

`LOG_PATH` - The path to the log file to use

`ENTITY_ID` - The Entity ID used to identify this application to Identity Providers when using Single Sign On 

`SP_PUBLIC_CERT` - The Public Key to use when this application communicates with Identity Providers to use Single Sign On

`SP_PRIVATE_KEY` - The Private Key to use when this application communicates with Identity Providers to use Single Sign On

`CERT_VOLUME` - The path to the certificate (on the host machine) to use when connecting to AWS


# Installation

1. Clone the Github repository:

    https://github.com/OpenLXP/openlxp-xds.git

2. Open terminal at the root directory of the project.
    
    example: ~/PycharmProjects/openlxp-xds 

3. Run command to install all the requirements from requirements.txt 
    
    docker-compose build.

4. Once the installation and build are done, run the below command to start the server.
    
    docker-compose up

5. Once the server is up, go to the admin page:
    
    http://localhost:8100/admin (replace localhost with server IP)


# Configuration

1. On the Admin page, log in with the admin credentials 


2. `Add xds configuration`: Configure Experience Discovery Service (XDS):
    
    `Default user group`: Select a group for new users to be assigned to automatically.

    `Target xis metadata api`: Metadata API Endpoint to connect to on an XIS instance.

    `Target xse host`: Hostname and port of XSE instance to use.

    `Target xse index`: Index of data to use on XSE instance.


3. `Add xdsui configuration`: Configure Experience Discovery Service - User Interface (XDS-UI): 

    `Search results per page`: Number of results that should be displayed on a search page on the UI.

    `Xds configuration`: Select the XDS Configuration to use.

    `Course img fallback`: Image to use if no image is supplied in the experience


4. `Add Saml configuration`: Configure Security Assertion Markup Language (SAML):
    
    `Name`: The name that will be used to identify the IdP in the URL.

    `Entity id`: The unique name provided by the IdP.

    `Url`: The connection URL to connect to the IdP at.

    `Cert`: The public cert used to connect to the IdP.

    `Attribute mapping`: The JSON formatted mapping to convert attributes provided by the IdP, to a User in this system.


5. `Add course spotlight`: Configure Spotlight Courses in XDS-UI:

    `Course id`: The ID of the course to add.

    `Active`: Whether this course should be shown in the Spotlight Courses section.


6. `Add search filter`: Configure Search Filters in XDS-UI:

    `Display name`: The name to use to label the filter in the UI.

    `Field name`: The name of the field in ElasticSearch.

    `Xds ui configuration`: Select the XDS UI Configuration to use.

    `Filter type`: The type of filter to use.

    `Active`: Whether this filter should be shown in the search results page.


7. `Add sender email configuration`: Configure the sender email address from which conformance alerts are sent.


8. `Add receiver email configuration` : 
Add an email list to send conformance alerts. When the email gets added, an email verification email will get sent out. In addition, conformance alerts will get sent to only verified email IDs.


9. `Add email configuration` : To create customized email notifications content.
    
    `Subject`:  Add the subject line for the email. The default subject line is "OpenLXP Conformance Alerts."

    `Email Content`: Add the email content here. The  Email Content is an optional field. 	
        Note: When the log type is Message, Message goes in this field. 

    `Signature`: Add Signature here.

    `Email Us`: Add contact us email address here.

    `FAQ URL` : Add FAQ URL here.

    `Unsubscribe Email ID`: Add email ID to which Unsubscriber will send the emails.

    `Logs Type`: Choose how logs will get sent to the Owners/Managers. Logs can be sent in two ways Attachment or Message.

    For Experience Index Agents, and Experience Index Services, choose Attachment as a log type.

    For Experience Management Service and Experience discovery services, choose Message as a log type. 

    `HTML File` : Upload the HTML file here, this HTML file helps to beautify the email body.

    Please take the reference HTML file from the below path.

    https://github.com/OpenLXP/openlxp-notifications/blob/main/Email_Body.html

    In the above reference HTML file, feel free to add your HTML design for the email body.

        Note: Do not change the variables below as they display specific components in the email body.

        <p>{paragraph:}</p>
        {signature:}
        <a href="mailto: {email_us:}">
        <a href="{faq_url:}" >
        <a href="mailto: {unsubscribe:}">


# Troubleshooting

A good basic troubleshooting step is to use `docker-compose down` and then `docker-compose up --build` to rebuild the app image; however, this will delete everything in the database.

## XMLSEC

If the build fails when pip tries to install xmlsec, the issue is usually missing libraries.

The xmlsec package includes instructions for installing the libraries on common platforms in the [documentation](https://github.com/mehcode/python-xmlsec/blob/master/README.rst#install)

## Line Endings

If the container builds but crashes or logs an error of unrecognized commands, the issue is usually incorrect line endings.

Most IDEs/Text Editors allow changing the line endings, but the dos2unix utility can also be used to change the line endings of `start-app.sh` and `start-server.sh` to LF.


# Update

To update an existing installation: 

1. Pull the latest changes using git

2. Restart the application using `docker-compose restart`

# Testing

To run the automated tests on the application run the command below

Test coverage information will be stored in an htmlcov directory

```bash
docker-compose --env-file .env run app sh -c "coverage run manage.py test && coverage html && flake8"
```

# Authentication

The environment variables `SP_PUBLIC_CERT`, `SP_PRIVATE_KEY` , and `SP_ENTITY_ID` must be defined (if using docker-compose the variables can be passed through).

Information on the settings for the authentication module can be found on the [OpenLXP-Authentication repo](https://github.com/OpenLXP/openlxp-authentication).


# Authorization

The setting `OPEN_ENDPOINTS` can be defined in the django settings file.
It is a list of strings (regex notation may be used) for URLs that should not check for authentication or authorization.