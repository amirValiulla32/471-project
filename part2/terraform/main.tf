# ============================================
# FTP Server Infrastructure on AWS
# ============================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ============================================
# Provider Configuration
# ============================================

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ============================================
# Data Sources
# ============================================

# Get latest Ubuntu 22.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Alternative: Amazon Linux 2 AMI (uncomment to use)
# data "aws_ami" "amazon_linux_2" {
#   most_recent = true
#   owners      = ["amazon"]
#
#   filter {
#     name   = "name"
#     values = ["amzn2-ami-hvm-*-x86_64-gp2"]
#   }
#
#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }
# }

# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# Get a subnet in the default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ============================================
# Security Group
# ============================================

resource "aws_security_group" "ftp_server" {
  name        = "${var.project_name}-${var.environment}-sg"
  description = "Security group for FTP server with two-connection architecture"

  # SSH access
  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  # FTP Control Connection
  ingress {
    description = "FTP Control Connection"
    from_port   = 11123
    to_port     = 11123
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # FTP Data Connection (static port - for testing)
  ingress {
    description = "FTP Data Connection (legacy)"
    from_port   = 11124
    to_port     = 11124
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Dynamic data ports range (for concurrent clients)
  ingress {
    description = "FTP Dynamic Data Ports"
    from_port   = 49152
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-sg"
  }
}

# ============================================
# EC2 Instance
# ============================================

resource "aws_instance" "ftp_server" {
  ami           = data.aws_ami.ubuntu.id
  # To use Amazon Linux 2 instead, change to: data.aws_ami.amazon_linux_2.id

  instance_type = var.instance_type
  key_name      = var.key_name

  # Use first available subnet in default VPC
  subnet_id = data.aws_subnets.default.ids[0]

  vpc_security_group_ids = [aws_security_group.ftp_server.id]

  # Enable public IP
  associate_public_ip_address = true

  # User data script for initial setup
  user_data = <<-EOF
              #!/bin/bash
              set -e

              # Log all output
              exec > >(tee /var/log/user-data.log)
              exec 2>&1

              echo "=== FTP Server Setup Started ==="
              echo "Timestamp: $(date)"

              # Update package manager
              echo "Updating packages..."
              apt-get update -y

              # Install Python 3 and pip (Ubuntu usually has Python 3 pre-installed)
              echo "Installing Python 3 and pip..."
              apt-get install -y python3 python3-pip

              # Verify Python installation
              python3 --version
              pip3 --version

              # Create FTP server directory
              echo "Creating FTP server directory..."
              mkdir -p /home/ubuntu/ftp-server
              chown ubuntu:ubuntu /home/ubuntu/ftp-server

              # Create a README in the FTP directory
              cat > /home/ubuntu/ftp-server/README.txt <<EOL
FTP Server Directory
====================

This directory is ready for your FTP server deployment.

To deploy your server:
1. Upload server.py and client.py to this directory
2. Run: python3 server.py

Server will listen on:
- Control port: 11123
- Data ports: Dynamic (49152-65535)

For testing locally:
- python3 client.py

For remote access:
- Update client.py SERVER_IP to this instance's public IP
- Ensure security group allows your IP
EOL

              chown ubuntu:ubuntu /home/ubuntu/ftp-server/README.txt

              # Create systemd service file for FTP server (optional, for auto-start)
              cat > /etc/systemd/system/ftp-server.service <<EOL
[Unit]
Description=Custom FTP Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ftp-server
ExecStart=/usr/bin/python3 /home/ubuntu/ftp-server/server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

              # Don't enable the service yet (no server.py uploaded)
              # systemctl enable ftp-server

              echo "=== FTP Server Setup Complete ==="
              echo "Instance is ready for FTP server deployment"
              EOF

  # Root volume configuration
  root_block_device {
    volume_size           = 8  # GB (free tier eligible)
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-root-volume"
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-instance"
  }
}
