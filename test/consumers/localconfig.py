import boto3
import os
import logging

here = os.path.abspath(os.path.dirname(__file__))

class KinesisConfig:
    def __init__(self):

        DEFAULT_PARAM_DICT = {
            "APP_LOG_FILE": here + ".log",            
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_SESSION_TOKEN": "test",
            "USE_SSL": None
        }

        # these come from aws secret-manager or env
        DEFAULT_OPT_PARAM_DICT = {
            "AWS_REGION": "us-east-1",
            "KINESIS_ENDPOINT": None,
            "STREAM_NAME": None,
        }

        for k, v in DEFAULT_PARAM_DICT.items():
            setattr(self, k, os.environ.get(k, v))
        
        for k, v in DEFAULT_OPT_PARAM_DICT.items():
            setattr(self, k, os.environ.get(k, v))

        self.kinesis_client = None
        self.s3_client = None
        self.configured_from_aws_secret = None
        self.set_logger()

    def set_logger(self):
        logging.basicConfig(
            filename='./logs/simplestack.log', 
            level=logging.INFO,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M',                
            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console)
        self.logging = logging

    def kinesis_connection(self):
        if not self.kinesis_client:
            kwargs = {                
                'region_name':self.AWS_REGION,
                'aws_access_key_id':self.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key':self.AWS_SECRET_ACCESS_KEY,
                'aws_session_token':self.AWS_SESSION_TOKEN
                }            
            
            if getattr(self,'KINESIS_ENDPOINT',None):
                kwargs['endpoint_url']=self.KINESIS_ENDPOINT
            
            if getattr(self,'USE_SSL',None):
                kwargs['use_ssl']=not (self.USE_SSL=='False')


            self.kinesis_client = boto3.client(
                'kinesis',
                **kwargs
            )
        else:
            self.logging.info('kinesis_client is already set, using existing.')


    def get_kinesis_shard_iterator(self, stream_name):
        kinesis_stream = self.kinesis_client.describe_stream(StreamName=stream_name)
        shards = kinesis_stream['StreamDescription']['Shards']
        shard_ids = [shard['ShardId'] for shard in shards]
        shard_iterator_list = []
        for shard_id in shard_ids:
            iter_response = self.kinesis_client.get_shard_iterator(StreamName=stream_name, ShardId=shard_id, ShardIteratorType="TRIM_HORIZON")
            shard_iterator_list.append(iter_response['ShardIterator'])
        return shard_iterator_list

config: KinesisConfig = KinesisConfig()
