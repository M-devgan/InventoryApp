import json
import os
from decimal import Decimal
from typing import Any, Dict

import boto3


def decimal_default(obj: Any) -> Any:
    """Convert Decimal values to int or float for JSON serialization."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


# pylint: disable=broad-except
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Retrieve a single inventory item by ID."""

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
                "body": json.dumps("Item not found"),
            }

        return {
            "statusCode": 200,
            "body": json.dumps(matched_item, default=decimal_default),
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error getting item: {str(error)}"),
        }
