import boto3
import json
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key


def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # Get table name and index name from environment variables
    table_name = os.getenv('TABLE_NAME', 'Inventory')
    index_name = os.getenv('LOCATION_INDEX_NAME', 'location_id-item_id-index')
    table = dynamodb.Table(table_name)

    # Extract location id from path parameters
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    try:
        location_id = event['pathParameters']['id']

        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=Key('location_id').eq(location_id)
        )

        items = response.get('Items', [])

        return {
            'statusCode': 200,
            'body': json.dumps(items, default=decimal_default)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error getting location inventory items: {str(e)}")
        }