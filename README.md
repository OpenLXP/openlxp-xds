# Enterprise Course Catalog: OPENLXP-XDS


## Setup

To setup and run an XDS instance Docker-Compose files have been included to automate the process.

To start the system using Docker-Compose, run `docker-compose up` from this directory.

To stop the system use `docker-compose stop`.

`docker-compose down` will delete the containers, along with any data in them.

System settings can be passed into the Docker-Compose through an env file.

Once the system is running, you can access it through a web browser (by default it is available at http://localhost:8100).

Navigate to /admin (http://localhost:8100/admin) and login using the DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD variables.

Under Configurations, create a new XDS Configuration and a new XDSUI Configuration.

Other optional settings can also be configured through the admin portal.

### Update

To update an existing installation, pull the latest changes using git

Then restart the application using `docker-compose restart`

Occasionally some updates may require the application be rebuilt using `docker-compose up --build`, but this can also rebuild the database resulting in data loss

### Testing

To run the automated tests on the application run the command below

Test coverage information will be stored in an htmlcov directory

```bash
docker-compose --env-file .env run app sh -c "coverage run manage.py test && coverage html && flake8"
```

### Enviroment Variables

The list of required variables is below

#### DB_NAME

The name to give the database

```ini
DB_NAME=django
```

#### DB_USER

The name of the user to use when connecting to the database

When testing use root to allow the creation of a test database

```ini
DB_USER=root
```

#### DB_PASSWORD

The password for the user to access the database

```ini
DB_PASSWORD=password
```

#### DB_ROOT_PASSWORD

The password for the root user to access the database, should be the same as `DB_PASSWORD` if using the root user

```ini
DB_ROOT_PASSWORD=password
```

#### DB_HOST

The host name, IP, or docker container name of the database

```ini
DB_HOST=db
```

#### DJANGO_SUPERUSER_USERNAME

The username of the superuser that will be created in the application

```ini
DJANGO_SUPERUSER_USERNAME=admin
```

#### DJANGO_SUPERUSER_PASSWORD

The password of the superuser that will be created in the application

```ini
DJANGO_SUPERUSER_PASSWORD=password
```

#### DJANGO_SUPERUSER_EMAIL

The email of the superuser that will be created in the application

```ini
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

#### AWS_ACCESS_KEY_ID

The Access Key ID for AWS

```ini
AWS_ACCESS_KEY_ID=*********
```

#### AWS_SECRET_ACCESS_KEY

The Secret Access Key for AWS

```ini
AWS_SECRET_ACCESS_KEY=*********
```

#### AWS_DEFAULT_REGION

The region for AWS

```ini
AWS_DEFAULT_REGION=*********
```

#### SECRET_KEY_VAL

The Secret Key for Django

```ini
SECRET_KEY_VAL=*********
```

#### LOG_PATH

The path to the log file to use

```ini
LOG_PATH=/etc/debug.txt
```

#### ENTITY_ID

The Entity ID used to identify this application to Identity Providers when using Single Sign On 

```ini
ENTITY_ID=http://localhost
```

#### SP_PUBLIC_CERT

The Public Key to use when this application communicates with Identity Providers to use Single Sign On

```ini
SP_PUBLIC_CERT=************************************
```

#### SP_PRIVATE_KEY

The Private Key to use when this application communicates with Identity Providers to use Single Sign On

```ini
SP_PRIVATE_KEY=************************************
```

#### CERT_VOLUME

The path to the certificate (on the host machine) to use when connecting to AWS

```ini
CERT_VOLUME=C:/Users/johnsmith/Documents/dockerRun/cacert.pem
```


## Authentication

The environment variables `SP_PUBLIC_CERT`, `SP_PRIVATE_KEY` , and `SP_ENTITY_ID` must be defined (if using docker-compose the variables can be passed through).

Information on the settings for the authentication module can be found on the [OpenLXP-Authentication repo](https://github.com/OpenLXP/openlxp-authentication).


## Authorization

The setting `OPEN_ENDPOINTS` can be defined in the django settings file.
It is a list of strings (regex notation may be used) for URLs that should not check for authentication or authorization.


## Notification

`Add email configuration` : To create customized email notifications content.
    
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

    `HTML File` : Upload the HTML file here, this HTML file helps to beutify the email body.

    Please take the reference HTML file from the below path.

    https://github.com/OpenLXP/openlxp-notifications/blob/main/Email_Body.html

    In the above reference HTML file, feel free to add your HTML design for the email body.

        Note: Do not change the variables below as they display specific components in the email body.

        <p>{paragraph:}</p>
        {signature:}
        <a href="mailto: {email_us:}">
        <a href="{faq_url:}" >
        <a href="mailto: {unsubscribe:}">
