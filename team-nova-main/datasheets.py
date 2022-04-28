import numpy as np
import phonenumbers as phone
from datasheetsexception import DatasheetsException
from datasheets_lib import *

class Datasheet:

    def __init__(self, account_sid, auth_token):
        self.messenger_system = MyTwilioMessenger(account_sid, auth_token)
        self.imr_df = None
        self.due_df = None
        self.contact_df = None
        self.invalid_contact_df = None
        self.due_df_with_contact = None
        self.due_df_with_msg = None

    def process_upload_from_asims(self, csv_filename, is_superuser):
        imr_df_raw = get_sheet(csv_filename)
        imr_df = get_reformatted_imr_sheet(imr_df_raw, is_superuser)
        due_df = query_imr_sheet(imr_df, due=True)
        self.imr_df = imr_df
        self.due_df = due_df
        return imr_df, due_df

    def get_data_analytics(self):
        imr_category_df = query_imr_sheet(self.due_df, imr_category=True)
        category_df = imr_category_df.groupby('Category').sum()

        category_df.reset_index(level=0, inplace=True)
        category_count = [['Category', 'Count']] + category_df.to_numpy().tolist()

        categories = set(list(imr_category_df['Category']))
        items_count = dict()
        for c in categories:
            specific_category_df = imr_category_df[imr_category_df['Category'] == c]
            items_count[c] = [['Item', 'Count']] + [[item[0], item[1]] for item in specific_category_df.to_numpy().tolist()]
            
        return category_count, items_count



    def process_upload_for_contact(self, csv_filename):
        try:
            contact_df = get_sheet(csv_filename)
            contact_df_cleaned = clean_contact_sheet(contact_df)
            self.contact_df = contact_df_cleaned
            self.due_df_with_contact = self.__join_sheets()
            return self.due_df_with_contact
        except Exception as e:
            print(e)
            raise DatasheetsException(e)

    def __join_sheets(self):
        try:
            due_df_with_contact = self.due_df.merge(self.contact_df, how='left', on=['First Name', 'Last Name'])
            due_df_with_contact['Has Phone Number'] = due_df_with_contact['Phone Number'].notna()
            return due_df_with_contact
        except KeyError as e:
            msg = "Key Error for " + str(e)
            raise DatasheetsException(msg)

    def message_display_df(self):
        self.due_df_with_contact = self.due_df_with_contact.sort_values(by=['Has Phone Number', 'IMR', 'Last Name', 'First Name'],ascending=[False, True, True, True])
        return self.due_df_with_contact[['First Name', 'Last Name', 'Unit', 'IMR', 'All Items Due', 'Has Phone Number']]

    def user_message_display_df(self):
        self.due_df_with_contact = self.due_df
        print("in datasehets")
        print(self.due_df_with_contact)
        return self.due_df_with_contact[['First Name', 'Last Name', 'Unit', 'IMR', 'All Items Due', 'Phone Number']]


    def send_messages(self, is_superuser):
        self.due_df_with_contact = make_sms_messages(self.due_df_with_contact)
        self.due_df_with_msg =  self.messenger_system.send_mass_messages(self.due_df_with_contact, is_superuser)
        due_df_with_failed_msg = self.due_df_with_msg.loc[self.due_df_with_msg['Message Sent'] == False]
        return due_df_with_failed_msg[['First Name', 'Last Name', 'Unit']]

def main():
    datasheet = Datasheet()
    is_superuser = True
    datasheet.process_upload_from_asims('test-sheets/superuser_asims_sheet-sample.csv', is_superuser)
    return datasheet

def main_data_analytics():
    datasheet = main()
    datasheet.process_upload_for_contact('test-sheets/superuser_contact_sheet-sample.csv')
    main_chart_data, little_chart_data = datasheet.get_data_analytics()

def main_messaging():
    datasheet = main()
    datasheet.process_upload_for_contact('test-sheets/superuser_contact_sheet-sample.csv')
    display_table = datasheet.message_display_df()
    datasheet.send_messages()  # this sends SMSs to all the airmen in main_df

if __name__ == "__main__":
    # main_messaging()
    main_data_analytics()
    print("main")