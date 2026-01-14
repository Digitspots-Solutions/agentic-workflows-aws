"""
Hardening LAUTECH RDS PostgreSQL
Enables production protections and demonstrates networking lockdown
"""

import boto3

REGION = 'us-east-1'
DB_IDENTIFIER = 'lautech-agentcore-db'

def enable_protections():
    """Enable RDS Deletion Protection and automated backups"""
    rds = boto3.client('rds', region_name=REGION)
    
    try:
        print(f"🔒 Enabling Deletion Protection for {DB_IDENTIFIER}...")
        rds.modify_db_instance(
            DBInstanceIdentifier=DB_IDENTIFIER,
            DeletionProtection=True,
            BackupRetentionPeriod=30, # Increase to 30 days for production
            ApplyImmediately=True
        )
        print("✅ Deletion Protection enabled.")
        print("✅ Backup retention increased to 30 days.")
    except Exception as e:
        print(f"❌ Error: {e}")

def lockdown_network():
    """
    WARNING: This will make the database inaccessible from your local machine.
    Only run this if the Agent and Dashboards are fully deployed to AWS.
    """
    rds = boto3.client('rds', region_name=REGION)
    print("\n⚠️  Manual Action Required for Networking Lockdown:")
    print("1. Set 'PubliclyAccessible' to False in the RDS Console.")
    print("2. Update the Security Group to only allow port 5432 from the Cloud's VPC CIDR.")
    print("3. Ensure the AgentCore Lambda is configured to run inside same VPC/Subnets.")

if __name__ == "__main__":
    enable_protections()
    lockdown_network()
