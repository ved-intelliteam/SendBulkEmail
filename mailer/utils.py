

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_email(receiver_mail,receiver_name, verification_url=None, Subject=None, Message=None, user=None, html_template=None):
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
    from_email = "info@docextract.ai"
    subject = Subject or "Verify your Email - DocExtract"
    text_message = Message or f"Email Verification Link: {verification_url}"
    receiver_email = [receiver_mail]

    # Render HTML content from the template
    if html_template:
        print("template is available")
        html_message = render_to_string(
            html_template,
            {"name": receiver_name.title(), "current_year": 2025}
        )

    # Compose and send the email
    print("sending email")
    email = EmailMultiAlternatives(subject, text_message, from_email, receiver_email)
    if html_template:
        email.attach_alternative(html_message, "text/html")
    email.send()

    print(f"HTML email sent to {receiver_email} using template {html_template}")