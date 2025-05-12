from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import json


def send_email(
    receiver_mail,
    receiver_name,
    verification_url=None,
    Subject=None,
    Message=None,
    user=None,
    html_template=None,
):
    """
    Send an email with a verification link using a custom HTML template.

    Args:
        receiver_mail (str): The email address of the recipient.
        verification_url (str): The verification URL to be included in the email.
        Subject (str, optional): Optional subject override.
        Message (str, optional): Optional plain text message.
        user (CustomUser, optional): The user object for personalized content.
        html_template (str): Path to the HTML template.

    Returns:
        None
    """
    print("got call for mailer utility function ")
    from_email = "ved@docextract.ai"
    subject = Subject or "Verify your Email - DocExtract"
    text_message = Message or f"Email Verification Link: {verification_url}"
    receiver_email = [receiver_mail]

    # Render HTML content from the template
    if html_template:
        print("template is available")
        html_message = render_to_string(
            html_template, {"name": receiver_name.title(), "current_year": 2025}
        )

    # Compose and send the email
    print("sending email")
    email = EmailMultiAlternatives(subject, text_message, from_email, receiver_email)
    if html_template:
        email.attach_alternative(html_message, "text/html")
    email.send()

    print(f"HTML email sent to {receiver_email} using template {html_template}")


import json
import boto3
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Initialize boto3 client once
SES_CLIENT = boto3.client(
    "ses",
    aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
    aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
    region_name="ap-south-1",
)


import json
import boto3
from django.conf import settings
from django.template.loader import render_to_string


import json
import boto3
import logging
from django.conf import settings
from django.template.loader import render_to_string


def send_bulk_email_with_ses(
    recipients,
    subject: str = None,
    message: str = None,
    html_template: str = None,
    use_template: bool = False,
    ses_template_name: str = None,
):
    """
    Sends emails to multiple recipients via AWS SES (boto3 only).

    Args:
      recipients: List of dicts, each with keys 'email' and 'name'.
      subject: Email subject override.
      message: Plain-text message override (applies to all recipients).
      html_template: Path to a local Django HTML template.
      use_template: If True, uses a stored SES template.
      ses_template_name: Name of the SES template to use (for bulk sends).

    Returns:
      The boto3 response: send_bulk_templated_email or list of individual send_email responses.
    """
    default_subject = "Still Copy-Pasting Data Manually?"
    subject = subject or default_subject

    # Configure logging
    logger = logging.getLogger(__name__)
    logger.info(f"Sending emails to {len(recipients)} recipients")

    # Prepare bulk templated email payload
    if use_template and ses_template_name:
        logger.info(f"Using SES template: {ses_template_name}")
        destinations = []
        for rec in recipients:
            # build individual replacement data
            data = {"name": rec["name"].title()}
            destinations.append(
                {
                    "Destination": {"ToAddresses": [rec["email"]]},
                    "ReplacementTemplateData": json.dumps(data),
                }
            )
        try:
            response = SES_CLIENT.send_bulk_templated_email(
                Source=settings.DEFAULT_FROM_EMAIL,
                Template=ses_template_name,
                DefaultTemplateData=json.dumps({"name": "there"}),
                Destinations=destinations,
            )
            logger.info(f"Bulk email sent successfully")
            return response
        except Exception as e:
            logger.error(f"Error sending bulk email: {str(e)}")
            raise

    # Fallback: loop through recipients one-by-one using the provided HTML template
    logger.info(f"Sending individual emails using template: {html_template}")
    responses = []
    for rec in recipients:
        context = {"name": rec["name"].title()}
        try:
            # Generate text version from the template if available
            text_body = message
            if not text_body and html_template:
                try:
                    text_template = html_template.replace(".html", ".txt")
                    text_body = render_to_string(text_template, context)
                except Exception as text_err:
                    logger.warning(f"Could not render text template: {str(text_err)}")
                    # Create simple text version from HTML as fallback
                    text_body = f"Hello {rec['name'].title()},\n\nPlease check out our service.\n\n"
                    text_body += "Regards,\nThe Team"

            # Generate HTML body
            html_body = (
                render_to_string(html_template, context) if html_template else None
            )

            email_params = {
                "Source": settings.DEFAULT_FROM_EMAIL,
                "Destination": {"ToAddresses": [rec["email"]]},
                "Message": {
                    "Subject": {"Data": subject},
                    "Body": {},
                },
            }

            # Add text and HTML bodies as available
            if text_body:
                email_params["Message"]["Body"]["Text"] = {"Data": text_body}
            if html_body:
                email_params["Message"]["Body"]["Html"] = {"Data": html_body}

            response = SES_CLIENT.send_email(**email_params)
            responses.append(
                {"email": rec["email"], "status": "success", "response": response}
            )
            logger.info(f"Email sent to {rec['email']}")
        except Exception as e:
            error_message = str(e)
            logger.error(f"Failed to send email to {rec['email']}: {error_message}")
            responses.append(
                {"email": rec["email"], "status": "failed", "error": error_message}
            )

    return responses
