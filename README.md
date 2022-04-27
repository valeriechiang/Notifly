# Notifly
Notifly is a python web application that leverages google chart data analytics and Twilio API to provide more visibility on medical readiness status for the Hickam Medical Group and Unit Managers (UDMs/UHMs). The workflow is broken down in the “Users and Workflows'' section below. The functionality is to allow users to view data analytics and also send SMS notifications to all airmen with items due.

Techincal Requirements:
● sudo apt-get update
● sudo apt install python3-pip
● pip3 install flask
● pip3 install pandas
● pip3 install flask_session
● Twillio account-You need an account_sid and auth_token to run the application

How to run:
1)Clone the GitHub repository
2)Change directories until you are in the team nova directory
3)Type into the command line: python3 app.py [account_sid] [auth_token]
4)Follow the link to launch the web application
