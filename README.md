# Notifly
Notifly is a python web application that leverages google chart data analytics and Twilio API to provide more visibility on medical readiness status for the Hickam Medical Group and Unit Managers (UDMs/UHMs). The workflow is broken down in the “Users and Workflows'' section below. The functionality is to allow users to view data analytics and also send SMS notifications to all airmen with items due.

Techincal Requirements:
```angular2html
sudo apt-get update
sudo apt install python3-pip
pip3 install -r requirements.txt
```

For the Twilio API, you need an account_sid and auth_token to run the application

How to run:
```angular2html
python3 app.py [account_sid] [auth_token]
```
