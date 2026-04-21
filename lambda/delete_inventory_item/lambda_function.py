import boto3
import json
import os


def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # Get table name from environment variable
    table_name = os.getenv('TABLE_NAME', 'Inventory')
    table = dynamodb.Table(table_name)

    # Extract item_id from path parameters
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    item_id = event['pathParameters']['id']

    try:
        # Find the item first because delete needs both item_id and location_id
        response = table.scan()
        items = response.get('Items', [])

        matched_item = None
        for item in items:
            if item.get('item_id') == item_id:
                matched_item = item
                break

        if not matched_item:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Item with ID {item_id} not found.")
            }

        table.delete_item(
            Key={
                'item_id': matched_item['item_id'],
                'location_id': matched_item['location_id']
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f"Item with ID {item_id} deleted successfully.")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error deleting item: {str(e)}")
        }