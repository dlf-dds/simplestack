import json
import boto3
import os
import base64
from pathlib import Path
from os import path


def around_the_world(event, context):
    print(f"running {Path(__file__).resolve()}")
    

    body = {
        "message": "We are sending the record back into a new Kinesis Stream",
    }
    print(event)
    

    KINESIS_ENDPOINT_ = os.getenv('KINESIS_ENDPOINT', None)
    AWS_SECURITY_TOKEN_ = os.getenv('AWS_SECURITY_TOKEN', None)
    AWS_ACCESS_KEY_ID_ = os.getenv('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY_ = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    
    if AWS_SECURITY_TOKEN_ == None:
        os.environ['AWS_SECURITY_TOKEN'] = "test"
    if AWS_ACCESS_KEY_ID_ == None:
        os.environ['AWS_ACCESS_KEY_ID'] = "test"
    if AWS_SECRET_ACCESS_KEY_ == None:
        os.environ['AWS_SECRET_ACCESS_KEY'] = "test"

    print(f"initial AWS_SECURITY_TOKEN: {AWS_SECURITY_TOKEN_}"+"\n")
    print(f"initial AWS_ACCESS_KEY_ID: {AWS_ACCESS_KEY_ID_}"+"\n")
    print(f"initial AWS_SECRET_ACCESS_KEY: {AWS_SECRET_ACCESS_KEY_}"+"\n")
    print(f"initial KINESIS_ENDPOINT: {KINESIS_ENDPOINT_}"+"\n")

    if KINESIS_ENDPOINT_:
        kinesis = boto3.client('kinesis',endpoint_url=KINESIS_ENDPOINT_)
    else:
        kinesis = boto3.client('kinesis')
    for record in event["Records"]:
        decoded_data = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")        
        stream_name = os.getenv('SINK_STREAM_NAME')    
        print(f"stream_name:{stream_name}")
        # PartitionKey=str(hash(json.dumps(event)))
        try:
            print("""
                hold off on kinesis.put_record bc localstack can't handle it.
                I think it's trying to hit real AWS Cloud services from the lambda.
                And it cannot reach http://localhost:4566 from within the lambda container""")
            lambda_response = {
                "statusCode": 200,
                "body": json.dumps(body),
                "handlerLocation": f"{Path(__file__).resolve()}",
                "stream": stream_name,
                "KINESIS_ENDPOINT_": KINESIS_ENDPOINT_,
                "AWS_SECURITY_TOKEN_": AWS_SECURITY_TOKEN_,
                "AWS_ACCESS_KEY_ID_": AWS_ACCESS_KEY_ID_,
                "AWS_SECRET_ACCESS_KEY_": AWS_SECRET_ACCESS_KEY_,          
            }
            if False:
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
                    "KINESIS_ENDPOINT_": KINESIS_ENDPOINT_,
                    "AWS_SECURITY_TOKEN_": AWS_SECURITY_TOKEN_,
                    "AWS_ACCESS_KEY_ID_": AWS_ACCESS_KEY_ID_,
                    "AWS_SECRET_ACCESS_KEY_": AWS_SECRET_ACCESS_KEY_,          
                }
        except Exception as exc:
            print(repr(exc)+','.join(exc.args))
            lambda_response = {
                "statusCode": 400,
                "body": json.dumps({"msg":"kinesis put failed."}),
                "handlerLocation": f"{Path(__file__).resolve()}",
                "exception": repr(exc)+','.join(exc.args),
                "stream": stream_name,
                "KINESIS_ENDPOINT_": KINESIS_ENDPOINT_,
                "AWS_SECURITY_TOKEN_": AWS_SECURITY_TOKEN_,
                "AWS_ACCESS_KEY_ID_": AWS_ACCESS_KEY_ID_,
                "AWS_SECRET_ACCESS_KEY_": AWS_SECRET_ACCESS_KEY_,
            }

        
    print(f"lambda_response:{lambda_response}")

    return lambda_response




