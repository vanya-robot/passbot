# passbot
A bot that allows authorized users to order a car pass 

### Preparation for work

1. Get Telegram Bot Token from FatherBot. Write it in the token.txt file;
2. Create Google Cloud service account with "Edit" permissions. Download credentials file and rename it as creds.json;
3. Create Google Spreadsheet named 'Orders' with worksheets "Orders_latest" and "Orders_completed". Give service account from step 2 permission to edit this spreadsheet (if you want to name them differently, you'll have to change names in spreadsheets.py);
4. Create admins.txt file and write admin's Telegram Chat ID in it (one ID per line);
5. In the passbot directory create 'vol' folder (passbot/vol). Move all files from previous steps into the vol directory.

### Functionality

During first launch of main.py, SQLite3 database will be created in the passbot/vol directory. 
User data and orders will be stored there.

Bot commands:

/code - Generates random code, consisting of 20 characters. It will be used during registration of a user. Can be used only by admins (from admins.txt);

/register - First checks if user is already in the database. If not, starts registration process;

/start - Same as /register;

/order - Checks if user is in the database. If so, starts pass order process;

/help - Sends a message to user with the list of available commands;

### Registration process

/register or /start command will trigger this process.

1. Bot will ask to provide inviter code from admin. After checking if code is in the database, it will be marked as used, so it couldn't be used second time.

2. Bot will ask for user's name, phone number, house number.

3. If all the data is presented in correct format, registration will be completed successfully.

### Order process

/order command will trigger this process. Only registered users can use this command.

1. Bot will ask to enter car brand.
2. Bot will ask to enter license plate number (Russian Federation format).
3. If all the data is presented in correct format, order will be written in the database.

### Google Sheets integration

client_to_server.py and spreadsheets.py are responsible for GS integration.

Every order has its timestamp (time when order was created). 

client_to_server.py script updates 'Orders_latest' sheet every 20 seconds (you can change that value, but be aware that GSheets API v4 doesn't allow more than 60 requests per minute).

Every order in 'Orders_latest' is displayed with all the data about user, who commited it. Also, not all the orders are displayed: by default, orders for the last 48 hours are displayed (changeable, check set_updated_orders function in client_to_server.py to change time).

In column H, next to every order, checkbox is located. It's necessary for security checkpoint operator to mark completed orders. During next client_to_server.py update, every order with filled checkbox will be marked as completed in the database, and written in the 'Orders_completed' sheet with filled 'Time_of_arrival' column (time of arrival is, basically, timestamp of the client_to_server.py update, during which, order was marked as completed).