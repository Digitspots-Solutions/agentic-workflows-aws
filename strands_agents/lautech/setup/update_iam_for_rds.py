"""
Update IAM role permissions for LAUTECH AgentCore
Adds RDS and Secrets Manager access for the correct account
"""

import boto3
import json

# Configuration for CORRECT account (715841330456)
ROLE_NAME = "AmazonBedrockAgentCoreSDKRuntime-us-east-1-7fed580dbf"
SECRET_ARN = "arn:aws:secretsmanager:us-east-1:715841330456:secret:lautech/rds/credentials-*"
RDS_ARN = "arn:aws:rds:us-east-1:715841330456:db:lautech-agentcore-db"
REGION = "us-east-1"


def attach_rds_policy():
    """Attach RDS and Secrets Manager policy to role"""
    iam = boto3.client('iam', region_name=REGION)

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "SecretsManagerAccess",
                "Effect": "Allow",
                "Action": [
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret"
                ],
                "Resource": SECRET_ARN
            },
            {
                "Sid": "RDSDescribe",
                "Effect": "Allow",
                "Action": [
                    "rds:DescribeDBInstances",
                    "rds:DescribeDBClusters"
                ],
                "Resource": RDS_ARN
            }
        ]
    }

    policy_name = "LAUTECHRDSAccessPolicy"

    try:
        # Attach inline policy
        iam.put_role_policy(
            RoleName=ROLE_NAME,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )

        print(f"✅ Successfully attached policy '{policy_name}' to role '{ROLE_NAME}'")
        print(f"\n📜 Policy allows:")
        print(f"   - Secrets Manager: GetSecretValue, DescribeSecret")
        print(f"   - RDS: DescribeDBInstances")
        print(f"\n🔐 Secret ARN: {SECRET_ARN}")
        print(f"📊 RDS ARN: {RDS_ARN}")

        return True

    except Exception as e:
        print(f"❌ Error attaching policy: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("Update IAM Permissions for LAUTECH AgentCore")
    print(f"Account: 715841330456")
    print(f"Role: {ROLE_NAME}")
    print("=" * 60)
    print()

    if attach_rds_policy():
        print("\n" + "=" * 60)
        print("✅ IAM permissions updated successfully!")
        print("=" * 60)
        print("\nThe agent can now:")
        print("1. Access RDS credentials from Secrets Manager")
        print("2. Connect to PostgreSQL database")
        print("3. Query and manage LAUTECH data")
        print("\nTest with:")
        print('agentcore invoke \'{"prompt": "What are the fees for 100 Level?"}\' ')
        print("=" * 60)
    else:
        print("\n❌ Failed to update IAM permissions")


if __name__ == "__main__":
    main()
