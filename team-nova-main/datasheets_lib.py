import os
import pandas as pd
import pandas.errors

from messenger_system import MyTwilioMessenger
from imr_sheet import query_imr_sheet
import numpy as np
import phonenumbers as phone
from datasheetsexception import DatasheetsException

def get_sheet(file):
    if type(file) == str:
        filename = file
    else:
        filename = file.filename
    ext = os.path.splitext(filename)[-1].lower()

    if ext != ".csv":
        raise DatasheetsException("Incorrect File Format. Please upload .csv file.")

    try:
        df = pd.read_csv(file)
        return df
    except pandas.errors.ParserError as e:
        raise DatasheetsException("Cannot parse csv file. Please check your format.")
    except FileNotFoundError as e:
        raise DatasheetsException("File Not Found.")


def f(row):
    """
    takes the record of one airman and determines:
    - the IMR categories that they have left to complete
    - all IMR categories that they are due for
    - if they are due for requirements on their behalf
    """

    record = dict(row)
    actions = record['Action List']

    items_due_for_airman = []
    if record['IMR'] == 'G':
        if 'PHAQ' in actions or 'MHA' in actions:
            items_due_for_airman.append('PHA')
    else:
        if record['Imm'] == 'R' or record['Imm'] == 'Y':
            items_due_for_airman.append('Immunization(s)')
        if record['Lab'] == 'R' or record['Lab'] == 'Y':
            items_due_for_airman.append('Lab Screening(s)')
        if 'Blood' in record and (record['Blood'] == 'R' or record['Blood'] == 'Y'):
            items_due_for_airman.append('Blood work')
        if 'DNA' in record and (record['DNA'] == 'R' or record['DNA'] == 'Y'):
            items_due_for_airman.append('DNA test')
        if record['Dental'] == 'R' or record['Dental'] == 'Y':
            if 'Dental Class' in record:
                if record['Dental Class'] in {1, 2, 3}:
                    items_due_for_airman.append('Dental exam')
            else:
                items_due_for_airman.append('Dental exam')
        if record['PHA'] == 'R' or record['PHA'] == 'Y':
            if 'PHAQ' in actions or 'MHA' in actions:
                items_due_for_airman.append('PHA')
            else:
                # this is on the med group side to complete
                pass
        if record['Eqp'] == 'R' or record['Eqp'] == 'Y':
            items_due_for_airman.append('Occupational health requirements and/or optometry exam')

    if len(items_due_for_airman) == 0:
        items_due_for_airman = None
        is_due = False
    else:
        is_due = True

    all_items = list(set(actions.split('|')) - {''})
    all_items.sort()

    return is_due, items_due_for_airman, all_items


def get_reformatted_imr_sheet(imr_df_raw, is_superuser):
    try:
        if not is_superuser:
            if 'Med Eqp' in imr_df_raw.columns:
                msg = "You may have accidentally uploaded a supervisor's spreadsheet. Please upload a different spreadsheet"
                raise DatasheetsException(msg)

            imr_df_raw.rename(columns={'Den': 'Dental'}, inplace=True)

        final_columns = ['Last Name', 'First Name', 'Unit', 'Imm', 'Dental', 'Dental Class', 'Lab', 'DLC', 'PHA', 'IMR',
                         'Action List', 'Eqp']
        if is_superuser:
            imr_df_raw.rename(columns={'Med Eqp': 'Eqp'}, inplace=True)
            try:
                test = imr_df_raw['DNA']
                test = imr_df_raw['HIV']
                test = imr_df_raw['Blood']
            except:
                msg = "Your spreadsheet is missing information, please upload a different spreadsheet"
                raise DatasheetsException(msg)
            final_columns = final_columns + ['DNA', 'HIV', 'Blood']
  

        imr_df_clean = pd.DataFrame(imr_df_raw, columns=final_columns)
        imr_df_clean = imr_df_clean.convert_dtypes(infer_objects=True)

        d = dict.fromkeys(imr_df_clean.select_dtypes(exclude=np.number).columns, '')
        imr_df_clean = imr_df_clean.fillna(d)

        new_action_columns = list(imr_df_clean.apply(f, axis=1))
        is_due_for_airmen, items_due_for_airmen, items_due = map(list, zip(*new_action_columns))

        imr_df_clean['Items Due for Airmen'] = items_due_for_airmen
        imr_df_clean['Due'] = is_due_for_airmen
        imr_df_clean['All Items Due'] = items_due
        return imr_df_clean

    except KeyError as e:
        msg = "Key Error for " + str(e)
        raise DatasheetsException(msg)


def clean_contact_sheet(contact_df):
    cleaned_phone_numbers = []
    for number in contact_df['Phone Number']:
        try:
            cleaned_phone_numbers.append(phone.parse(str(number), 'US').national_number)
        except phone.NumberParseException:
            cleaned_phone_numbers.append(pd.NaT)

    contact_df['Phone Number'] = cleaned_phone_numbers

    return contact_df


def make_sms_messages(due_df):
    sms_list = []
    for idx, row in due_df.iterrows():
        msg_string = "This is a message from the 15th Medical Group. You are due for the following: " + ', '.join(row['Items Due for Airmen']) + \
                     ". Please check the Air Force Portal to verify your IMR status."
        sms_list.append(msg_string)
    due_df['Message'] = sms_list

    return due_df
