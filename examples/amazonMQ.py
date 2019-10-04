#!/usr/bin/python
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=missing-docstring
from __future__ import print_function
from troposphere.ec2 import (SecurityGroup, SecurityGroupEgress,
                             SecurityGroupIngress, SecurityGroupRule, Tags)
from troposphere import Output, Join, GetAtt, Export, ImportValue, Ref

from troposphere.amazonmq import User as BrokerUser
from troposphere.amazonmq import Broker, MaintenanceWindow, EncryptionOptions, LogsConfiguration

from troposphere import template as t


stack="stack"
projectCode="projectCode"
stackPrvAZa1="subnet1" # put here your first subnet in AZ1
stackPrvAZb1="subnet2" # put here your second subnet in AZ2
AMQBrokerName="MyBroker"

t.set_description(
    "AWS CloudFormation Template for the AMZ-MQ Components of the %s %s Project" % (stack, projectCode))


 brokerSG = t.add_resource(
     SecurityGroup(
         "amqbrokerSecurityGroup",
         GroupName=getSgName("amq"),
         GroupDescription="Enable Ingress traffic on associated ports for associated services",
         VpcId=ImportValue(stackVPCID),
         Tags=Tags({'gto:finops:projectcode': projectCode, 'Name': getSgName("amq")}),
 		SecurityGroupEgress=[
 			SecurityGroupRule(
 				CidrIp='127.0.0.1/32',
 				IpProtocol='-1'
 			)
 		]
 	)
 )



AMQBroker = t.add_resource(Broker(
    "%sAMQBroker" % stack,
    AutoMinorVersionUpgrade=False,
    # BrokerName="mqb-ibs-d-ew1-tmraus-issuancebroker2",
    BrokerName=AMQBrokerName,
    # Configuration=Ref(brokerConfiguration),
    DeploymentMode="ACTIVE_STANDBY_MULTI_AZ",
    EncryptionOptions=EncryptionOptions(
        #KmsKeyId = "aws:kms",
        UseAwsOwnedKey="True"
    ),
    EngineType="ACTIVEMQ",
    EngineVersion="5.15.9",
    HostInstanceType="mq.t2.micro",
    Logs=LogsConfiguration(
        Audit="True",
        General="True"
    ),
    MaintenanceWindowStartTime=MaintenanceWindow(
        DayOfWeek="Sunday",
        TimeOfDay="02:00",
        TimeZone="UTC"
    ),
    PubliclyAccessible=False,
    
    SecurityGroups=[Ref(AMQBrokerSG_ExportName)],
    SubnetIds=[ImportValue(stackPrvAZa1), ImportValue(stackPrvAZb1)],
    Tags=Tags({'gto:finops:projectcode': projectCode, 'Name': AMQBrokerName}),
    Users=[BrokerUser(
        ConsoleAccess="true",
        Password="AmazonMqPassword1",
        Username="AmazonMqUsername1"
    )]
))


ep = Join(",", GetAtt("%sAMQBroker" % stack, "OpenWireEndpoints"))
arn = GetAtt("%sAMQBroker" % stack, "Arn")


#export usefull info for using the Broker 
t.add_output([
    Output(
         "%sAMQBrokerOWEPExport" % stack,  # Key
        Value=ep,  # Value
        Export=Export("AMQBrokerOWEP_ExportName")  # Export Name
    )
])

t.add_output([
    Output(
         "%sAMQBrokerARNExport" % stack,  # Key
        Value=arn,  # Value
        Export=Export("AMQBrokerARN_ExportName")  # Export Name
    )
])


print(t.to_yaml())
