# CloudFormation ECS-EC2-Jenkins-Git Usage Guide

This guide explains how to deploy and manage separate development, production, and disaster recovery environments using the CloudFormation templates in this project.

## Prerequisites

Before you begin, ensure you have the following:

1. **AWS CLI** installed and configured with appropriate credentials
2. **AWS account** with permissions to create CloudFormation stacks and all required resources
3. AWS Region selected (templates default to `eu-west-2` if not specified)

## Project Structure

```
CloudFormation_ECS_EC2_Jenkins_Git/
├── templates/                  # CloudFormation templates
│   ├── master.yaml             # Main template that orchestrates all others
│   ├── network.yaml            # VPC, subnets, and network components
│   ├── iam.yaml                # IAM roles and policies
│   ├── ecs.yaml                # ECS clusters, services, and tasks
│   ├── database.yaml           # RDS database configuration
│   ├── cicd.yaml               # Jenkins and CI/CD resources
│   ├── monitoring.yaml         # CloudWatch and monitoring resources
│   ├── security.yaml           # Security groups and WAF configuration
│   ├── cache.yaml              # ElastiCache Redis configuration
│   ├── dr-pilot-light.yaml     # DR pilot light master template
│   ├── dr-lambda.yaml          # Lambda functions for DR failover
│   ├── route53-failover.yaml   # Route53 failover configuration
│   └── db-read-replica.yaml    # Database read replica for DR
├── dev-parameters.json         # Parameter values for development environment
├── prod-parameters.json        # Parameter values for production environment
├── dr-parameters.json          # Parameter values for DR environment
├── deploy-dev.bat              # Script to deploy dev environment (Windows)
├── deploy-prod.bat             # Script to deploy prod environment (Windows)
├── deploy-dr.bat               # Script to deploy DR environment (Windows)
└── USAGE.md                    # This usage guide
```

## Deploying Environments

### Option 1: Using Deployment Scripts (Recommended)

The easiest way to deploy any environment is to use the provided batch scripts:

#### Development Environment

```
deploy-dev.bat
```

This will deploy a stack named `dev-ecs-jenkins-infrastructure` using the parameters defined in `dev-parameters.json`.

#### Production Environment

```
deploy-prod.bat
```

This will deploy a stack named `prod-ecs-jenkins-infrastructure` using the parameters defined in `prod-parameters.json`.

#### DR Pilot Light Environment

```
deploy-dr.bat
```

This will deploy a stack named `dr-ecs-jenkins-infrastructure` using the parameters defined in `dr-parameters.json`.

### Option 2: Manual Deployment via AWS CLI

If you prefer to run the commands manually or need to customize them:

#### Development Environment

```bash
aws cloudformation deploy \
  --template-file templates/master.yaml \
  --stack-name dev-ecs-jenkins-infrastructure \
  --parameter-overrides file://dev-parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

#### Production Environment

```bash
aws cloudformation deploy \
  --template-file templates/master.yaml \
  --stack-name prod-ecs-jenkins-infrastructure \
  --parameter-overrides file://prod-parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

#### DR Pilot Light Environment

```bash
aws cloudformation deploy \
  --template-file templates/dr-pilot-light.yaml \
  --stack-name dr-ecs-jenkins-infrastructure \
  --parameter-overrides file://dr-parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### Option 3: AWS Management Console

1. Log in to the AWS Management Console
2. Navigate to CloudFormation
3. Click "Create stack" > "With new resources (standard)"
4. Upload `templates/master.yaml`
5. Specify stack name (`dev-ecs-jenkins-infrastructure` or `prod-ecs-jenkins-infrastructure`)
6. Input parameter values from the respective parameter file
7. Click through the remaining steps and select "Create stack"

## Environment Separation

Both environments are completely isolated from each other:

- Each has its own VPC (dev: 10.0.0.0/16, prod: 10.1.0.0/16)
- Each has dedicated subnets, security groups, and network ACLs
- Each has separate IAM roles with appropriate permissions
- Each has distinct ECS clusters, services, and ALBs
- Each uses separate databases, caches, and other resources
- Each can be updated, modified, or deleted without affecting the other

## Updating Environments

### Modifying Parameter Values

To change the configuration of an environment:

1. Edit the appropriate parameter file (`dev-parameters.json` or `prod-parameters.json`)
2. Run the deployment script or command again
3. CloudFormation will update only the resources that need to change

### Modifying Templates

If you need to change the templates themselves:

1. Edit the templates in the `templates/` directory
2. Run the deployment script or command again
3. CloudFormation will update the resources based on your changes

## Viewing Stack Resources

To see all the resources created by each stack:

### AWS Management Console

1. Navigate to CloudFormation in the AWS Console
2. Select the stack name (e.g., `dev-ecs-jenkins-infrastructure`)
3. Click on the "Resources" tab

### AWS CLI

```bash
# For development environment
aws cloudformation list-stack-resources --stack-name dev-ecs-jenkins-infrastructure

# For production environment
aws cloudformation list-stack-resources --stack-name prod-ecs-jenkins-infrastructure
```

## Accessing Your Applications

### Jenkins Access

Jenkins will be available at:

- Development: `https://jenkins-dev.[your-domain]`
- Production: `https://jenkins-prod.[your-domain]`

### Application Access

Your applications will be available at:

- Development: `https://app-dev.[your-domain]`
- Production: `https://app-prod.[your-domain]` or `https://[your-domain]`

## Common Operations

### Scaling Applications

To change the number of instances in your ECS cluster:

1. Edit the `MinCapacity` and `MaxCapacity` values in the parameter file
2. Redeploy the stack

### Adding New Resources

To add new resources:

1. Modify the appropriate template file
2. Add any new parameters to parameter files
3. Redeploy the stacks

### Testing DR Failover

To test the DR failover mechanism:

```bash
# Invoke the DR Lambda function with test mode
aws lambda invoke \
  --function-name ecs-jenkins-github-dr-dr-scale-up \
  --payload '{"test_mode": true, "test_duration_minutes": 30}' \
  response.json
```

This will:
1. Scale up the DR environment to the failover capacity
2. Run in this configuration for 30 minutes
3. Automatically scale back down to pilot light mode after the test

### Manually Triggering DR Failover

In a real disaster scenario, the failover would happen automatically via Route53 health checks. To manually trigger it:

```bash
# Invoke the DR Lambda without test mode
aws lambda invoke \
  --function-name ecs-jenkins-github-dr-dr-scale-up \
  --payload '{}' \
  response.json
```

## Deleting Environments

When you no longer need an environment, you can delete it:

### AWS Management Console

1. Navigate to CloudFormation
2. Select the stack
3. Click "Delete"

### AWS CLI

```bash
# For development environment
aws cloudformation delete-stack --stack-name dev-ecs-jenkins-infrastructure

# For production environment
aws cloudformation delete-stack --stack-name prod-ecs-jenkins-infrastructure

# For DR environment
aws cloudformation delete-stack --stack-name dr-ecs-jenkins-infrastructure
```

## Troubleshooting

### Failed Stack Creation

If stack creation fails:

1. Check the "Events" tab in the CloudFormation console
2. Look for the first resource that failed and note the error message
3. Fix the issue in the template or parameters
4. Delete the failed stack and try again

### Resource Limitations

If you encounter resource limits:

1. Request a service limit increase from AWS
2. Modify templates to use fewer resources

### Permission Issues

If you see permission errors:

1. Ensure your AWS user/role has the necessary permissions
2. Check IAM policies in the templates for correctness

## Best Practices

1. **Never make direct changes** to resources created by CloudFormation
2. Always update through CloudFormation to avoid drift
3. Use versioning for your templates (e.g., in a Git repository)
4. Test changes in development before applying to production
5. Back up important data before making significant changes
6. Use CloudFormation drift detection periodically to ensure consistency

## Additional Resources

- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/)
- [CloudFormation Template Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)