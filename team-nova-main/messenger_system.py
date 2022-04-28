from abc import ABCMeta, abstractmethod, ABC
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import pandas as pd

# Account SID from twilio.com/console



class MyTwilioMessenger():
    def __init__(self, account_sid, auth_token):
        self.client = Client(account_sid, auth_token)
        self.from_number = "+16018005644"

    def send_mass_messages(self, df, if_superuser):
        message_sent = []
        message_receipts = []

        for idx, row in df.iterrows():
            try:
                msg = row['Message']
                number = row['Phone Number']
                tmp = False
                tmp_user = 'N/A'
                if if_superuser:
                    tmp = row['Has Phone Number']
                else:
                    tmp_user = row['Phone Number']
                if tmp or tmp_user is not 'N/A':
                    message = self.client.messages.create(
                        to=number,
                        from_=self.from_number,
                        body=msg)
                    print('message sent to {} {} @ {}'.format(row['First Name'], row['Last Name'], row['Phone Number']))
                    message_sent.append(True)
                    message_receipts.append(message.sid)

                else:
                    print('\t missing/invalid number for {} {}'.format(row['First Name'], row['Last Name']))

                    message_sent.append(False)
                    message_receipts.append("Missing/Invalid Phone Number")


            except TwilioRestException as e:
                print('\t could not send to {} {}'.format(row['First Name'], row['Last Name']))
                print('\t\t', e)
                message_sent.append(False)
                message_receipts.append("Twilio Could Not Send")


        df['Message Sent'] = message_sent
        df['Message Receipt'] = message_receipts
        return df