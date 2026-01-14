"""
Setup RDS PostgreSQL for LAUTECH Agent
Creates a PostgreSQL instance with proper security and configuration
"""

import boto3
import json
import time
import random
import string
from botocore.exceptions import ClientError

# AWS Configuration
REGION = 'us-east-1'
DB_INSTANCE_IDENTIFIER = 'lautech-agentcore-db'
DB_NAME = 'lautech_db'
DB_USERNAME = 'lautech_admin'
SECRET_NAME = 'lautech/rds/credentials'

# RDS Configuration
DB_INSTANCE_CLASS = 'db.t3.micro'  # Cost-effective, eligible for free tier
ALLOCATED_STORAGE = 20  # GB
ENGINE = 'postgres'
ENGINE_VERSION = '16.11'  # Latest stable PostgreSQL 16


def generate_password(length=32):
    """Generate a secure random password (RDS compliant - no /, @, ", or space)"""
    # RDS allows printable ASCII except /, @, ", and space
    characters = string.ascii_letters + string.digits + '!#$%^&*()_+-=~`[]{}|;:,.<>?'
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def create_secret(password):
    """Create secret in AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name=REGION)

    secret_value = {
        'engine': ENGINE,
        'host': '',  # Will be updated after RDS creation
        'port': 5432,
        'username': DB_USERNAME,
        'password': password,
        'dbname': DB_NAME,
        'dbInstanceIdentifier': DB_INSTANCE_IDENTIFIER
    }

    try:
        response = client.create_secret(
            Name=SECRET_NAME,
            Description='LAUTECH RDS PostgreSQL credentials',
            SecretString=json.dumps(secret_value),
            Tags=[
                {'Key': 'Project', 'Value': 'LAUTECH-AgentCore'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        print(f"✅ Created secret: {SECRET_NAME}")
        print(f"   ARN: {response['ARN']}")
        return response['ARN']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceExistsException':
            print(f"⚠️  Secret {SECRET_NAME} already exists, updating...")
            response = client.update_secret(
                SecretId=SECRET_NAME,
                SecretString=json.dumps(secret_value)
            )
            # Get the ARN
            secret = client.describe_secret(SecretId=SECRET_NAME)
            return secret['ARN']
        else:
            raise


def get_default_vpc():
    """Get default VPC and subnets"""
    ec2 = boto3.client('ec2', region_name=REGION)

    # Get default VPC
    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
    if not vpcs['Vpcs']:
        raise Exception("No default VPC found")

    vpc_id = vpcs['Vpcs'][0]['VpcId']
    print(f"📡 Using default VPC: {vpc_id}")

    # Get subnets in default VPC
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    subnet_ids = [s['SubnetId'] for s in subnets['Subnets']]
    print(f"📡 Found {len(subnet_ids)} subnets: {subnet_ids}")

    return vpc_id, subnet_ids


def create_security_group(vpc_id):
    """Create security group for RDS"""
    ec2 = boto3.client('ec2', region_name=REGION)

    sg_name = f"{DB_INSTANCE_IDENTIFIER}-sg"
    sg_description = "Security group for LAUTECH RDS PostgreSQL"

    try:
        # Check if security group exists
        existing_sgs = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [sg_name]},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )

        if existing_sgs['SecurityGroups']:
            sg_id = existing_sgs['SecurityGroups'][0]['GroupId']
            print(f"⚠️  Security group {sg_name} already exists: {sg_id}")
            return sg_id

        # Create security group
        response = ec2.create_security_group(
            GroupName=sg_name,
            Description=sg_description,
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': [
                        {'Key': 'Name', 'Value': sg_name},
                        {'Key': 'Project', 'Value': 'LAUTECH-AgentCore'}
                    ]
                }
            ]
        )

        sg_id = response['GroupId']
        print(f"✅ Created security group: {sg_id}")

        # Add inbound rule for PostgreSQL (5432)
        # Note: In production, restrict this to Lambda security group or specific CIDR
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 5432,
                    'ToPort': 5432,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'PostgreSQL access'}]
                }
            ]
        )
        print("✅ Added inbound rule for PostgreSQL (port 5432)")

        return sg_id

    except ClientError as e:
        print(f"❌ Error creating security group: {e}")
        raise


def create_db_subnet_group(subnet_ids):
    """Create DB subnet group"""
    rds = boto3.client('rds', region_name=REGION)

    subnet_group_name = f"{DB_INSTANCE_IDENTIFIER}-subnet-group"

    try:
        response = rds.create_db_subnet_group(
            DBSubnetGroupName=subnet_group_name,
            DBSubnetGroupDescription='Subnet group for LAUTECH RDS',
            SubnetIds=subnet_ids,
            Tags=[
                {'Key': 'Project', 'Value': 'LAUTECH-AgentCore'}
            ]
        )
        print(f"✅ Created DB subnet group: {subnet_group_name}")
        return subnet_group_name
    except ClientError as e:
        if e.response['Error']['Code'] == 'DBSubnetGroupAlreadyExists':
            print(f"⚠️  DB subnet group {subnet_group_name} already exists")
            return subnet_group_name
        else:
            raise


def create_rds_instance(password, security_group_id, db_subnet_group_name):
    """Create RDS PostgreSQL instance"""
    rds = boto3.client('rds', region_name=REGION)

    try:
        # Check if instance already exists
        try:
            existing = rds.describe_db_instances(DBInstanceIdentifier=DB_INSTANCE_IDENTIFIER)
            if existing['DBInstances']:
                instance = existing['DBInstances'][0]
                status = instance['DBInstanceStatus']
                print(f"⚠️  RDS instance {DB_INSTANCE_IDENTIFIER} already exists with status: {status}")

                if status == 'available':
                    endpoint = instance['Endpoint']['Address']
                    port = instance['Endpoint']['Port']
                    print(f"✅ Instance is available at: {endpoint}:{port}")
                    return endpoint, port
                else:
                    print(f"⏳ Waiting for instance to become available (current status: {status})...")
                    return wait_for_instance_available()
        except ClientError as e:
            if e.response['Error']['Code'] != 'DBInstanceNotFound':
                raise

        # Create new instance
        print(f"🚀 Creating RDS instance {DB_INSTANCE_IDENTIFIER}...")
        print(f"   Instance class: {DB_INSTANCE_CLASS}")
        print(f"   Storage: {ALLOCATED_STORAGE} GB")
        print(f"   Engine: {ENGINE} {ENGINE_VERSION}")

        response = rds.create_db_instance(
            DBInstanceIdentifier=DB_INSTANCE_IDENTIFIER,
            DBName=DB_NAME,
            MasterUsername=DB_USERNAME,
            MasterUserPassword=password,
            DBInstanceClass=DB_INSTANCE_CLASS,
            Engine=ENGINE,
            EngineVersion=ENGINE_VERSION,
            AllocatedStorage=ALLOCATED_STORAGE,
            StorageType='gp3',  # General Purpose SSD
            StorageEncrypted=True,
            VpcSecurityGroupIds=[security_group_id],
            DBSubnetGroupName=db_subnet_group_name,
            PubliclyAccessible=True,  # For initial setup; restrict in production
            BackupRetentionPeriod=7,  # 7 days of automated backups
            PreferredBackupWindow='03:00-04:00',  # UTC
            PreferredMaintenanceWindow='sun:04:00-sun:05:00',  # UTC
            EnableCloudwatchLogsExports=['postgresql'],
            DeletionProtection=False,  # Set to True for production
            Tags=[
                {'Key': 'Name', 'Value': DB_INSTANCE_IDENTIFIER},
                {'Key': 'Project', 'Value': 'LAUTECH-AgentCore'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )

        print("✅ RDS instance creation initiated")
        print("⏳ Waiting for instance to become available (this may take 5-10 minutes)...")

        return wait_for_instance_available()

    except ClientError as e:
        print(f"❌ Error creating RDS instance: {e}")
        raise


def wait_for_instance_available():
    """Wait for RDS instance to become available"""
    rds = boto3.client('rds', region_name=REGION)

    max_attempts = 60  # 30 minutes (30 seconds * 60)
    attempt = 0

    while attempt < max_attempts:
        try:
            response = rds.describe_db_instances(DBInstanceIdentifier=DB_INSTANCE_IDENTIFIER)
            instance = response['DBInstances'][0]
            status = instance['DBInstanceStatus']

            if status == 'available':
                endpoint = instance['Endpoint']['Address']
                port = instance['Endpoint']['Port']
                print(f"\n✅ RDS instance is available!")
                print(f"   Endpoint: {endpoint}")
                print(f"   Port: {port}")
                return endpoint, port
            else:
                print(f"   Status: {status} (attempt {attempt + 1}/{max_attempts})", end='\r')
                time.sleep(30)
                attempt += 1

        except ClientError as e:
            if 'DBInstanceNotFound' in str(e):
                print(f"   Waiting for instance to be created... (attempt {attempt + 1}/{max_attempts})", end='\r')
                time.sleep(30)
                attempt += 1
            else:
                raise

    raise TimeoutError(f"RDS instance did not become available within {max_attempts * 30} seconds")


def update_secret_with_endpoint(endpoint, port):
    """Update secret with RDS endpoint"""
    client = boto3.client('secretsmanager', region_name=REGION)

    # Get current secret
    response = client.get_secret_value(SecretId=SECRET_NAME)
    secret_data = json.loads(response['SecretString'])

    # Update with endpoint
    secret_data['host'] = endpoint
    secret_data['port'] = port

    # Update secret
    client.update_secret(
        SecretId=SECRET_NAME,
        SecretString=json.dumps(secret_data)
    )

    print(f"✅ Updated secret {SECRET_NAME} with RDS endpoint")


def main():
    """Main setup function"""
    print("=" * 60)
    print("LAUTECH RDS PostgreSQL Setup")
    print("=" * 60)
    print()

    try:
        # Generate password
        print("🔐 Generating secure password...")
        password = generate_password()

        # Create secret
        print("\n📝 Creating AWS Secrets Manager secret...")
        secret_arn = create_secret(password)

        # Get VPC and subnets
        print("\n🌐 Getting VPC and subnets...")
        vpc_id, subnet_ids = get_default_vpc()

        # Create security group
        print("\n🔒 Creating security group...")
        security_group_id = create_security_group(vpc_id)

        # Create DB subnet group
        print("\n📡 Creating DB subnet group...")
        db_subnet_group_name = create_db_subnet_group(subnet_ids)

        # Create RDS instance
        print("\n🗄️  Creating RDS instance...")
        endpoint, port = create_rds_instance(password, security_group_id, db_subnet_group_name)

        # Update secret with endpoint
        print("\n📝 Updating secret with endpoint...")
        update_secret_with_endpoint(endpoint, port)

        # Print summary
        print("\n" + "=" * 60)
        print("✅ RDS Setup Complete!")
        print("=" * 60)
        print(f"DB Instance: {DB_INSTANCE_IDENTIFIER}")
        print(f"Endpoint: {endpoint}:{port}")
        print(f"Database: {DB_NAME}")
        print(f"Username: {DB_USERNAME}")
        print(f"Secret ARN: {secret_arn}")
        print(f"Secret Name: {SECRET_NAME}")
        print()
        print("Next steps:")
        print("1. Run the migration script to transfer data from SQLite")
        print("2. Update Lambda environment variables with secret ARN")
        print("3. Test the connection from Lambda")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        raise


if __name__ == "__main__":
    main()
