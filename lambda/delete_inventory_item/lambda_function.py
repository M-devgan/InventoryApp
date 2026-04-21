import json
import os
from typing import Any, Dict

import boto3


# pylint: disable=broad-except
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Delete an inventory item from DynamoDB."""

    dynamodb = boto3.resource("dynamodb")

    table_name = os.getenv("TABLE_NAME", "Inventory")
    table = dynamodb.Table(table_name)

    if "pathParameters" not in event or "id" not in event["pathParameters"]:
        return {
            "statusCode": 400,
            "body": json.dumps("Missing 'id' path parameter"),
        }

    item_id = event["pathParameters"]["id"]

    try:
        response = table.scan()
        items = response.get("Items", [])

        matched_item = next(
            (item for item in items if item.get("item_id") == item_id),
            None,
        )

        if not matched_item:
            return {
                "statusCode": 404,
                "body": json.dumps(f"Item with ID {item_id} not found."),
            }

        table.delete_item(
            Key={
                "item_id": matched_item["item_id"],
                "location_id": matched_item["location_id"],
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(f"Item with ID {item_id} deleted successfully."),
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error deleting item: {str(error)}"),
        }
