"""
Deploy LAUTECH Dashboards to AWS ECS Fargate
Properly supports WebSockets for Streamlit applications
"""

import boto3
import json
import time

REGION = 'us-east-1'
ACCOUNT_ID = '715841330456'
CLUSTER_NAME = 'lautech-cluster'
ECR_REPO = f'{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/lautech-dashboards:latest'

# Clients
ecs = boto3.client('ecs', region_name=REGION)
ec2 = boto3.client('ec2', region_name=REGION)
elbv2 = boto3.client('elbv2', region_name=REGION)
iam = boto3.client('iam', region_name=REGION)
logs = boto3.client('logs', region_name=REGION)


def create_cluster():
    """Create ECS cluster"""
    print("🚀 Creating ECS Cluster...")
    try:
        ecs.create_cluster(
            clusterName=CLUSTER_NAME,
            capacityProviders=['FARGATE', 'FARGATE_SPOT'],
            defaultCapacityProviderStrategy=[
                {'capacityProvider': 'FARGATE', 'weight': 1}
            ]
        )
        print(f"✅ Created cluster: {CLUSTER_NAME}")
    except ecs.exceptions.ClusterNotFoundException:
        pass
    except Exception as e:
        if 'already exists' in str(e).lower():
            print(f"⚠️  Cluster {CLUSTER_NAME} already exists")
        else:
            print(f"  Cluster may already exist: {e}")


def create_log_group(name):
    """Create CloudWatch log group"""
    try:
        logs.create_log_group(logGroupName=name)
        print(f"✅ Created log group: {name}")
    except logs.exceptions.ResourceAlreadyExistsException:
        print(f"⚠️  Log group {name} already exists")


def get_execution_role_arn():
    """Get or create ECS task execution role"""
    role_name = 'ecsTaskExecutionRole'
    try:
        response = iam.get_role(RoleName=role_name)
        return response['Role']['Arn']
    except iam.exceptions.NoSuchEntityException:
        # Create the role
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='ECS Task Execution Role for LAUTECH'
        )
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
        )
        # Also attach Secrets Manager access for RDS credentials
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/SecretsManagerReadWrite'
        )
        print(f"✅ Created execution role: {role_name}")
        time.sleep(5)  # Wait for role propagation
        return f'arn:aws:iam::{ACCOUNT_ID}:role/{role_name}'


def register_task_definition(name, app_type, env_vars):
    """Register a task definition"""
    execution_role_arn = get_execution_role_arn()
    log_group = f'/ecs/{name}'
    create_log_group(log_group)
    
    task_def = {
        'family': name,
        'networkMode': 'awsvpc',
        'requiresCompatibilities': ['FARGATE'],
        'cpu': '512',
        'memory': '1024',
        'executionRoleArn': execution_role_arn,
        'taskRoleArn': execution_role_arn,
        'containerDefinitions': [{
            'name': name,
            'image': ECR_REPO,
            'essential': True,
            'portMappings': [{
                'containerPort': 8501,
                'protocol': 'tcp'
            }],
            'environment': env_vars,
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': log_group,
                    'awslogs-region': REGION,
                    'awslogs-stream-prefix': 'ecs'
                }
            }
        }]
    }
    
    response = ecs.register_task_definition(**task_def)
    print(f"✅ Registered task definition: {name}")
    return response['taskDefinition']['taskDefinitionArn']


def get_default_vpc_and_subnets():
    """Get default VPC and public subnets"""
    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
    vpc_id = vpcs['Vpcs'][0]['VpcId']
    
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    subnet_ids = [s['SubnetId'] for s in subnets['Subnets'][:2]]  # Use first 2 subnets
    
    return vpc_id, subnet_ids


def create_security_group(vpc_id, name):
    """Create security group for ECS tasks"""
    sg_name = f'{name}-sg'
    try:
        existing = ec2.describe_security_groups(Filters=[
            {'Name': 'group-name', 'Values': [sg_name]},
            {'Name': 'vpc-id', 'Values': [vpc_id]}
        ])
        if existing['SecurityGroups']:
            return existing['SecurityGroups'][0]['GroupId']
    except:
        pass
    
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description=f'Security group for {name}',
        VpcId=vpc_id
    )
    sg_id = response['GroupId']
    
    # Allow inbound on port 8501 (Streamlit) and 80/443 for ALB
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 8501, 'ToPort': 8501, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
    )
    print(f"✅ Created security group: {sg_name}")
    return sg_id


def create_alb(name, vpc_id, subnet_ids, sg_id):
    """Create Application Load Balancer"""
    try:
        existing = elbv2.describe_load_balancers(Names=[name])
        if existing['LoadBalancers']:
            alb = existing['LoadBalancers'][0]
            print(f"⚠️  ALB {name} already exists")
            return alb['LoadBalancerArn'], alb['DNSName']
    except:
        pass
    
    response = elbv2.create_load_balancer(
        Name=name,
        Subnets=subnet_ids,
        SecurityGroups=[sg_id],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )
    alb = response['LoadBalancers'][0]
    print(f"✅ Created ALB: {name}")
    print(f"   DNS: {alb['DNSName']}")
    return alb['LoadBalancerArn'], alb['DNSName']


def create_target_group(name, vpc_id, port=8501):
    """Create target group for ALB"""
    try:
        existing = elbv2.describe_target_groups(Names=[name])
        if existing['TargetGroups']:
            return existing['TargetGroups'][0]['TargetGroupArn']
    except:
        pass
    
    response = elbv2.create_target_group(
        Name=name,
        Protocol='HTTP',
        Port=port,
        VpcId=vpc_id,
        TargetType='ip',
        HealthCheckPath='/_stcore/health',
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=10,
        HealthyThresholdCount=2,
        UnhealthyThresholdCount=5
    )
    print(f"✅ Created target group: {name}")
    return response['TargetGroups'][0]['TargetGroupArn']


def create_listener(alb_arn, tg_arn, port=80):
    """Create ALB listener"""
    try:
        elbv2.create_listener(
            LoadBalancerArn=alb_arn,
            Protocol='HTTP',
            Port=port,
            DefaultActions=[{'Type': 'forward', 'TargetGroupArn': tg_arn}]
        )
        print(f"✅ Created listener on port {port}")
    except Exception as e:
        if 'already exists' in str(e).lower() or 'DuplicateListener' in str(e):
            print(f"⚠️  Listener on port {port} already exists")
        else:
            raise


def create_service(task_def_arn, tg_arn, subnet_ids, sg_id, service_name):
    """Create ECS service"""
    try:
        existing = ecs.describe_services(cluster=CLUSTER_NAME, services=[service_name])
        if existing['services'] and existing['services'][0]['status'] != 'INACTIVE':
            print(f"⚠️  Service {service_name} already exists, updating...")
            ecs.update_service(
                cluster=CLUSTER_NAME,
                service=service_name,
                taskDefinition=task_def_arn,
                forceNewDeployment=True
            )
            return
    except:
        pass
    
    ecs.create_service(
        cluster=CLUSTER_NAME,
        serviceName=service_name,
        taskDefinition=task_def_arn,
        desiredCount=1,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': subnet_ids,
                'securityGroups': [sg_id],
                'assignPublicIp': 'ENABLED'
            }
        },
        loadBalancers=[{
            'targetGroupArn': tg_arn,
            'containerName': service_name,
            'containerPort': 8501
        }]
    )
    print(f"✅ Created service: {service_name}")


def deploy_dashboard(name, app_type, env_vars):
    """Deploy a single dashboard"""
    print(f"\n{'='*60}")
    print(f"Deploying {name}")
    print(f"{'='*60}")
    
    vpc_id, subnet_ids = get_default_vpc_and_subnets()
    sg_id = create_security_group(vpc_id, name)
    
    task_def_arn = register_task_definition(name, app_type, env_vars)
    
    alb_name = f'{name}-alb'
    alb_arn, dns_name = create_alb(alb_name, vpc_id, subnet_ids, sg_id)
    
    tg_arn = create_target_group(f'{name}-tg', vpc_id)
    create_listener(alb_arn, tg_arn)
    
    create_service(task_def_arn, tg_arn, subnet_ids, sg_id, name)
    
    return dns_name


def main():
    print("=" * 60)
    print("LAUTECH Dashboard Deployment to ECS Fargate")
    print("=" * 60)
    
    create_cluster()
    
    # Deploy Admin Panel
    admin_env = [
        {'name': 'APP_TYPE', 'value': 'admin'},
        {'name': 'USE_POSTGRES', 'value': 'true'},
        {'name': 'DB_SECRET_NAME', 'value': 'lautech/rds/credentials'},
        {'name': 'AWS_REGION', 'value': REGION}
    ]
    admin_dns = deploy_dashboard('lautech-admin', 'admin', admin_env)
    
    # Deploy Student Dashboard
    student_env = [
        {'name': 'APP_TYPE', 'value': 'web'},
        {'name': 'LAUTECH_AGENT_ID', 'value': 'lautech_agentcore-KLZaaW7AR6'},
        {'name': 'AWS_REGION', 'value': REGION}
    ]
    student_dns = deploy_dashboard('lautech-student', 'web', student_env)
    
    print("\n" + "=" * 60)
    print("✅ Deployment Complete!")
    print("=" * 60)
    print(f"\n📊 Admin Panel:     http://{admin_dns}")
    print(f"🎓 Student Dashboard: http://{student_dns}")
    print("\n⏳ Services take 2-3 minutes to become healthy.")
    print("=" * 60)


if __name__ == '__main__':
    main()
