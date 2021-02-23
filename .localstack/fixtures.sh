echo "running fixtures"
SERVICE_PREFIX="simplestack-service"
LOCALSTACK_REGION=${LOCALSTACK_REGION-'us-east-1'}
LOCALSTACK_STAGE=${LOCALSTACK_STAGE-'simple'}
AWS_ENDPOINT='http://localstack:4566'
### create source stream paramters
sourceStreamName="demo-source-stream"
awslocal kinesis create-stream --stream-name ${sourceStreamName} --shard-count 3 --region ${LOCALSTACK_REGION} --endpoint ${AWS_ENDPOINT}
sourceStreamArn=`awslocal kinesis describe-stream --stream-name ${sourceStreamName} --endpoint ${AWS_ENDPOINT} | jq '.StreamDescription.StreamARN'`
sourceSsmBase="/simple/simple-source/${LOCALSTACK_STAGE}/${LOCALSTACK_REGION}"
awslocal ssm put-parameter --name ${sourceSsmBase}/stream_arn --type String --value ${sourceStreamArn} --overwrite --description "ARN of source kinesis stream" --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
awslocal ssm put-parameter --name ${sourceSsmBase}/stream_name --type String --value ${sourceStreamName} --overwrite --description "Name of source kinesis stream" --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
awslocal ssm get-parameter --name ${sourceSsmBase}/stream_arn --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
awslocal ssm get-parameter --name ${sourceSsmBase}/stream_name --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
### create sink stream paramters
sinkStreamName="demo-sink-stream"
awslocal kinesis create-stream --stream-name ${sinkStreamName} --shard-count 3 --region ${LOCALSTACK_REGION} --endpoint ${AWS_ENDPOINT}
sinkStreamArn=`awslocal kinesis describe-stream --stream-name ${sinkStreamName} --endpoint ${AWS_ENDPOINT} | jq '.StreamDescription.StreamARN'`
sinkSsmBase="/simple/simple-sink/${LOCALSTACK_STAGE}/${LOCALSTACK_REGION}"
awslocal ssm put-parameter --name ${sinkSsmBase}/stream_arn --type String --value ${sinkStreamArn} --overwrite --description "ARN of source kinesis stream" --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
awslocal ssm put-parameter --name ${sinkSsmBase}/stream_name --type String --value ${sinkStreamName} --overwrite --description "Name of source kinesis stream" --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
export SINK_STREAM_NAME=${sinkStreamName} # for the aroundTheWorld example


### create deployment bucket
awslocal s3 mb s3://${SERVICE_PREFIX}-lambda-deployments-local --region ${LOCALSTACK_REGION} --endpoint ${AWS_ENDPOINT} 
awslocal s3api get-bucket-location --bucket ${SERVICE_PREFIX}-lambda-deployments-local --endpoint ${AWS_ENDPOINT}

# if false; then
    DIR="$(dirname $(readlink -f $0))/../"
    echo "running stream consumer test creations"
    ### create test stream consumer
    awslocal kinesis register-stream-consumer --consumer-name con1 --stream-arn ${sourceStreamArn} --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
    awslocal kinesis describe-stream-consumer --stream-arn ${sourceStreamArn} --consumer-name con1 --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
    awslocal kinesis describe-stream-consumer --consumer-arn "arn:aws:kinesis:us-east-1:000000000000:stream/demo-source-stream/consumer/con1" --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}

    ### deploy test stack to create stream consumer
    awslocal cloudformation create-stack --stack-name demo-prep --template-body file://${DIR}/.localstack/mini-cft.json --endpoint ${AWS_ENDPOINT} --region ${LOCALSTACK_REGION}
    awslocal kinesis describe-stream-consumer \
        --stream-arn ${sourceStreamArn} \
        --consumer-name StreamDemoConsumer \
        --endpoint ${AWS_ENDPOINT} \
        --region ${LOCALSTACK_REGION}
# fi
