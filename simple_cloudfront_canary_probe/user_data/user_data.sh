#!/bin/bash

# Ex: 'd123456789.cloudfront.net'
DISTRO='<REPLACE BY YOUR CLOUDFRONT DISTRIBUTION>'
# Ex: '/'
URL_HIT='<REPLACE BY YOUR MISS_URI>'
# Ex: '/cache/0'
URL_MISS='<REPLACE BY YOUR MISS URI>'

INSTALL_DIR=/scratch
mkdir -p $INSTALL_DIR/simple_cloudfront_canary_probe/

# Required packages
yum check-update 
yum install -y git gcc python3 python3-devel libcurl libcurl-devel openssl-devel 
python3 -m venv $INSTALL_DIR/simple_cloudfront_canary_probe/env
source $INSTALL_DIR/simple_cloudfront_canary_probe/env/bin/activate
pip install pip --upgrade
pip install boto3 pycurl

# Define cron job
METRIC_DIR=$INSTALL_DIR/simple_cloudfront_canary_probe/metric
mkdir $METRIC_DIR
cat <<EOF > $METRIC_DIR/PoPLatency.sh
#!/bin/bash
source /scratch/simple_cloudfront_canary_probe/env/bin/activate
$METRIC_DIR/PoPLatency.py $DISTRO $URL_HIT $URL_MISS
exit 0
EOF
chmod u+x $METRIC_DIR/PoPLatency.sh

# Install the probe from git
git clone https://github.com/GoncaloBorges/simple_cloudfront_canary_probe.git
cp simple_cloudfront_canary_probe/metric/PoPLatency.py $METRIC_DIR/PoPLatency.py
chmod u+x $METRIC_DIR/PoPLatency.py

chown -R ec2-user:ec2-user $INSTALL_DIR/simple_cloudfront_canary_probe

# Set up cron job to run the probe
cat <<EOF | crontab -u ec2-user -
* * * * * $METRIC_DIR/PoPLatency.sh >> $METRIC_DIR/PoPLatency.log 2>&1
EOF
systemctl status crond.service 

exit 0

