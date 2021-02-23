import json
import boto3
import os
import base64
from pathlib import Path
from os import path


def around_the_world(event, context):
    print(f"running {Path(__file__).resolve()}")

    logoutfilepath = Path(__file__).resolve().parent.parent.parent\
        .joinpath("logs").joinpath("manual-logs.log")
    
    try:
        if not path.exists(logoutfilepath):
            with open(logoutfilepath, "w")  as outfile:
                outfile.write(f"starting up manual log file for lambda: {Path(__file__)}\n")
        with open(logoutfilepath, "a")  as outfile:
            outfile.write(f"running lamdba: {Path(__file__)}\n")
    except:
        print("manual log file failed.")

    body = {
        "message": "We are sending the record back into a new Kinesis Stream",
    }
    print(event)
    

    kinesis_endpoint = os.getenv('KINESIS_ENDPOINT', None)
    initial_security_token = os.getenv('AWS_SECURITY_TOKEN', None)

    if initial_security_token == None:
        os.environ['AWS_SECURITY_TOKEN'] = "test"
    try:
        with open(logoutfilepath, "a")  as outfile:
            outfile.write(f"initial_security_token: {initial_security_token}"+"\n")
    except:
        print("manual log file failed.")

    if kinesis_endpoint:
        kinesis = boto3.client('kinesis',endpoint_url=kinesis_endpoint)
    else:
        kinesis = boto3.client('kinesis')
    for record in event["Records"]:
        decoded_data = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")        
        stream_name = os.getenv('SINK_STREAM_NAME')    
        print(f"stream_name:{stream_name}")
        # PartitionKey=str(hash(json.dumps(event)))
        try:
            last_kinesis_response = kinesis.put_record(
                StreamName=stream_name,
                Data=json.dumps(event), 
                PartitionKey=str(hash(stream_name))
            )
            body.update(json.loads(decoded_data))
            body.update(last_kinesis_response)
            lambda_response = {
                "statusCode": 200,
                "body": json.dumps(body),
                "handlerLocation": f"{Path(__file__).resolve()}",
                "stream": stream_name,
                "initial_security_token": initial_security_token,
                "kinesis_endpoint": kinesis_endpoint
            }
        except Exception as exc:
            print(exc)
            lambda_response = {
                "statusCode": 400,
                "body": json.dumps({"msg":"kinesis put failed."}),
                "handlerLocation": f"{Path(__file__).resolve()}",
                "exception": str(exc),
                "stream": stream_name,
                "initial_security_token": initial_security_token,
                "kinesis_endpoint": kinesis_endpoint
            }

        
    print(f"lambda_response:{lambda_response}")
    try:
        with open(logoutfilepath, "a")  as outfile:
            outfile.write(json.dumps(lambda_response)+"\n")
    except:
        print("manual log file failed.")

    return lambda_response




