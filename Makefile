include .make/help.Makefile
include .make/utils.Makefile

### CONFIGURE THESE (See comments) ###
uniqueSuffix=DLF
### END OF CONFIGURABLES ###

### CONSTANT DEFS ###
dcr=docker-compose run --rm docker-sls /bin/sh -c
localstack_env=source .localstack/.env.point-to-localstack && 
stackName=simplestack-service-demo-${uniqueSuffix}
SOURCE_STREAM_NAME=demo-source-stream
SINK_STREAM_NAME=demo-sink-stream
ROOT_DIR = $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
### END OF CONSTANT DEFS ###
.EXPORT_ALL_VARIABLES:

### LOCALSTACK ###
localstack:			##@d--localstack bring up localstack
	touch logs/manual-logs.log
	docker-compose down --remove-orphans \
	&& sleep 2 \
	&& docker-compose up localstack

LOCALSTACK_REGION?=us-east-1
LOCALSTACK_STAGE?=simple
fixtures:				##@d--localstack fixtures that sls deploy needs
	# USAGE: make fixtures LOCALSTACK_REGION=<us-east-1|us-west-1> 
	# e.g. make fixtures LOCALSTACK_REGION=us-east-1 
	${dcr} ./.localstack/fixtures.sh 	

localdeploy:			##@d--localstack deploy to localstack
	# USAGE: make deploy LOCALSTACK_REGION=<us-east-1|us-west-1> 
	# e.g. make localdeploy LOCALSTACK_REGION=us-east-1 
	source .localstack/.env.point-to-localstack && \
	${dcr} "sls print --stage ${LOCALSTACK_STAGE} --region ${LOCALSTACK_REGION} && \
	sls deploy --stage ${LOCALSTACK_STAGE} --region ${LOCALSTACK_REGION}"

	

FUN?=aroundTheWorld
localinvoke:           ##@d--localstack try invoking (local, localstack from sls, localstack w/ awslocal)
	# USAGE: make localinvoke FUN=<aroundTheWorld> LOCALSTACK_REGION=<us-east-1|us-west-1> 
	# e.g. make localinvoke LOCALSTACK_REGION=us-east-1 
	source .localstack/.env.point-to-localstack && \
	export KINESIS_ENDPOINT=http://localstack:4566 && \
	echo "[0] invoke local in localstack with sls" && \
	${dcr} "sls invoke local -f ${FUN} --stage ${LOCALSTACK_STAGE} --region ${LOCALSTACK_REGION} --path test/functions/${FUN}/data/hello.json" && \
	echo "[1] invoke in localstack with sls" && \
	${dcr} "sls invoke -f ${FUN} --stage ${LOCALSTACK_STAGE} --region ${LOCALSTACK_REGION} --path test/functions/${FUN}/data/hello.json" && \
	echo "[2] invoke from cli (w/o sls)" && \
	${dcr} "awslocal lambda invoke --function-name ${stackName}-${LOCALSTACK_STAGE}-${FUN} \
		--endpoint http://localstack:4566 --region ${LOCALSTACK_REGION} \
		--payload '{\"Records\": [{\"kinesis\": {\"data\": \"eyJtc2ciOiAiaGkifQ==\"}}]}' \
		/dev/null"	

diagnose:				##@d--localstack awslocal describe existing stack
	# USAGE: make diagnose LOCALSTACK_STAGE=<simple>
	# e.g. make diagnose
	${dcr} "awslocal cloudformation describe-stacks --stack-name ${stackName}-${LOCALSTACK_STAGE} --endpoint http://localstack:4566"
	${dcr} "awslocal cloudformation describe-stack-events --stack-name ${stackName}-${LOCALSTACK_STAGE} --endpoint http://localstack:4566"
	${dcr} "awslocal cloudformation describe-stack-resources --stack-name ${stackName}-${LOCALSTACK_STAGE} --endpoint http://localstack:4566"
	${dcr} "awslocal lambda list-functions --endpoint http://localstack:4566" 

shell:					##@e--sls shell
	source .localstack/.env.point-to-localstack && \
	${dcr}  /bin/bash

PUBLISH_STREAM_NAME?=demo-source-stream
publish:				##@f--utils kinesis publish
	# USAGE: make publish PUBLISH_STREAM_NAME=<demo-source-strea|demo-sink-stream>
	# e.g. make listen PUBLISH_STREAM_NAME=demo-source-stream
	${localstack_env} ${dcr} "\
		AWS_DEFAULT_REGION=us-east-1 \
		&& KINESIS_ENDPOINT=http://localstack:4566 \
		&& STREAM_NAME=${SOURCE_STREAM_NAME} \
		python3 ./test/producers/produce.py \
		"	
		
LISTEN_STREAM_NAME?=demo-sink-stream
listen:					##@f--utils listen to stream
	# USAGE: make listen LISTEN_STREAM_NAME=<demo-source-strea|demo-sink-stream>
	# e.g. make listen LISTEN_STREAM_NAME=demo-sink-stream
	source .localstack/.env.point-to-localstack && \
	${dcr} "python3 ./test/consumers/listen.py"	

logs:					##@f--utils kinesis
	# USAGE: make log FUN=<hello|around_the_world> LOCALSTACK_REGION=<us-east-1|us-west-1> LOCALSTACK_STAGE=<local>
	# e.g. make log FUN=aroundTheWorld LOCALSTACK_REGION=us-east-1 LOCALSTACK_STAGE=simple
	${dcr} "\
		awslocal logs \
		describe-log-groups \
		--endpoint http://localstack:4566 --region ${LOCALSTACK_REGION} \
		" && \
	${dcr} "\
		awslocal logs \
		describe-log-streams \
		--log-group-name /aws/lambda/${stackName}-${LOCALSTACK_STAGE}-${FUN} \
		--endpoint http://localstack:4566 --region ${LOCALSTACK_REGION}  \
		" && \
	${dcr} "\
		awslocal logs \
		describe-log-streams \
		--log-group-name /aws/lambda/${stackName}-${LOCALSTACK_STAGE}-${FUN} \
		--endpoint http://localstack:4566 --region ${LOCALSTACK_REGION}  \
		" > /var/tmp/logStreamName && \
	${dcr} "\
		awslocal logs \
		get-log-events  \
		--log-group-name /aws/lambda/${stackName}-${LOCALSTACK_STAGE}-${FUN} \
		--log-stream-name `cat /var/tmp/logStreamName | jq '.logStreams[-1].logStreamName'` \
		--endpoint http://localstack:4566 --region ${LOCALSTACK_REGION} \
		"

.PHONY: 
