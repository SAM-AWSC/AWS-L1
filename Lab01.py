import boto3
import time

ec2 = boto3.client('ec2')

def create_vpc(cidr_block):
    response = ec2.create_vpc(CidrBlock=cidr_block)
    return response['Vpc']['VpcId']

def create_subnet(vpc_id, cidr_block, availability_zone):
    response = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock=cidr_block,
        AvailabilityZone=availability_zone
    )
    return response['Subnet']['SubnetId']

def create_internet_gateway():
    response = ec2.create_internet_gateway()
    return response['InternetGateway']['InternetGatewayId']

def attach_internet_gateway(vpc_id, igw_id):
    ec2.attach_internet_gateway(
        VpcId=vpc_id,
        InternetGatewayId=igw_id
    )

def create_nat_gateway(subnet_id, allocation_id):
    response = ec2.create_nat_gateway(
        SubnetId=subnet_id,
        AllocationId=allocation_id
    )
    return response['NatGateway']['NatGatewayId']

def wait_for_nat_gateway(nat_gateway_id):
    print(f"Waiting for NAT Gateway {nat_gateway_id} to become available...")
    while True:
        response = ec2.describe_nat_gateways(NatGatewayIds=[nat_gateway_id])
        state = response['NatGateways'][0]['State']
        if state == 'available':
            print("NAT Gateway is now available.")
            break
        elif state in ['failed', 'deleted']:
            raise Exception(f"NAT Gateway {nat_gateway_id} is in '{state}' state. Exiting.")
        else:
            print(f"Current NAT Gateway state: {state}. Waiting...")
            time.sleep(10)

def create_route_table(vpc_id):
    response = ec2.create_route_table(VpcId=vpc_id)
    return response['RouteTable']['RouteTableId']

def create_route(route_table_id, destination_cidr_block, gateway_id):
    ec2.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock=destination_cidr_block,
        GatewayId=gateway_id
    )

def associate_route_table(route_table_id, subnet_id):
    ec2.associate_route_table(
        RouteTableId=route_table_id,
        SubnetId=subnet_id
    )

# Create VPC
vpc_id = create_vpc('10.0.0.0/16')

# Create subnets
subnet_public1 = create_subnet(vpc_id, '10.0.0.0/24', 'us-east-1a')
subnet_private1 = create_subnet(vpc_id, '10.0.1.0/24', 'us-east-1a')
subnet_public2 = create_subnet(vpc_id, '10.0.2.0/24', 'us-east-1b')
subnet_private2 = create_subnet(vpc_id, '10.0.3.0/24', 'us-east-1b')

# Create Internet Gateway
igw_id = create_internet_gateway()
attach_internet_gateway(vpc_id, igw_id)

# Allocate Elastic IP for NAT Gateway
allocation = ec2.allocate_address(Domain='vpc')
nat_gateway_id = create_nat_gateway(subnet_public1, allocation['AllocationId'])

# Wait for NAT Gateway to be available
wait_for_nat_gateway(nat_gateway_id)

# Create route tables
public_rt_id = create_route_table(vpc_id)
private_rt_id = create_route_table(vpc_id)

# Create routes
create_route(public_rt_id, '0.0.0.0/0', igw_id)
create_route(private_rt_id, '0.0.0.0/0', nat_gateway_id)

# Associate route tables with subnets
associate_route_table(public_rt_id, subnet_public1)
associate_route_table(public_rt_id, subnet_public2)
associate_route_table(private_rt_id, subnet_private1)
associate_route_table(private_rt_id, subnet_private2)

print("VPC, Subnets, Route Tables, and Gateways successfully created.")
