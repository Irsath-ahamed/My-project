#  Expected file format(csv):  PlatformOrderId, PlatformItemId, TrackingId(optional).

import datetime
import json
import os
import string
import sys
import time
import requests
import uuid
import auth0
from utils import auth_token_handler

if len(sys.argv) != 2:
    print("Usage: python send-fulfillment-events-items-only.py <file>")
    sys.exit()

v2_tok = auth_token_handler.get_v2_auth_token()

# Headers for API calls
headers = {'Accept': 'application/json', 'Authorization': f'Bearer {v2_tok}'}

# Read input file containing Platform Order ID, Platform Item ID, and optional Tracking ID
with open(sys.argv[1], 'r') as file:
    the_rows = [line.strip() for line in file if line.strip() and ',' in line]  

for the_row in the_rows:
    row_data = the_row.split(',')
    platform_order_id = row_data[0].strip()
    platform_item_id = row_data[1].strip()
    tracking_id = row_data[2].strip() if len(row_data) > 2 and row_data[2].strip() else None  # Handle optional tracking ID

    if not platform_order_id or not platform_item_id:
        continue  # Skip invalid entries

    print(f'Processing Order {platform_order_id}, Item {platform_item_id}')
    time.sleep(0.2)

    # Fetch Short Item ID from Item Service API
    item_service_url = f"https://item-service.commerce.cimpress.io/v1/items/{platform_item_id}"
    item_response = requests.get(item_service_url, headers=headers)

    if item_response.status_code != 200:
        print(f'ERROR: Failed to fetch item details for {platform_item_id}')    
        continue

    item_data = item_response.json()
    short_item_id = item_data.get('shortItemId', platform_item_id)

    # Fetch quantity details
    delivery_configurations = sum(config.get('quantity', 0) for config in item_data.get('deliveryConfigurations', []))
    fulfilled_quantity = item_data.get('statuses', {}).get('fulfilled', {}).get('quantity', 0)
    remaining_quantity = max(delivery_configurations - fulfilled_quantity, 0)

    # Check if already fully shipped
    fulfillment_status = item_data.get('statuses', {}).get('fulfillment', {}).get('state', '').lower()
    if fulfillment_status == 'shipped' or delivery_configurations == fulfilled_quantity or remaining_quantity == 0:
        print(f'Skipping Order {platform_order_id}, Item {short_item_id} - Already fully shipped')
        continue

    # Determine quantity to update
    quantity_to_update = delivery_configurations if fulfilled_quantity == 0 else remaining_quantity

    # Prepare payload for fulfillment update
    data = {
        'details': [{
            'fulfillerOrderId': item_data.get('shortFulfillmentGroupId', platform_order_id),
            'fulfillerOrderItemId': short_item_id,
            'quantity': int(quantity_to_update),
            'shipmentId': str(uuid.uuid4())
        }],
        'eventDate': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    
    if tracking_id:
        data['details'][0]['trackingId'] = tracking_id  

    # Send fulfillment update request
    fulfillment_url = 'https://fulfiller-gateway.fulfillment.cimpress.io/v2/fulfillment'
    fulfillment_response = requests.post(fulfillment_url, json=data, headers=headers)

    if fulfillment_response.status_code > 299:
        print(f'ERROR: Failed to update fulfillment for Order {platform_order_id}, Item {short_item_id}')
    else:
        print(f'Successfully updated fulfillment for Order {platform_order_id}, Item {short_item_id}' + (f' with Tracking ID: {tracking_id}' if tracking_id else ''))
