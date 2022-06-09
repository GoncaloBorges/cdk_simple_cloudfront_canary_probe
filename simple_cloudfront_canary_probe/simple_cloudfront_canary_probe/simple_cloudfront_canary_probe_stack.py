from aws_cdk import (
    # Duration,
    App,Stack,
    aws_ec2 as ec2,
    aws_iam as iam, 
)
from constructs import Construct

vpcID="<YOUR VPC>"
key_name="<YOUR SSH KEY>"
SSH_INGRESS_CIDR="<YOUR_CIDR_FOR_SSH>"
instanceName="Ec2SimpleCloudfrontCanary"
instanceType="t2.small"
amiName="amzn2-ami-kernel-5.10-hvm-2.0.20220426.0-x86_64-gp2"

with open("./user_data/user_data.sh") as f:
    user_data = f.read()

class SimpleCloudfrontCanaryProbeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "SimpleCloudfrontCanaryProbeQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        # lookup existing VPC
        vpc = ec2.Vpc.from_lookup(
            self,
            "vpc",
            vpc_id=vpcID,
        )

        # create a new security group
        sec_group = ec2.SecurityGroup(
            self,
            "sec-group-allow-ssh",
            vpc=vpc,
            allow_all_outbound=True,
        )

        # add a new ingress rule to allow port 22 to internal hosts
        sec_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(SSH_INGRESS_CIDR),
            description="Allow SSH connection",
            connection=ec2.Port.tcp(22)
        )

        ec2_role = iam.Role(self, "Role_simple_cloudfront_canary_probe2", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        ec2_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=["cloudwatch:PutMetricData"],
            conditions={"StringEquals": {"cloudwatch:namespace": "Simple CloudFront Canary Probe"}}
            )
        )

        ec2_instance = ec2.Instance(
            self,
            "ec2-instance",
            instance_name=instanceName,
            instance_type=ec2.InstanceType(instanceType),
            machine_image=ec2.MachineImage().lookup(name=amiName),
            vpc=vpc,
            security_group=sec_group,
            key_name=key_name,
            role=ec2_role,
            user_data=ec2.UserData.custom(user_data),
        )

