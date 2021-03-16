#!/usr/bin/env python3
"""EC2 Manager

Requires Python 3.8+

Simple script for starting and stopping EC2 instances. Requires that AWS credentials are
already set up as described here:

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html

Usage:
  ec2_manager.py (--list | --start INSTANCE | --stop INSTANCE) [ --quiet | --verbose] [--test]

Options:
  -h --help                 Show this screen.
  -v --version              Show version.
  -l --list                 Lists all registered EC2 instances in the user's account.
  --start=INSTANCE          Start an EC2 instance
  --stop=INSTANCE           Stop an EC2 instance
  --test                    Runs the program in test mode to check permissions. Does not stop or start instances.
  --quiet                   Print less text
  --verbose                 Print more text
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import boto3
from botocore.exceptions import ClientError
from docopt import docopt

VERSION = 0.1


@dataclass(eq=True, frozen=True)
class Settings:
    """
    Simple class to capture command line args as settings that can be passed around
    """

    instance_id: str
    test: bool = False
    verbose: bool = False
    quiet: bool = False


@dataclass(eq=True, frozen=True)
class EC2Instance:
    """
    Class to encapsulate EC2 instance details
    """

    image_id: str
    instance_id: str
    instance_type: str
    launch_time: datetime
    availability_zone: str
    private_dns_name: str
    private_ip_address: str
    public_ip_address: str
    public_dns_name: str
    state: str
    subnet_id: str
    vpc_id: str
    tags: List[Dict[str, str]]


class EC2Manager:
    def __init__(self, settings: Settings):
        self._settings = settings
        self.ec2 = boto3.client("ec2")

    @property
    def settings(self):
        return self._settings

    def list_instances(self) -> list[EC2Instance]:
        """
        Lists all registered EC2 instances
        """
        boto_response = self.ec2.describe_instances()
        instances = self.instance_from_response(boto_response)
        return instances

    @staticmethod
    def instance_from_response(response: Dict) -> List[EC2Instance]:
        """
        Unpacks the dictionary response from Boto3 and makes a nice dataclass with
        the some of the more useful details of the EC2 instance
        :param response: Boto3 response from a call to boto3.client("ec2").describe_instances()
        :return: List of EC2Instance objects
        """
        ec2_instances = []
        for reservation in response.get("Reservations"):
            for instance in reservation.get("Instances"):
                if dns := instance.get("PublicDnsName"):
                    public_dns_name = dns
                else:
                    public_dns_name = "NONE"
                if ip := instance.get("PublicIpAddress"):
                    public_ip_address = ip
                else:
                    public_ip_address = "NONE"
                ec2_instance = EC2Instance(
                    image_id=instance.get("ImageId"),
                    instance_id=instance.get("InstanceId"),
                    instance_type=instance.get("InstanceType"),
                    launch_time=instance.get("LaunchTime"),
                    availability_zone=instance.get("Placement").get("AvailabilityZone"),
                    private_dns_name=instance.get("PrivateDnsName"),
                    private_ip_address=instance.get("PrivateIpAddress"),
                    public_dns_name=public_dns_name,
                    public_ip_address=public_ip_address,
                    state=instance.get("State").get("Name"),
                    subnet_id=instance.get("SubnetId"),
                    vpc_id=instance.get("VpcId"),
                    tags=instance.get("Tags"),
                )
                ec2_instances.append(ec2_instance)

        return ec2_instances

    def print_instance_summary(self, instance: EC2Instance):
        """
        Prints summary of EC2 instance details
        """
        print(instance.instance_id)
        self.not_quiet("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.verbose_output(f"  AMI:         {instance.image_id}")
        self.not_quiet(f"  Type:        {instance.instance_type}")
        self.verbose_output(f"  Launched:    {instance.launch_time}")
        self.verbose_output(f"  AZ:          {instance.availability_zone}")
        self.verbose_output(f"  Private DNS: {instance.private_dns_name}")
        self.verbose_output(f"  Public DNS:  {instance.public_dns_name}")
        self.not_quiet(f"  Private IP:  {instance.private_ip_address}")
        self.not_quiet(f"  Public IP:   {instance.public_ip_address}")
        self.verbose_output(f"  Subnet Id:   {instance.subnet_id}")
        self.verbose_output(f"  VPC Id:      {instance.vpc_id}")
        self.not_quiet(f"  State:       {instance.state}")
        self.verbose_output(f"  Tags:        {instance.tags}")
        print()

    def start(self):
        """
        Start an EC2 instance
        :return: none
        """
        # Dry run to verify permissions
        try:
            self.ec2.start_instances(
                InstanceIds=[self.settings.instance_id], DryRun=True
            )
        except ClientError as e:
            if "DryRunOperation" not in str(e):
                if self.settings.test:
                    print(f"Test failed, can't start {self.settings.instance_id}.\n{e}")
            else:
                if self.settings.test:
                    print(
                        f"Test successful, able to start {self.settings.instance_id}."
                    )

        if self.settings.test:
            return

        # Dry run succeeded, run start_instances without dry run
        try:
            self.ec2.start_instances(
                InstanceIds=[self.settings.instance_id], DryRun=False
            )
        except ClientError as e:
            print(f"ERROR: {e}")
        else:
            print(f"Command successful, {self.settings.instance_id} is staring...")

    def stop(self):
        """
        Stop an EC2 instance
        :return: none
        """
        # Dry run to verify permissions
        try:
            self.ec2.stop_instances(
                InstanceIds=[self.settings.instance_id], DryRun=True
            )
        except ClientError as e:
            if "DryRunOperation" not in str(e):
                if self.settings.test:
                    print(f"Test failed, can't stop {self.settings.instance_id}.\n{e}")
            else:
                if self.settings.test:
                    print(f"Test successful, able to stop {self.settings.instance_id}.")

        if self.settings.test:
            return

        # Dry run succeeded, run start_instances without dry run
        try:
            self.ec2.stop_instances(
                InstanceIds=[self.settings.instance_id], DryRun=False
            )
        except ClientError as e:
            print(f"ERROR: {e}")
        else:
            print(f"Command successful, {self.settings.instance_id} is stopping...")

    def verbose_output(self, message: str):
        if self.settings.verbose:
            print(message)

    def not_quiet(self, message: str):
        if not self.settings.quiet:
            print(message)


if __name__ == "__main__":
    args = docopt(__doc__, version=f"EC2 Manager {VERSION}")
    list_mode = args.get("--list")
    if not list_mode:
        if instance_id := args.get("--start"):
            app_settings = Settings(
                instance_id=instance_id,
                test=args.get("--test"),
                verbose=args.get("--verbose"),
                quiet=args.get("--quiet"),
            )
            manager = EC2Manager(app_settings)
            manager.start()
        else:
            app_settings = Settings(
                instance_id=args.get("--stop"),
                test=args.get("--test"),
                verbose=args.get("--verbose"),
                quiet=args.get("--quiet"),
            )
            manager = EC2Manager(app_settings)
            manager.stop()
    else:
        # just list instances and quit
        app_settings = Settings(
            instance_id="",
            test=args.get("--test"),
            verbose=args.get("--verbose"),
            quiet=args.get("--quiet"),
        )
        manager = EC2Manager(app_settings)
        manager.not_quiet("Instances found in your AWS account:\n")
        all_instances = manager.list_instances()
        for i in all_instances:
            manager.print_instance_summary(instance=i)
