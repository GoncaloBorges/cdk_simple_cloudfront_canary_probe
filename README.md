# cdk_simple_cloudfront_canary_probe

### 0) Requirements
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
