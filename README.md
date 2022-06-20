# cdk_simple_cloudfront_canary_probe

## Introduction

Amazon CloudFront is a web service to distribute content with low latency and high data transfer rates by serving requests using a network of edge locations around the world. Customers leveraging Amazon CloudFront have high expectation about its performance and are highly sensible to systemic or sporadic latency increases. The factors contributing for increased latency while serving web content via CloudFront vary but customer often lack the capability to correctly identify the different sources of latency, leading to an extended degraded user experience. 

These instructions will deploy a CDK stack that, on it own, deploys an EC2 instance on a VPC of your choice, executing a latency probe every minute and uploading per PoP metrics into Cloudwatch in ```us-east-1``` region. 

The latency probe is developed in Python3, and leverages PyCurl to perform 2 requests against a CloudFront Distribution distribution. The URIs of the requests is customizable but they should be served through path pattern behaviours configured with Server Timing Response Policy. One of the requests should always result in a MISS event so that the probe is able to assess upstream latency experience as experienced by CloudFront towards the origin.

## Metrics

On successfull deployment, per PoP CW metrics are available in ```us-east-1``` region under a custom metric named ```Simple CloudFront Canary Probe```. The latency probe captures the following data per PoP:

#### From PyCurl metrics:

1. ```pycurl-dns```: The time PyCurl client took to resolve the CloudFront distribution domain name 
1. ```pycurl-connect```: The time PyCurl client took to connect to the edge location 
1. ```pycurl-pretranfer```: The pretransfer time e.g. the time until the end of SSL/TLC negotiation as experienced by PyCurl client
1. ```(miss/hit)-pycurl-fbl```: The time until PyCurl client receives the first byte of the response
1. ```(miss/hit)-pycurl-totaltime```: The total elapsed time as experienced by PyCurl client to be served

#### From CloudFront Server timing response headers:

1.	```miss-cdn-upstream-dns```: The time CloudFront took to resolve the domain name of the origin (for Miss events)
1.	```miss-cdn-upstream-connect```: The time CloudFront took to connect to the origin 
1.	```miss-cdn-upstream-fbl```: The time CloudFront expected until the first byte of the response is received from the origin 


## Installation

The deployment of the CDK stack can be triggered from any Linux instance as long as it provides python3, git and has AWS CLI instance. For convinience you may want to deploy it on an AMZ Linux 2 EC2 instance where all of the above utilities are installed or available by default. However, it is not mandatory to deploy it on an EC2 instance

### Requirements

* Create a custom response policy with Server-Timing header enabled with a 100% sampling rate.

* Attach the custom response policy with Server-Timing header enabled to a specific behaviour of your CloudFront Distribution.

* Select two requests / uris to probe the distribution performance matching the above behaviour:
1. one which will likely result on a `HIT` event;
1. another which will always result in a `MISS` event. A `MISS` event can be configured by adding a `Cache-Control: max-age=0` response header to response from your origin server. 

### Install NodeJS
###### Ref:  https://docs.aws.amazon.com/cdk/v2/guide/work-with.html#work-with-prerequisites

    wget https://nodejs.org/dist/v16.15.0/node-v16.15.0-linux-x64.tar.xz
    xz -d -v node-v16.15.0-linux-x64.tar.xz
    tar xvf node-v16.15.0-linux-x64.tar 
    export PATH=${PWD}/node-v16.15.0-linux-x64/bin:$PATH

### Install CDKv2 framework (`python3` must be already available - a AMZ Linux 2 EC2 instance provides it by default)
###### Ref: https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html

    python3 -m ensurepip --upgrade
    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade virtualenv
    npm install -g aws-cdk
    
### Create the default 'simple_cloudfront_canary_probe' project

    mkdir simple_cloudfront_canary_probe/; cd simple_cloudfront_canary_probe/
    cdk init app --language python
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    cd ..

### Download custom 'simple_cloudfront_canary_probe' project files (`git` must be available)

    git clone https://github.com/GoncaloBorges/cdk_simple_cloudfront_canary_probe.git
    cp cdk_simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/app.py simple_cloudfront_canary_probe/
    cp cdk_simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/simple_cloudfront_canary_probe_stack.py simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/
    cp -r cdk_simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/user_data simple_cloudfront_canary_probe/

### Customize the project user script for your use case

Edit ```simple_cloudfront_canary_probe/user_data/user_data.sh``` and customize the ```DISTRO, URL_HIT and URL_MISS``` variables 
 
   ```
   # Ex: 'd123456789.cloudfront.net'
   DISTRO='<REPLACE BY YOUR CLOUDFRONT DISTRIBUTION TO MONITOR>'
   # Ex: '/'
   URL_HIT='<REPLACE BY YOUR MISS_URI (a request to this URI should generate a HIT in the ma)>'
   # Ex: '/cache/0'
   URL_MISS='<REPLACE BY YOUR MISS URI> (a request to this URI should always generate a MISS)'
   ```

### Customize the project stack script for your use case

Edit ```simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/simple_cloudfront_canary_probe_stack.py``` and customize the ```vpcID, key_name and SSH_INGRESS_CIDR``` variables

    # vpc-123456
    vpcID="<YOUR VPC>"
    # name_of_your_ssh_key
    key_name="<YOUR SSH KEY>"
    # CIDR for SSH INGRESS to the instance where application will be executing
    SSH_INGRESS_CIDR="<YOUR_CIDR_FOR_SSH>"
    
### Deploy the project

    export CDK_DEFAULT_ACCOUNT=<YOUR AWS ACCOUNT NUMBER>
    export CDK_DEFAULT_REGION=<YOUR REGION>
    aws configure 
    cd simple_cloudfront_canary_probe
    cdk synth
    cdk bootstrap (only on first deployment)
    cdk deploy
