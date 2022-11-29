import gspread
import time
import orders_update
from spreadsheets import set_updated_orders, take_df_from_spreadsheet, clear_worksheet

account = gspread.service_account(filename='creds.json')

while True:
    clear_worksheet('Orders', 'Orders_latest', account=account)
    try:
        set_updated_orders(48, 'Orders', 'Orders_latest', account=account)
        time.sleep(20)
        df = take_df_from_spreadsheet('Orders', 'Orders_latest', [3, 7], account=account)
        orders_update.update_order_status(df)
    except ValueError:
        time.sleep(20)
        print('No Orders')
        continue

