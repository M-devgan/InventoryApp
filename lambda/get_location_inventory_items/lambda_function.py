# pylint: disable=missing-module-docstring, broad-except
# mypy: ignore-errors
import json
import os
from decimal import Decimal
from typing import Any, Dict

import boto3  # type: ignore
from boto3.dynamodb.conditions import Key  # type: ignore


def decimal_default(obj: Any) -> Any:
    """Convert Decimal values to int or float for JSON serialization."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


# pylint: disable=broad-except
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Retrieve inventory items by location ID."""

    dynamodb = boto3.resource("dynamodb")

    table_name = os.getenv("TABLE_NAME", "Inventory")
    index_name = os.getenv(
        "LOCATION_INDEX_NAME",
        "location_id-item_id-index",
    )
    table = dynamodb.Table(table_name)

    if "pathParameters" not in event or "id" not in event["pathParameters"]:
        return {
            "statusCode": 400,
            "body": json.dumps("Missing 'id' path parameter"),
        }

    try:
        location_id = int(event["pathParameters"]["id"])

        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=Key("location_id").eq(location_id),
        )

        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "body": json.dumps(items, default=decimal_default),
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error getting location inventory items: {str(error)}"),
        }
