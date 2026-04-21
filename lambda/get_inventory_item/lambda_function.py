# pylint: disable=missing-module-docstring, missing-function-docstring, broad-except, import-error, unused-argument
# mypy: ignore-errors

import json
import os
from decimal import Decimal
from typing import Any, Dict

import boto3  # type: ignore


def decimal_default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    table = boto3.resource("dynamodb").Table(os.getenv("TABLE_NAME", "Inventory"))

    if "pathParameters" not in event or "id" not in event["pathParameters"]:
        return {"statusCode": 400, "body": json.dumps("Missing id")}

    item_id = event["pathParameters"]["id"]

    try:
        items = table.scan().get("Items", [])

        matched = next(
            (item for item in items if item.get("item_id") == item_id),
            None,
        )

        if not matched:
            return {"statusCode": 404, "body": json.dumps("Not found")}

        return {
            "statusCode": 200,
            "body": json.dumps(matched, default=decimal_default),
        }

    except Exception as error:
        return {"statusCode": 500, "body": json.dumps(str(error))}
