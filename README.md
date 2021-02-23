# SimpleStack

e2e localstack

## Try It

### set up

#### API KEY

include a `.localstack/.env.localstack.secret` file with your
unique API KEY like so: `export LOCALSTACK_API_KEY=<your-api-key>` and confirm
that your `.gitignore` does ignore that file.

#### Bring up localstack and fixtures

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
