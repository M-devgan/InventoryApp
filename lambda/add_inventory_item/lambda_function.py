import json
import boto3
import uuid
import os
from decimal import Decimal

# Trigger Lambda deployment workflow

def lambda_handler(event, context):
    if 'body' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing request body")
        }

    try:
        data = json.loads(event['body'])
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps("Invalid JSON format")
        }

    table_name = os.getenv('TABLE_NAME', 'Inventory')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    unique_id = str(uuid.uuid4())

    try:
        table.put_item(
            Item={
                'item_id': unique_id,
                'location_id': str(data['location_id']),
                'item_name': data['item_name'],
                'item_description': data['item_description'],
                'item_qty_on_hand': int(data['item_qty_on_hand']),
                'item_price': Decimal(str(data['item_price']))
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f"Item with ID {unique_id} added successfully.")
        }
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f"Missing required field: {str(e)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error adding item: {str(e)}")
        }