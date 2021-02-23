import json
import boto3
import random
import datetime
import os
import time

os.environ['AWS_DEFAULT_REGION'] = 'us-gov-west-1'
# need to set AWS_DEFAULT_REGION in env
kinesis_endpoint = os.getenv('KINESIS_ENDPOINT', None)
if kinesis_endpoint:
    kinesis = boto3.client('kinesis',endpoint_url=kinesis_endpoint)
else:
    kinesis = boto3.client('kinesis')


stream_name = os.getenv('STREAM_NAME', 'demo-source-stream')
# stream_name = os.getenv('STREAM_NAME', 'demo-sink-stream')


def getReferrer():
    data = {}
    now = datetime.datetime.now()
    str_now = now.isoformat()
    data['EVENT_TIME'] = str_now
    data['TICKER'] = random.choice(['AAPL', 'AMZN', 'MSFT', 'INTC', 'TBV'])
    price = random.random() * 100
    data['PRICE'] = round(price, 2)
    return data
while True:
    try:
        data = json.dumps(getReferrer())
        print(data)
        response = kinesis.put_record(
                StreamName=stream_name,
                Data=data,
                PartitionKey="partitionkey")
        print(response)
    except Exception as exc:
        print(exc)

    time.sleep(5)
