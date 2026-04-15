import json
import boto3
import os

def lambda_handler(event, context):
    table_name = os.getenv('TABLE_NAME', 'Inventory')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    try:
        item_id = event['pathParameters']['item_id']

        table.delete_item(
            Key={
                'item_id': item_id
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f"Item {item_id} deleted successfully")
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }