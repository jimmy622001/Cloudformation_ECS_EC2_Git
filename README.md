# CloudFormation ECS-EC2-Jenkins-Git Infrastructure

This repository contains AWS CloudFormation templates to deploy a complete infrastructure consisting of:

- Amazon ECS cluster with EC2 instances
- Jenkins CI/CD pipeline integrated with Git
- RDS database (PostgreSQL/MySQL)
- ElastiCache Redis
- Monitoring with CloudWatch, Prometheus, and Grafana
- Security features including WAF, GuardDuty, and Security Hub

## Architecture Overview

The infrastructure is deployed using nested CloudFormation templates to maintain modularity and reusability:

- **master.yaml** - The main template that orchestrates all other resources
- **network.yaml** - Creates VPC, subnets, security groups, and other networking resources
- **iam.yaml** - Creates IAM roles and policies
- **ecs.yaml** - Deploys the ECS cluster with EC2 instances, ALB, and services
- **database.yaml** - Creates RDS database instances
- **cicd.yaml** - Deploys Jenkins and CodeDeploy resources
- **monitoring.yaml** - Sets up monitoring solutions
- **security.yaml** - Configures security services
- **cache.yaml** - Deploys ElastiCache Redis

## Prerequisites

- AWS CLI configured with appropriate permissions
- AWS credentials with permissions to create all required resources
- S3 bucket for storing templates (optional, for nested stacks)

## Deployment Instructions

### Option 1: Using GitHub Actions (Recommended)

This project is configured to use GitHub Actions for CI/CD (see [docs/CICD.md](docs/CICD.md) for details):

1. Fork this repository to your GitHub account
2. Set up the required GitHub secrets:
   - `AWS_ROLE_ARN`: The ARN of the IAM role for GitHub Actions (see `.github/workflows/deploy.yml`)
3. Push changes to trigger the workflow or manually trigger it from the Actions tab
4. The workflow will validate and deploy your CloudFormation templates

### Option 2: Using AWS Management Console

1. Upload all templates to an S3 bucket
2. Navigate to the CloudFormation console
3. Create a new stack and upload the master.yaml template
4. Set the parameters as needed
5. Review and create the stack

### Option 3: Using AWS CLI

```bash
aws cloudformation create-stack \
  --stack-name ecs-jenkins-github \
  --template-body file://templates/master.yaml \
  --parameters \
    ParameterKey=ProjectName,ParameterValue=ecs-jenkins-github \
    ParameterKey=Environment,ParameterValue=dev \
    ParameterKey=AWSRegion,ParameterValue=eu-west-2 \
  --capabilities CAPABILITY_NAMED_IAM
```

## Environment Configuration

The infrastructure supports multiple environments (dev, test, prod) with different configurations. Key parameters include:

- **ProjectName** - The name of the project used for resource naming
- **Environment** - The deployment environment (dev, test, prod)
- **AWSRegion** - The AWS region where resources will be deployed

## Resources Created

### Networking
- VPC with public, private, database, and cache subnets
- Internet Gateway and NAT Gateways for outbound connectivity
- Security Groups for each component

### Compute
- ECS Cluster running on EC2 instances
- Auto Scaling Groups for ECS instances
- Load Balancer for application traffic

### Database
- RDS instance (PostgreSQL or MySQL)
- Parameter groups and option groups

### CI/CD
- Jenkins server on EC2
- CodeDeploy application and deployment group
- S3 bucket for artifacts

### Caching
- ElastiCache Redis cluster

### Monitoring
- CloudWatch dashboards and alarms
- Prometheus for metrics collection
- Grafana for visualization

### Security
- WAF for web application protection
- GuardDuty for threat detection
- Security Hub for security compliance
- AWS Config for resource tracking

## Customization

You can customize the deployment by modifying the parameters in the master.yaml file or directly modifying the templates.

## Cleanup

To delete all resources created by the stack:

```bash
aws cloudformation delete-stack --stack-name ecs-jenkins-github
```

Note that some resources like S3 buckets with content will need to be emptied before deletion.

## Converting from Terraform

This CloudFormation project was converted from a Terraform project. The main differences include:

1. **State Management** - CloudFormation manages state internally, while Terraform requires explicit state management
2. **Template Structure** - CloudFormation uses nested stacks for modularity instead of Terraform modules
3. **Resource Referencing** - CloudFormation uses intrinsic functions like !Ref and !GetAtt instead of Terraform's interpolation syntax

## Security Notes

- The default SSH access is configured to allow access from any IP (0.0.0.0/0). For production environments, this should be restricted.
- Secret values are managed using AWS Secrets Manager and AWS Systems Manager Parameter Store.
- In production environments, encryption is enabled for all applicable resources.

## Project Structure

The project structure has been organized as follows:

- `/.github/workflows/` - GitHub Actions workflow files for CI/CD
- `/templates/` - CloudFormation templates
- `/scripts/` - Utility scripts for template validation and management
- `/security/` - Security-related scripts and tools
- `/docs/` - Project documentation files
- Parameter files (*.json) - Environment-specific parameter files in the root directory

## Secure Secrets Management

This repository includes enhanced security features for managing secrets. Please review the following files:

- [security/setup-aws-secrets.sh](security/setup-aws-secrets.sh) - Script to securely store secrets in AWS Secrets Manager
- [docs/PARAMETER_MANAGEMENT.md](docs/PARAMETER_MANAGEMENT.md) - Documentation on parameter management

Make the scripts executable before using them:

```bash
chmod +x security/setup-aws-secrets.sh
```

**Important**: If you have found a security issue, please contact the security team.