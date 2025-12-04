================================================================================
FTP SERVER - PART 2: AWS CLOUD DEPLOYMENT
================================================================================

TEAM MEMBERS
--------------------------------------------------------------------------------
1. Amir Valiulla (amir.valiulla@csu.fullerton.edu)
2. Joshua Yee (joshuayee@csu.fullerton.edu)
3. Randolph Brummett (rbrummett@csu.fullerton.edu)
4. Ric Escalante (rescalante12@csu.fullerton.edu)
5. Kush Bajaria (bajariakush@csu.fullerton.edu)

PROGRAMMING LANGUAGE
--------------------------------------------------------------------------------
Python 3


WHAT'S DIFFERENT FROM PART 1
--------------------------------------------------------------------------------
- Deployed FTP server to AWS EC2 cloud instance
- Server handles multiple clients at the same time using Python threading
- Clients can connect from anywhere (not just localhost)
- Used Terraform to automate AWS infrastructure setup


HOW TO DEPLOY TO AWS
--------------------------------------------------------------------------------

1. Install Terraform and configure AWS credentials:
   - Install Terraform: https://www.terraform.io/downloads
   - Configure AWS: aws configure

2. Create SSH key pair in AWS (if you don't have one):
   - Go to EC2 Console > Key Pairs > Create Key Pair
   - Download the .pem file
   - chmod 400 yourkey.pem

3. Deploy infrastructure:
   cd terraform
   terraform init
   terraform apply

   When prompted, enter your AWS key pair name.

4. Get your server IP address:
   terraform output

   Note the "public_ip" value.

5. Upload server files to EC2:
   scp -i ~/path/to/yourkey.pem server.py ubuntu@YOUR_EC2_IP:/home/ubuntu/
   scp -i ~/path/to/yourkey.pem client.py ubuntu@YOUR_EC2_IP:/home/ubuntu/

6. SSH into EC2 and start server:
   ssh -i ~/path/to/yourkey.pem ubuntu@YOUR_EC2_IP
   cd /home/ubuntu
   python3 server.py


HOW TO CONNECT CLIENTS
--------------------------------------------------------------------------------

Edit client.py line 9:
   Change: SERVER_IP = '127.0.0.1'
   To:     SERVER_IP = 'YOUR_EC2_PUBLIC_IP'

Run client:
   python3 client.py

Commands:
   > ls                    (list files)
   > get filename          (download file)
   > put filename          (upload file)
   > quit                  (exit)


MULTI-CLIENT TESTING
--------------------------------------------------------------------------------

To test multiple clients at once:

1. Make sure server is running on EC2

2. Open 3 different terminal windows on your computer

3. In each terminal, run:
   python3 client.py

4. All 3 clients should connect and work at the same time

The server uses Python threading (one thread per client) so it handles
multiple connections concurrently without blocking.


TERRAFORM FILES
--------------------------------------------------------------------------------

terraform/
├── main.tf           - Main infrastructure (EC2, security groups)
├── variables.tf      - Configuration variables
├── outputs.tf        - Output values (IP address, SSH command)
└── terraform.tfvars  - Your specific settings (key name, region)

What Terraform creates:
- EC2 instance (t2.micro, Ubuntu 22.04)
- Security group (allows ports 22, 11123, 49152-65535)
- Automatically installs Python 3


CLOUD DEPLOYMENT DETAILS
--------------------------------------------------------------------------------

AWS Region: us-east-1
Instance Type: t2.micro (free tier)
OS: Ubuntu 22.04 LTS
Python Version: 3.x

Ports opened:
- 22: SSH access
- 11123: FTP control connection
- 49152-65535: FTP data connections (dynamic ports)

The server uses dynamic port allocation for data connections, which is why
we need a wide port range open.


TESTING CHECKLIST
--------------------------------------------------------------------------------

✓ Server runs on EC2 without errors
✓ Can connect from local machine
✓ ls command works
✓ get command downloads files correctly
✓ put command uploads files correctly
✓ Multiple clients can connect at the same time
✓ Each client operates independently
✓ Server logs show multiple client connections


KNOWN ISSUES
--------------------------------------------------------------------------------

- EC2 public IP changes if you stop/start the instance
- Need to update client.py with new IP each time
- Security group had to be updated to allow wider port range (1024-65535)
  because Python was assigning ports outside the initial range


HOW TO CLEAN UP
--------------------------------------------------------------------------------

When done testing:

cd terraform
terraform destroy

This will delete the EC2 instance and stop AWS charges.


NOTES
--------------------------------------------------------------------------------

- Server code is the same as Part 1 (already had threading)
- Main difference is deployment to cloud and remote access
- Tested with 3 simultaneous clients successfully
- All Part 1 functionality works the same on AWS


================================================================================
