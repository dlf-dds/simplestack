from datetime import datetime, timedelta
import json
import boto3
from botocore.exceptions import ClientError
import os, sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from test.consumers.localconfig import config as kinconfig


def get_kinesis_data_iterator(stream_name=None, minutes_running=None):
    print(f"AWS_SECURITY_TOKEN: {os.getenv('AWS_SECURITY_TOKEN',None)}")
    kinconfig.kinesis_connection()
    kinconfig.logging.info(f'stream_name={stream_name}')    
    shard_iterator_list = kinconfig.get_kinesis_shard_iterator(stream_name)

    # Calculate end time
    end_time = datetime.now() + timedelta(minutes=minutes_running)
    while True:
        try:
            new_shard_iterator_list = []
            for shard_iterator in shard_iterator_list:
                now = datetime.now()
                if end_time < now:
                    break

                kinconfig.logging.info('Time: {0}'.format(now.strftime('%Y/%m/%d %H:%M:%S')))
                record_response = kinconfig.kinesis_client.get_records(ShardIterator=shard_iterator)
                if len(record_response['Records']) == 0:
                    continue
                kinconfig.logging.info(f"record_response: {record_response}")
                kinconfig.logging.info(f"shard_iterator: {shard_iterator[-10:0]}")
                kinconfig.logging.info(f"num records: {len(record_response['Records'])}")
                for record in record_response['Records']:
                    kinconfig.logging.info(f'record: {record}')                    
                    last_sequence = record['SequenceNumber']
                    yield json.loads(record['Data'])
                if record_response['NextShardIterator']:
                    new_shard_iterator_list.append(record_response['NextShardIterator'])
                else:
                    new_shard_iterator_list.append(shard_iterator)
            shard_iterator_list=new_shard_iterator_list
        except ClientError as e:
            kinconfig.logging.error(e)
        time.sleep(5)

if __name__ == "__main__":
    import os
    minutes_running = int(os.getenv('MINUTES_RUNNING','1'))
    os.environ['AWS_REGION']='us-east-1'
    kinesis_data = get_kinesis_data_iterator(
        stream_name="demo-source-stream",
        minutes_running=minutes_running
        )
    for d in kinesis_data:
        print(d)
