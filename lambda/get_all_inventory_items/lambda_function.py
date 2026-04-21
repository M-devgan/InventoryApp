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

    try:
        items = table.scan().get("Items", [])
        return {
            "statusCode": 200,
            "body": json.dumps(items, default=decimal_default),
        }
    except Exception as error:
        return {"statusCode": 500, "body": json.dumps(str(error))}
