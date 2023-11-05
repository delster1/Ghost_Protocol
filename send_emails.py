import os
import smtplib
from creds import exec_emails  # Replace with your actual file and variable
from location_details import location_details_string, get_location_details, city  # Replace with your actual file and variable

# Gmail credentials
gmail_user = 'jacearnoldmail@gmail.com'  # Replace with your actual email
gmail_password = os.environ.get('GMAIL_APP_PASSWORD')  # Replace with your actual password

# Email content
location = get_location_details()
subject = f'{city(location)}' #NEED TO CHANGE TO USE LOCATION DETAILS

body = location_details_string(location)

# Set up the SMTP server
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login(gmail_user, gmail_password)

# Send the email
for user in exec_emails:
    to = user
    email_text = f"From: {gmail_user}\nTo: {to}\nSubject: {subject}\n\n{body}"
    server.sendmail(gmail_user, to, email_text)


# Close the server
server.close()

print(subject)