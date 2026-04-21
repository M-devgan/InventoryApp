# pylint: disable=missing-module-docstring, missing-function-docstring, broad-except, import-error, unused-argument
# mypy: ignore-errors

import json
import os
from typing import Any, Dict

import boto3  # type: ignore


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    table = boto3.resource("dynamodb").Table(os.getenv("TABLE_NAME", "Inventory"))

    if "pathParameters" not in event or "id" not in event["pathParameters"]:
        return {"statusCode": 400, "body": json.dumps("Missing id")}

    item_id = event["pathParameters"]["id"]

    try:
        response = table.scan()
        items = response.get("Items", [])

        matched = next(
            (item for item in items if item.get("item_id") == item_id),
            None,
        )

        if not matched:
            return {"statusCode": 404, "body": json.dumps("Not found")}

        table.delete_item(
            Key={
                "item_id": matched["item_id"],
                "location_id": matched["location_id"],
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(f"Deleted {item_id}"),
        }

    except Exception as error:
        return {"statusCode": 500, "body": json.dumps(str(error))}
