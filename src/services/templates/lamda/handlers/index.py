import json

def handler(event, context):
    response_body = {
        "message": "Hello from Lambda!",
        "input": event,
    }

    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(response_body),
    }

    return response

