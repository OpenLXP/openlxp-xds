# Openlxp XDS Setup & Configuration
Expand the following drop down to see the steps for configuring the ECC Openlxp XDS.

# Configuration

## Steps to Configure the ECC XDS

1. **Go to the admin page http://localhost:8100/admin**
    - Log in with the admin credentials 


2. **`Add xds configuration`: Configure Experience Discovery Service (XDS)**
    
     - `Default user group`: Select a group for new users to be assigned to automatically.
     - `Target xis metadata api`: Metadata API Endpoint to connect to on an XIS instance.
     - `Target xse host`: Hostname and port of XSE instance to use.
     - `Target xse index`: Index of data to use on XSE instance.


3. **`Add xdsui configuration`: Configure Experience Discovery Service - User Interface (XDS-UI)** 

     - `Search results per page`: Number of results that should be displayed on a search page on the UI.

     - `Xds configuration`: Select the XDS Configuration to use.

     - `Course img fallback`: Image to use if no image is supplied in the experience


4. **Configure SAML**
    - On the django admin page click on the `Add Saml configuration` button to configure the SAML and fill out the following fields.
    - **Note: Please make sure to upload schema file in the Experience Schema Server (XSS).**
    
    </br>

    | Django Admin Field  | Configuration Field Description |
    | ------------- | ------------- |
    | Name | Metadata API Endpoint to connect to on an XIS instance  |
    | Entity id     | Catalogs API Endpoint to connect to on an XIS instance.|
    | Url     | Catalogs API Endpoint to connect to on an XIS instance.|
    | Cert     | Catalogs API Endpoint to connect to on an XIS instance.|
    | Attribute Mapping     | Catalogs API Endpoint to connect to on an XIS instance.|

    </br>


5. **Configure Spotlight Courses in XDS-UI**

    - On the django admin page click on the `Add course spotlight` button to configure the SAML and fill out the following fields.
    
    </br>

    | Django Admin Field  | Configuration Field Description |
    | ------------- | ------------- |
    | Course id  | The ID of the course to add.  |
    | Active     | Whether this course should be shown in the Spotlight Courses section.|

    </br>


6. **Configure Search Filters in XDS-UI**
    - On the django admin page click on the `Add search filter` button to configure the SAML and fill out the following fields.

    </br>

    | Django Admin Field  | Configuration Field Description |
    | ------------- | ------------- |
    | Display name | The name to use to label the filter in the UI.  |
    | Field name     | The name of the field in ElasticSearch.|
    | Xds ui configuration     | Select the XDS UI Configuration to use.|
    | Filter type     | The type of filter to use.|
    | Active     | Whether this filter should be shown in the search results page|

    </br>



7. **Configure the ECC XDS Email Sender, Receiver, and Email Content**

    | Django Admin Field  | Configuration Field Description |
    | ------------- | ------------- |
    | `Add sender email configuration` |  Configure the sender email address from which conformance alerts are sent. |
    | `Add receiver email configuration` | Add an email list to send conformance alerts. When the email gets added, an email verification email will get sent out. In addition, conformance alerts will get sent to only verified email IDs.  |
    | `Add email configuration` | To create customized email notifications content.  |

     </br>


    - **Add email configuration**

    </br>

    | XDS Email Configuration Fields  | Configuration Field Description |
    | ------------- | ------------- |
    | Subject | Add the subject line for the email. The default subject line is "OpenLXP Conformance Alerts.  |
    | Email Content     | Add the email content here. The  Email Content is an optional field. </br> </br>  Note: When the log type is Message, Message goes in this field. |
    | Signature     | Add Signature here.|
    | Email Us     | Add contact us email address here.|
    | FAQ URL     | Add FAQ URL here.|
    | Unsubscribe Email ID     | Add email ID to which Unsubscriber will send the emails.|
    | Logs Type    | Choose how logs will get sent to the Owners/Managers. Logs can be sent in two ways Attachment or Message.|
    | FAQ URL     | Add FAQ URL here.|

    For Experience Management Service and Experience discovery services, choose Message as a log type.

    | Django Admin Field  | Configuration Field Description |
    | ------------- | ------------- |
    |HTML File | Upload the HTML file here, this HTML file helps to beautify the email body.  |

    - Please take the reference HTML file from the below path.

        - https://github.com/OpenLXP/openlxp-notifications/blob/main/Email_Body.html

        - In the above reference HTML file, feel free to add your HTML design for the email body.

            - Note: Do not change the variables below as they display specific components in the email body.
            </br> </br>
            
            ```
            <p>{paragraph:}</p>
            {signature:}
            <a href="mailto: {email_us:}">
            <a href="{faq_url:}" >
            <a href="mailto: {unsubscribe:}">

    </br>


## Troubleshooting the ECC XDS

A good basic troubleshooting step is to use `docker-compose down` and then `docker-compose up --build` to rebuild the app image; however, this will delete everything in the database.

| Troubleshooting  | Description |
| ------------- | ------------- |
| XMLSEC | If the build fails when pip tries to install xmlsec, the issue is usually missing libraries. </br> </br> The xmlsec package includes instructions for installing the libraries on common platforms in the [documentation](https://github.com/mehcode/python-xmlsec/blob/master/README.rst#install)  |
| Line Endings      |  If the container builds but crashes or logs an error of unrecognized commands, the issue is usually incorrect line endings.</br> </br> Most IDEs/Text Editors allow changing the line endings, but the dos2unix utility can also be used to change the line endings of `start-app.sh` and `start-server.sh` to LF.|


##  Updating the ECC XDS

To update an existing installation: 

1. Pull the latest changes using git

2. Restart the application using `docker-compose restart`


##  ECC XDS Authentication

The environment variables `SP_PUBLIC_CERT`, `SP_PRIVATE_KEY` , and `SP_ENTITY_ID` must be defined (if using docker-compose the variables can be passed through).

Information on the settings for the authentication module can be found on the [OpenLXP-Authentication repo](https://github.com/OpenLXP/openlxp-authentication).


##  ECC XDS Authorization

The setting `OPEN_ENDPOINTS` can be defined in the django settings file.
It is a list of strings (regex notation may be used) for URLs that should not check for authentication or authorization.

