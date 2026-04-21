import boto3
import json
import os
from decimal import Decimal


def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource("dynamodb")

    # Get table name from environment variable
    table_name = os.getenv("TABLE_NAME", "Inventory")
    table = dynamodb.Table(table_name)

    # Check for path parameter
    if "pathParameters" not in event or "id" not in event["pathParameters"]:
        return {"statusCode": 400, "body": json.dumps("Missing 'id' path parameter")}

    item_id = event["pathParameters"]["id"]

    # Because table uses item_id + location_id, we first find the item by item_id
    try:
        response = table.scan()
        items = response.get("Items", [])

        matched_item = None
        for item in items:
            if item.get("item_id") == item_id:
                matched_item = item
                break

        if not matched_item:
            return {"statusCode": 404, "body": json.dumps("Item not found")}

        return {
            "statusCode": 200,
            "body": json.dumps(matched_item, default=decimal_default),
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error getting item: {str(e)}")}
