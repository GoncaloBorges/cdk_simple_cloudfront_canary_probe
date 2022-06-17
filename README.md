# cdk_simple_cloudfront_canary_probe

## Introduction

Amazon CloudFront is a web service to distribute content with low latency and high data transfer rates by serving requests using a network of edge locations around the world. Customers leveraging Amazon CloudFront have high expectation about its performance and are highly sensible to systemic or sporadic latency increases. The factors contributing for increased latency while serving web content via CloudFront vary but customer often lack the capability to correctly identify the different sources of latency, leading to an extended degraded user experience. 

This CDK stack deploys an EC2 instance on a VPC of your choice, executing a latency probe every minute. The latency probe is developed in Python3, and leverages PyCurl to perform 2 requests against a CloudFront Distribution distribution. The URIs of the requests is customizable but they should be served through path pattern behaviours configured with Server Timing Response Policy. One of the requests should always result in a MISS event so that the probe is able to assess upstream latency experience as experienced by CloudFront towards the origin.

## Metrics

The client captures the following data:

From PyCurl metrics:

•	The time PyCurl took to resolve the CloudFront distribution domain name 
•	The time PyCurl took to connect to the edge location 
•	The pretransfer time e.g. the time until the end of SSL/TLC negotiation
•	The starttransfer time, e.g. the until client receive the first byte 
•	The total elapsed time 

From CloudFront Server timing response headers:

•	The edge location which served the request
•	The type of event - Miss/Hit
•	The time CloudFront took to resolve the domain name of the origin (for Miss events)
•	The time CloudFront took to connect to the origin 
•	The time CloudFront expected until the first byte of the response is received from the origin 


##Requirements
* Configure a path pattern behaviour of your CloudFront Distribution with a server timing response header policy (please see here: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-response-headers-policies.html#server-timing-header)


### 1) NodeJS Install
Ref:  https://docs.aws.amazon.com/cdk/v2/guide/work-with.html#work-with-prerequisites

    wget https://nodejs.org/dist/v16.15.0/node-v16.15.0-linux-x64.tar.xz
    xz -d -v node-v16.15.0-linux-x64.tar.xz
    tar xvf node-v16.15.0-linux-x64.tar 
    export PATH=${PWD}/node-v16.15.0-linux-x64/bin:$PATH

### 2) Install CDKv2 framework
Ref: https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html

    python3 -m ensurepip --upgrade
    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade virtualenv
    npm install -g aws-cdk
    
### 3) Create the default 'simple_cloudfront_canary_probe' project

    mkdir simple_cloudfront_canary_probe/; cd simple_cloudfront_canary_probe/
    cdk init app --language python
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    cd ..

### 4) Download custom project files

    git clone https://github.com/GoncaloBorges/cdk_simple_cloudfront_canary_probe.git
    cp cdk_simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/app.py simple_cloudfront_canary_probe/
    cp cdk_simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/simple_cloudfront_canary_probe_stack.py simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/
    cp -r cdk_simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/user_data simple_cloudfront_canary_probe/

### 5) Customize the project user script

Edit ```simple_cloudfront_canary_probe/user_data/user_data.sh``` and customize the ```DISTRO, URL_HIT and URL_MISS``` variables 
 
   ```
   # Ex: 'd123456789.cloudfront.net'
   DISTRO='<REPLACE BY YOUR CLOUDFRONT DISTRIBUTION TO MONITOR>'
   # Ex: '/'
   URL_HIT='<REPLACE BY YOUR MISS_URI (a request to this URI should generate a HIT in the ma)>'
   # Ex: '/cache/0'
   URL_MISS='<REPLACE BY YOUR MISS URI> (a request to this URI should always generate a MISS)'
   ```

### 6) Customize the project stack script

Edit ```simple_cloudfront_canary_probe/simple_cloudfront_canary_probe/simple_cloudfront_canary_probe_stack.py``` and custome the ```vpcID, key_name and SSH_INGRESS_CIDR``` variables

    # vpc-123456
    vpcID="<YOUR VPC>"
    # name_of_your_ssh_key
    key_name="<YOUR SSH KEY>"
    # CIDR for SSH INGRESS to the instance where application will be executing
    SSH_INGRESS_CIDR="<YOUR_CIDR_FOR_SSH>"
    
### 7) Deploy the project

    export CDK_DEFAULT_ACCOUNT=<YOUR AWS ACCOUNT NUMBER>
    export CDK_DEFAULT_REGION=<YOUR REGION>
    aws configure 
    cdk synth; cdk deploy
