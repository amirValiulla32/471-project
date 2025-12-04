# ============================================
# Terraform Outputs
# ============================================

output "instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.ftp_server.id
}

output "public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_instance.ftp_server.public_ip
}

output "public_dns" {
  description = "The public DNS name of the EC2 instance"
  value       = aws_instance.ftp_server.public_dns
}

output "ssh_connection_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.ftp_server.public_ip}"
}

output "ftp_control_port" {
  description = "FTP control connection port"
  value       = "11123"
}

output "ftp_data_port_range" {
  description = "FTP data connection dynamic port range"
  value       = "49152-65535"
}

output "security_group_id" {
  description = "The ID of the security group"
  value       = aws_security_group.ftp_server.id
}
