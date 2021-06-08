import logging

from core.management.utils.notification import send_notifications
from core.models import ReceiverEmailConfiguration, SenderEmailConfiguration
from django.conf import settings

logger = logging.getLogger('dict_config_logger')


def send_log_email(message):
    """ function to send emails of log file to personas"""

    # getting email id to send email to personas

    email_data = ReceiverEmailConfiguration.objects.values_list(
        'email_address',
        flat=True)
    email = list(email_data)
    # Getting sender email id
    sender_email_configuration = SenderEmailConfiguration.objects.first()
    sender = sender_email_configuration.sender_email_address
    # Write error message into a file
    write_error_message(message)
    send_notifications(email, sender)


def write_error_message(message):
    """ function to write error message into a log file """
    ATTACHMENT = getattr(settings, "LOG_PATH", None)
    with open(ATTACHMENT, 'w') as f:
        f.write(message)
