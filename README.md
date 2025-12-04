# CPSC 471 Network Programming Project

FTP Server Implementation - Parts 1 & 2

## Team Members
- Amir Valiulla
- Joshua Yee
- Randolph Brummett
- Ric Escalante
- Kush Bajaria

## Project Structure

```
471-project/
├── part1/              Part 1: Local FTP Server
│   ├── server.py       FTP server (localhost)
│   ├── client.py       FTP client
│   └── README.txt      Part 1 documentation
│
└── part2/              Part 2: AWS Cloud Deployment
    ├── server.py       Same FTP server (cloud-ready)
    ├── client.py       Same FTP client (remote access)
    ├── README.txt      Part 2 AWS deployment guide
    └── terraform/      Infrastructure as Code
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── terraform.tfvars.example
```

## Submission Files

**Part 1**: `p1-amir.tar` (contains part1/ directory)
**Part 2**: `p2-amir.tar` (contains part2/ directory)

## Quick Start

**Part 1 (Local):**
```bash
cd part1
python3 server.py    # Terminal 1
python3 client.py    # Terminal 2
```

**Part 2 (AWS):**
```bash
cd part2/terraform
terraform init
terraform apply
# Follow README.txt for deployment
```

## AWS Instance (Part 2)
- **Public IP**: 3.81.111.91
- **Status**: Running (for demo/testing)
- **Will destroy after**: Project submission
