import gspread
from gspread_formatting.dataframe import format_with_dataframe
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import orders_update


def set_updated_orders(time, googlesheet_name, worksheet_name, account=gspread.service_account(filename='vol/creds.json')):
    gp = account
    googlesheet = gp.open(googlesheet_name)
    worksheet = googlesheet.worksheet(worksheet_name)

    df = orders_update.select_current_orders(time)
    df_len = df.shape[0]
    set_with_dataframe(worksheet, df)
    add_checkboxes('H', 2, df_len)
    format_with_dataframe(worksheet, df, include_column_header=True)


def take_df_from_spreadsheet(googlesheet_name, worksheet_name, usecols,
                             account=gspread.service_account(filename='vol/creds.json')):
    gp = account
    googlesheet = gp.open(googlesheet_name)
    worksheet = googlesheet.worksheet(worksheet_name)

    df = get_as_dataframe(worksheet, parse_dates=True, usecols=usecols, skiprows=1, header=None)

    return df


def add_checkboxes(column, start_val, stop_val, account=gspread.service_account(filename='vol/creds.json'),
                   googlesheet_name='Orders', worksheet_name='Orders_latest'):
    service = account
    googlesheet = service.open(googlesheet_name)
    worksheet = googlesheet.worksheet(worksheet_name)

    validation_rule = DataValidationRule(
        BooleanCondition('BOOLEAN', ['TRUE', 'FALSE']),  # condition'type' and 'values', defaulting to TRUE/FALSE
        showCustomUi=True)

    set_data_validation_for_cell_range(worksheet, column + f'{start_val}' + ':' + column + f'{stop_val + 1}',
                                       validation_rule)


def clear_worksheet(googlesheet_name, worksheet_name, account=gspread.service_account(filename='vol/creds.json')):
    service = account
    googlesheet = service.open(googlesheet_name)
    worksheet = googlesheet.worksheet(worksheet_name)

    worksheet.clear()


def append_row_order(row, info, account=gspread.service_account(filename='vol/creds.json')):
    """

    :param row: row = [code, car_num, car_brand, Time, Time_of_arrival]
    :param info: info = (Name, Phone, Home_num)
    :param account: gspread account
    :return: adds a row to the Orders_all worksheet
    """

    googlesheet = account.open('Orders')
    worksheet = googlesheet.worksheet('Orders_completed')

    line = [row[0], row[1], row[2], str(row[3]), info[0], info[1], info[2], row[4]]
    worksheet.append_row(line)
