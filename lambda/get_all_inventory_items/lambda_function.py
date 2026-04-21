# pylint: disable=missing-module-docstring, broad-except
# mypy: ignore-errors
import json
import os
from decimal import Decimal
from typing import Any, Dict

import boto3  # type: ignore


def decimal_default(obj: Any) -> Any:
    """Convert Decimal values to int or float for JSON serialization."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


# pylint: disable=broad-except
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Retrieve all inventory items from DynamoDB."""

    dynamodb = boto3.resource("dynamodb")

    table_name = os.getenv("TABLE_NAME", "Inventory")
    table = dynamodb.Table(table_name)

    try:
        response = table.scan()
        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "body": json.dumps(items, default=decimal_default),
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error getting inventory items: {str(error)}"),
        }
