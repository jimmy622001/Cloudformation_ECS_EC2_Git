# Fixing Nested Stack Parameter Issues

This document outlines the specific E3043 errors detected by cfn-lint and provides instructions for fixing them.

## Background

The E3043 error occurs when a parameter specified in a nested stack doesn't exist in the target template. This happens when:
1. A nested stack refers to parameters that don't exist in the nested template
2. A parameter required by the nested template isn't provided by the parent template

## Issues to Fix

1. In `templates/dr-pilot-light.yaml`:
   - `VpcId` parameter doesn't exist in `SecurityStack` - This needs to be added to `security.yaml`
   - `ECSOptimizedAMI` missing in `ECSStack` - This needs to be added to `ecs.yaml`
   - `ContainerInsights` parameter doesn't exist in `ECSStack` - This needs to be added to `ecs.yaml`
   - `UseSpotInstances` parameter doesn't exist in `ECSStack` - This needs to be added to `ecs.yaml`
   - `OnDemandPercentage` parameter doesn't exist in `ECSStack` - This needs to be added to `ecs.yaml`
   - `VpcId` and `DBEngineVersion` parameters don't exist in `DatabaseReadReplica` - These need to be added to `db-read-replica.yaml`

2. In `templates/master.yaml`:
   - `VpcId` parameter doesn't exist in `SecurityStack` - This needs to be added to `security.yaml`
   - `ECSOptimizedAMI` missing in `ECSStack` - This needs to be added to `ecs.yaml`
   - `ContainerInsights` parameter doesn't exist in `ECSStack` - This needs to be added to `ecs.yaml` 
   - `JenkinsAMI` parameter missing in `CICDStack` - This needs to be added to `cicd.yaml`
   - `GithubRepository` parameter doesn't exist in `CICDStack` - This needs to be added to `cicd.yaml`
   - `PrivateSubnets` and `PublicSubnets` parameters don't exist in `MonitoringStack` - These need to be added to `monitoring.yaml`

## Steps to Fix

For each issue:

1. Open the referenced nested template
2. Add the missing parameters with appropriate defaults and descriptions
3. Update the nested stack logic to use these parameters properly
4. Run cfn-lint again to verify the fixes

## Example Fixes

### Adding VpcId to security.yaml:

```yaml
Parameters:
  # Add missing parameter
  VpcId:
    Type: String
    Description: VPC ID to deploy security resources in
```

### Adding ECSOptimizedAMI to ecs.yaml:

```yaml
Parameters:
  # Add missing parameter
  ECSOptimizedAMI:
    Type: String
    Description: AMI ID for ECS optimized instances
    Default: ""  # Default empty to use latest via SSM parameter
```

After completing these fixes, the E3043 errors should be resolved, leading to more reliable CloudFormation deployments.