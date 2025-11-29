# FTP Server AWS Deployment with Terraform

This directory contains Terraform configuration to deploy your FTP server on AWS EC2.

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions to create EC2 instances and security groups
2. **Terraform** installed (>= 1.0): [Install Guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
3. **AWS CLI** configured with credentials: `aws configure`
4. **SSH Key Pair** created in AWS (or create one below)

## 🔑 Step 1: Create SSH Key Pair (if needed)

```bash
# Create key pair in AWS
aws ec2 create-key-pair \
  --key-name ftp-server-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/ftp-server-key.pem

# Set proper permissions
chmod 400 ~/.ssh/ftp-server-key.pem
```

## 🚀 Step 2: Deploy Infrastructure

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform (download providers)
terraform init

# Preview changes
terraform plan -var="key_name=ftp-server-key"

# Deploy (you'll be prompted to confirm)
terraform apply -var="key_name=ftp-server-key"

# Or auto-approve
terraform apply -var="key_name=ftp-server-key" -auto-approve
```

## 📤 Step 3: Upload FTP Server Files

After successful deployment, Terraform will output the public IP. Use it to upload your files:

```bash
# Get the public IP from Terraform output
export SERVER_IP=$(terraform output -raw public_ip)

# Upload server and client files
scp -i ~/.ssh/ftp-server-key.pem ../server.py ubuntu@$SERVER_IP:/home/ubuntu/ftp-server/
scp -i ~/.ssh/ftp-server-key.pem ../client.py ubuntu@$SERVER_IP:/home/ubuntu/ftp-server/
```

## 🖥️ Step 4: Start FTP Server

```bash
# SSH into the instance
ssh -i ~/.ssh/ftp-server-key.pem ubuntu@$SERVER_IP

# Navigate to FTP directory
cd /home/ubuntu/ftp-server

# Start the server
python3 server.py
```

You should see:
```
============================================================
FTP Server with Multi-Threaded Two-Connection Architecture
============================================================
Control connection listening on port 11123
Data connections use dynamically assigned ports
Ready to handle multiple concurrent clients
Waiting for clients...
```

## 🔌 Step 5: Connect from Client

On your **local machine**, update the client configuration:

```bash
# Update client.py to use the EC2 public IP
sed -i '' "s/SERVER_IP = '127.0.0.1'/SERVER_IP = '$SERVER_IP'/" ../client.py

# Or manually edit client.py:
# SERVER_IP = 'YOUR_EC2_PUBLIC_IP'

# Run the client
python3 ../client.py
```

## ⚙️ Configuration Options

### variables.tf

You can customize deployment by modifying these variables:

```hcl
# terraform.tfvars (create this file)
region         = "us-west-2"      # Change region
instance_type  = "t2.small"       # Upgrade instance
key_name       = "my-custom-key"  # Your SSH key name
environment    = "prod"           # Environment tag
```

Or pass variables via command line:
```bash
terraform apply \
  -var="key_name=my-key" \
  -var="region=us-west-2" \
  -var="instance_type=t2.small"
```

## 🔒 Security Group Configuration

The deployed security group allows:

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | 0.0.0.0/0 | SSH access |
| 11123 | TCP | 0.0.0.0/0 | FTP control connection |
| 11124 | TCP | 0.0.0.0/0 | FTP data (legacy/testing) |
| 49152-65535 | TCP | 0.0.0.0/0 | Dynamic data ports |

**Security Note**: For production, restrict SSH access to your IP only:
```bash
terraform apply -var="allowed_ssh_cidr=YOUR_IP/32"
```

## 🔄 Auto-Start Service (Optional)

To make the FTP server start automatically on boot:

```bash
# SSH into instance
ssh -i ~/.ssh/ftp-server-key.pem ubuntu@$SERVER_IP

# Enable and start the service
sudo systemctl enable ftp-server
sudo systemctl start ftp-server

# Check status
sudo systemctl status ftp-server

# View logs
sudo journalctl -u ftp-server -f
```

## 📊 Useful Commands

```bash
# Show outputs after deployment
terraform output

# Get just the public IP
terraform output -raw public_ip

# Get SSH command
terraform output -raw ssh_connection_command

# Show current state
terraform show

# Refresh outputs without redeploying
terraform refresh
```

## 🧹 Cleanup / Destroy Infrastructure

When done testing, destroy resources to avoid charges:

```bash
# Preview what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy -var="key_name=ftp-server-key"

# Auto-approve destruction
terraform destroy -var="key_name=ftp-server-key" -auto-approve
```

## 💰 Cost Estimation

**Free Tier Eligible** (first 12 months):
- t2.micro: 750 hours/month free
- 30 GB EBS storage free
- 15 GB data transfer out free

**After Free Tier** (~$0.01/hour for t2.micro):
- Instance: ~$8-10/month if running 24/7
- Storage: ~$1/month for 8GB
- Data transfer: Variable based on usage

**Cost Savings Tip**: Stop instance when not in use:
```bash
# Stop instance (keeps EBS, only pay for storage)
aws ec2 stop-instances --instance-ids $(terraform output -raw instance_id)

# Start instance again
aws ec2 start-instances --instance-ids $(terraform output -raw instance_id)
```

## 🐛 Troubleshooting

### Can't connect via SSH
```bash
# Check security group allows your IP
aws ec2 describe-security-groups --group-ids $(terraform output -raw security_group_id)

# Verify key permissions
ls -l ~/.ssh/ftp-server-key.pem  # Should be -r--------
```

### Can't connect to FTP server
```bash
# Check if server is running
ssh -i ~/.ssh/ftp-server-key.pem ubuntu@$SERVER_IP "ps aux | grep python"

# Check server logs
ssh -i ~/.ssh/ftp-server-key.pem ubuntu@$SERVER_IP "sudo journalctl -u ftp-server -n 50"

# Test connectivity
telnet $SERVER_IP 11123
```

### User data script issues
```bash
# Check user data logs
ssh -i ~/.ssh/ftp-server-key.pem ubuntu@$SERVER_IP "cat /var/log/user-data.log"
```

## 📁 File Structure

```
terraform/
├── README.md           # This file
├── main.tf            # Main infrastructure configuration
├── variables.tf       # Input variables
├── outputs.tf         # Output values
└── terraform.tfvars   # Variable values (create this, gitignored)
```

## 🔐 Important Notes

1. **Never commit** `terraform.tfvars` or `.pem` files to git
2. **Always** use key pairs for SSH, never password auth
3. **Consider** using AWS Secrets Manager for sensitive data
4. **Enable** CloudWatch monitoring for production deployments
5. **Use** Elastic IP if you need a static IP address

## 📚 Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [AWS Free Tier Details](https://aws.amazon.com/free/)

## 🎯 Next Steps

1. ✅ Deploy infrastructure with Terraform
2. ✅ Upload FTP server files
3. ✅ Test with multiple concurrent clients
4. 📈 Monitor performance with CloudWatch
5. 🔒 Harden security (restrict SSH, enable encryption)
6. 📦 Consider containerizing with Docker/ECS
