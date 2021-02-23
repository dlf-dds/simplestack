# SimpleStack

e2e localstack

## Try It

### set up

`docker-compose build`

`make localstack`

in a new console:

`make fixtures`

### deploy

`make localdeploy`

### invoke

`make localinvoke`

### kinesis

publish to the source stream

`make publish`

listen to the sink stream

`make listen`

### etc

`make` will show you all the make targets
