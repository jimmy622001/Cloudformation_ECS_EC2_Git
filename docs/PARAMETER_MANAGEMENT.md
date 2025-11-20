# CloudFormation Parameter Management

This document explains how sensitive information is managed in the CloudFormation templates using AWS Systems Manager Parameter Store and Secrets Manager.

## Sensitive Parameters

The CloudFormation templates have been updated to use references to AWS Systems Manager Parameter Store and Secrets Manager instead of hard-coding sensitive values. The following parameters are stored externally:

1. **Database Credentials**
   - Username: Stored in SSM Parameter Store at `/ecs-jenkins-github/db/username`
   - Password: Auto-generated and stored in Secrets Manager by the Database stack

2. **Grafana Dashboard**
   - Password: Stored as a secure parameter in SSM Parameter Store at `/ecs-jenkins-github/grafana/password`

3. **Network Security**
   - SSH CIDR Range: Stored in SSM Parameter Store at `/ecs-jenkins-github/network/allowed-ssh-cidr`

4. **Domain Configuration**
   - Domain Name: Stored in SSM Parameter Store at `/ecs-jenkins-github/ecs/domain-name`

5. **GitHub Integration**
   - Repository: Stored in SSM Parameter Store at `/ecs-jenkins-github/cicd/github-repository`

## Setup Process

To set up the required parameters:

1. Run the included `setup-ssm-parameters.sh` script:
   ```bash
   ./setup-ssm-parameters.sh
   ```

2. Update the default values with your actual values using either:
   - AWS Management Console
   - AWS CLI:
     ```bash
     # For standard parameters:
     aws ssm put-parameter --name "/ecs-jenkins-github/parameter-name" --value "your-value" --type "String" --overwrite
     
     # For secure parameters:
     aws ssm put-parameter --name "/ecs-jenkins-github/secure-parameter" --value "your-secure-value" --type "SecureString" --overwrite
     ```

## How Parameter References Work

The CloudFormation templates use dynamic references to access these parameters:

- **SSM Parameter Store (standard):**
  ```yaml
  Parameter: '{{resolve:ssm:/ecs-jenkins-github/parameter-name:1}}'
  ```

- **SSM Parameter Store (secure):**
  ```yaml
  SecureParameter: '{{resolve:ssm-secure:/ecs-jenkins-github/secure-parameter:1}}'
  ```

- **Secrets Manager:**
  ```yaml
  SecretValue: '{{resolve:secretsmanager:secret-id:SecretString:json-key}}'
  ```

## Benefits of External Parameter Storage

1. **Security:** Sensitive values are not persisted in template files
2. **Centralized Management:** Update parameters in one place
3. **Version Control:** Parameter Store supports versioning
4. **Access Control:** Fine-grained IAM permissions for parameters
5. **Audit Trail:** Changes to parameters are logged in CloudTrail

## Additional Notes

- Database passwords are automatically generated during stack creation using Secrets Manager
- Ensure your CloudFormation service role has access to read from Parameter Store and Secrets Manager
- Consider using AWS KMS customer managed keys for additional encryption security