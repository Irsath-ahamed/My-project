#Fetch order information to excel sheet.
#
#Output default location will be '~\Downloads'
#Expected file format: Only MCP orderID (CSV)

import pandas as pd
import requests
import json
import os
from utils import auth_token_handler

orders_df = pd.DataFrame()

csv_file = input("Enter CSV file containing order IDs: ")

try:
    with open(csv_file, 'r') as file:
        order_ids = file.readlines()
    order_ids = [order_id.strip() for order_id in order_ids if order_id.strip()]
except FileNotFoundError:
    print("CSV file not found.")
    exit()

# Get an auth token
v2_tok = auth_token_handler.get_v2_auth_token()
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {v2_tok}'
}

for order_id in order_ids:
    if not order_id:
        continue  # Skip empty order IDs
    api_url = f'https://merchantorder.commerce.cimpress.io/v1/orders/{order_id}'
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        order_data = response.json()
        order_df = pd.json_normalize(order_data)
        order_df['order_id'] = order_id
        orders_df = orders_df._append(order_df, ignore_index=True)
        print(f"Fetch order data for '{order_id}' saved successfully")
    else:
        print(f"Error fetching order for '{order_id}'. Status code: {response.status_code}")


downloads_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'orders_data.xlsx')


orders_df.to_excel(downloads_path, index=False)
print(f"Order data saved to '{downloads_path}'.")
print("Exiting the script.")
