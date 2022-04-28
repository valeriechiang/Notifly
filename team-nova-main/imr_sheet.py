from collections import defaultdict
import pandas as pd
from datasheetsexception import DatasheetsException

imr_item_to_category = {
    'INFLUENZA, NORTHERN HEMISPHERE': 'Imm',
    'ANTHRAX': 'Imm',
    'COVID-19': 'Imm',
    'JAPANESE ENCEPHALITIS': 'Imm',
    'MENINGOCOCCAL': 'Imm',
    'MMR': 'Imm', 'PPD': 'Imm',
    'RABIES': 'Imm',
    'TD': 'Imm',
    'TYPHOID': 'Imm',
    'YELLOW FEVER': 'Imm',
    'DENTAL': 'Dental',
    'MILITARY DENTAL': 'Dental',
    'BLOOD TYPE': 'Lab',
    'DNA': 'Lab',
    'G6PD': 'Lab',
    'HEP A': 'Lab',
    'HEP B': 'Lab',
    'HIV': 'Lab',
    'RH': 'Lab',
    'SERUM': 'Lab',
    'SICKLECELL': 'Lab',
    'MHA': 'PHA',
    'PHA': 'PHA',
    'PHAQ': 'PHA',
    'AUDIOGRAM': 'Eqp',
    'CONTACT LENS APPT': 'Eqp',
    'DISTANT VISUAL ACUITY': 'Eqp',
    'GAS MASK INSERTS': 'Eqp',
    'DD2795': 'DHL',
    'DD2796': 'DHL',
    'DHA1 APPT': 'DHL',
    'DHA2 APPT': 'DHL',
    'DHA3': 'DHL',
    'DHA3 APPT': 'DHL',
    'DHA4': 'DHL',
    'DHA4 APPT': 'DHL',
    'DHA5': 'DHL',
    'DHA5 APPT': 'DHL',
    'MED WARNING TAG': 'Other',
    'FITNESS COUNSELING': 'Other',
    'ANAM': 'Other'
}


def unit_to_group():
    filename = 'unit_to_group.csv'
    unit_to_group_d = dict()
    with open(filename) as f:
        for line in f:
            unit, group = line.strip().split(',')
            if group != '':
                unit_to_group_d[unit] = group
    return unit_to_group_d


def query_imr_sheet(imr_df, due=None, imr_category=None) -> object:
    try:
        if due:
            return imr_df.loc[imr_df['Due'] == True]

        if imr_category:
            imr_items_with_frequency = defaultdict(int)
            for items_list in imr_df['All Items Due']:
                for item in items_list:
                    imr_items_with_frequency[item.upper()] += 1
            imr_items_df = pd.DataFrame.from_dict(imr_items_with_frequency, orient='index')
            imr_items_df = imr_items_df.reset_index().rename(columns={'index': 'Item', '0': 'Frequency'})
            categories = []
            for c in imr_items_df['Item']:
                if c in imr_item_to_category:
                    categories.append(imr_item_to_category[c])
                else:
                    categories.append('Other')
            imr_items_df.insert(len(imr_items_df.columns), 'Category', categories)

            return imr_items_df


    except Exception as e:
        print(e)
        raise DatasheetsException("Cannot parse IMR sheet.")


