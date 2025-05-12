from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import send_bulk_email_with_ses
import logging
import re
import json

logger = logging.getLogger(__name__)


@csrf_exempt
def email_view_bulk(request):
    """View for handling bulk email sends via AWS SES."""
    logger.info("Email view called")

    if request.method == "POST":
        raw_input = request.POST.get("email", "")
        logger.debug(f"Raw data received: {raw_input}")

        # Process recipients from input
        recipients = parse_recipients(raw_input)

        if not recipients:
            logger.warning("No valid email/name pairs provided")
            return JsonResponse(
                {"message": "No valid email/name pairs provided."}, status=400
            )

        logger.info(f"Processed {len(recipients)} valid recipients")

        # Send bulk emails
        try:
            # First attempt to use the SES template if available
            response = send_bulk_email_with_ses(
                recipients=recipients,
                subject="Still Copy-Pasting Data Manually?",
                html_template="mailer/emailtemplate.html",  # This will be used if template send fails
                use_template=False,
                ses_template_name="YourSESTemplateName",
            )

            # Process results
            successful_emails = []
            failed_emails = []

            # Handle bulk templated email response structure
            if isinstance(response, dict) and "Status" in response:
                for status_item in response.get("Status", []):
                    recipient = status_item.get("Recipient")
                    if status_item.get("Status") == "Success":
                        successful_emails.append(recipient)
                    else:
                        failed_emails.append(recipient)

            # Handle individual email responses
            elif isinstance(response, list):
                for item in response:
                    if item.get("status") == "success":
                        successful_emails.append(item.get("email"))
                    else:
                        failed_emails.append(item.get("email"))

            logger.info(
                f"Email sending completed. Successful: {len(successful_emails)}, Failed: {len(failed_emails)}"
            )

        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return JsonResponse(
                {"message": f"Email sending failed: {str(e)}"}, status=500
            )

        # Prepare response data
        response_data = {
            "message": f"Email sending completed. {len(successful_emails)} successful, {len(failed_emails)} failed.",
            "successful_count": len(successful_emails),
            "failed_count": len(failed_emails),
            "successful": successful_emails[:10],
            "failed": failed_emails[:10],
        }

        # Add truncation indicators if needed
        if len(successful_emails) > 10:
            response_data["successful"].append("... and more")
        if len(failed_emails) > 10:
            response_data["failed"].append("... and more")

        return render(
            request,
            "mailer/send_email.html",
            context={"response_data": response_data},
        )

    # GET or other methods
    return render(request, "mailer/send_email.html")


def parse_recipients(raw_input):
    """
    Parse and validate a raw string of email/name pairs.

    Expected format can be combinations of:
    - "Name1 email1@example.com, Name2 email2@example.com"
    - "Name1 email1@example.com; Name2 email2@example.com"
    - Multiline variations

    Returns:
        List of dicts with 'name' and 'email' keys
    """
    # Normalize whitespace and split by common delimiters
    normalized_input = re.sub(r"\s+", " ", raw_input)
    raw_data = re.split(r"[,;\s]+", normalized_input)

    # Remove empty entries
    raw_data = [item for item in raw_data if item]
    logger.debug(f"Raw data after cleaning: {raw_data}")

    # Separate names and emails assuming alternating entries
    name_list = raw_data[::2]  # Every even index (0, 2, 4...)
    raw_emails = raw_data[1::2]  # Every odd index (1, 3, 5...)

    # Handle mismatched pairs
    min_length = min(len(name_list), len(raw_emails))
    name_list = name_list[:min_length]
    raw_emails = raw_emails[:min_length]

    logger.debug(f"Raw Names: {name_list}")
    logger.debug(f"Raw Emails: {raw_emails}")

    # Validate emails
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    recipients = []

    for name, email in zip(name_list, raw_emails):
        email = email.strip()
        if email_pattern.match(email):
            recipients.append({"email": email, "name": name.strip()})
        else:
            logger.warning(f"Invalid email format: {email}")

    return recipients
