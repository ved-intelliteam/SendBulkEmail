from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .utils import send_email
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import logging




import re


@csrf_exempt
def email_view_bulk(request):
    print("email view called ")
    if request.method == "POST":
        raw_input = request.POST.get("email", "")
        print(f"Raw data received: {raw_input}")

        # Process the pasted text to extract emails
        # This handles newlines, commas, tabs, and spaces as separators

        # First, replace all tabs and multiple spaces with a single space
        normalized_input = re.sub(r"\s+", " ", raw_input)
        

        # Then split by common delimiters (comma and space)
        raw_data = re.split(r"[,;\s]+", normalized_input)
        if len(raw_data)==0:
            return JsonResponse({"message":"please give some input"})
        if raw_data[len(raw_data)-1]=='':
            del raw_data[len(raw_data)-1]
        if raw_data[0]=='':
            del raw_data[0]
        
        
        print(f"raw_data after cleaning:{raw_data}")
        raw_emails=[]
        name_list=[]
        for i in range(0,len(raw_data)):
            if i%2!=0  :
               raw_emails.append(raw_data[i])
            else:
                name_list.append(raw_data[i])
            

        
        print(f"Raw Emails are:{raw_emails}")
        print(f"Raw Names are:{name_list}")

        # Filter and clean up email addresses
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        
        if len(raw_emails)!= len(name_list):
            return JsonResponse({"message":"incomplete data"},status=200)
        
        email_list=[]

        for i in range(0,len(name_list)):
            current_raw_email=raw_emails[i]
            if  not email_pattern.match(current_raw_email.strip()):
                del name_list[i]
            else:
                email_list.append(current_raw_email.strip())

        print(f" Emails are:{email_list}")
        print(f" Names are:{name_list}")

        



        

        # email_list = [
        #     email.strip()
        #     for email in raw_emails
        #     if email.strip() and email_pattern.match(email.strip())
        # ]

        print(f"Extracted {len(email_list)} valid emails from input")

        successful_emails = []
        failed_emails = []
        print(f"Sending emails to {len(email_list)} recipients")
        print(f"Email list: {email_list}")

        # Send emails

        for i in range(0,len(name_list)):
            email=email_list[i]
            name=name_list[i]

            try:
                send_email(
                    receiver_mail=email,
                    receiver_name=name,
                    verification_url=None,
                    Subject="Still Copy-Pasting Data Manually?",
                    html_template="mailer/emailtemplate.html",
                )
                successful_emails.append(email)
                print(f"Email sent successfully to: {email}")
            except Exception as e:
                failed_emails.append(email)
                print(f"Failed to send email to {email}: {str(e)}")

        # for email in email_list:
        #     try:
        #         send_email(
        #             receiver_mails=email,
        #             receiver_names=name_list,
        #             verification_url=None,
        #             Subject="Still Copy-Pasting Data Manually?",
        #             html_template="mailer/emailtemplate.html",
        #         )
        #         successful_emails.append(email)
        #         print(f"Email sent successfully to: {email}")
        #     except Exception as e:
        #         failed_emails.append(email)
        #         print(f"Failed to send email to {email}: {str(e)}")

        # Provide detailed feedback
        response_data = {
            "message": f"Email sending completed. {len(successful_emails)} successful, {len(failed_emails)} failed.",
            "successful_count": len(successful_emails),
            "failed_count": len(failed_emails),
            "successful": successful_emails[:10],  # Limit the list size in the response
            "failed": failed_emails[:10],
        }

        if len(successful_emails) > 10:
            response_data["successful"].append("... and more")

        if len(failed_emails) > 10:
            response_data["failed"].append("... and more")

        return render(
            request,
            "mailer/send_email.html",
            context={"response_data": response_data},
        )

    else:
        return render(request, "mailer/send_email.html")

