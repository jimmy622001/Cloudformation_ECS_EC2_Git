param(
    [Parameter(Mandatory=$true)]
    [string]$StackSetName,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "eu-west-1",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# Set AWS region
Write-Host "Setting AWS region to $Region..."
$env:AWS_DEFAULT_REGION = $Region

# First, let's check if the StackSet exists and determine if it's SERVICE_MANAGED
Write-Host "Checking if StackSet '$StackSetName' exists..."
$stackSetInfo = $null
try {
    # Add --call-as parameter to handle both SELF_MANAGED and SERVICE_MANAGED stack sets
    $stackSetInfo = aws cloudformation describe-stack-set --stack-set-name $StackSetName | ConvertFrom-Json
    Write-Host "StackSet found: $($stackSetInfo.StackSet.StackSetId)"
    $permissionModel = $stackSetInfo.StackSet.PermissionModel
    Write-Host "StackSet permission model: $permissionModel"
    
    # Check if it's a SERVICE_MANAGED stack set (Control Tower or StackSets with AWS Organizations)
    if ($permissionModel -eq "SERVICE_MANAGED") {
        Write-Host "This is a SERVICE_MANAGED stack set. Service-managed stack sets must be deleted using appropriate service-specific methods."
        Write-Host "For AWS Control Tower stack sets, you should manage them through Control Tower."
        Write-Host "For Organization stack sets, use --call-as DELEGATED_ADMIN or work with your organization administrator."
        
        $proceed = Read-Host "Do you want to attempt deletion anyway? (y/N)"
        if ($proceed -ne "y" -and $proceed -ne "Y") {
            Write-Host "Operation cancelled by user."
            exit 0
        }
    }
} catch {
    Write-Host "Error finding StackSet '$StackSetName':"
    Write-Host $_
    Write-Host "Please check the following:"
    Write-Host " - The exact stack set name (case-sensitive): $StackSetName"
    Write-Host " - Your AWS credentials and permissions"
    Write-Host " - The region is correct: $Region"
    exit 1
}

# Get all stack instances in the StackSet
Write-Host "Getting list of stack instances in StackSet '$StackSetName'..."
$callAsParam = ""
if ($permissionModel -eq "SERVICE_MANAGED") {
    $callAsParam = "--call-as DELEGATED_ADMIN"
}

try {
    $stackInstances = aws cloudformation list-stack-instances --stack-set-name $StackSetName $callAsParam | ConvertFrom-Json
    $instanceCount = $stackInstances.Summaries.Count
} catch {
    Write-Host "Error listing stack instances: $_"
    Write-Host "This could be due to permission issues with service-managed stack sets."
    exit 1
}

if ($instanceCount -gt 0) {
    Write-Host "Found $instanceCount stack instances that need to be deleted first."
    
    # Get unique combinations of account and region
    $accountRegionPairs = @{}
    foreach ($instance in $stackInstances.Summaries) {
        $key = "$($instance.Account),$($instance.Region)"
        $accountRegionPairs[$key] = @{
            Account = $instance.Account
            Region = $instance.Region
        }
    }
    
    # Create operation to delete all stack instances
    $operationId = $null
    
    if ($Force) {
        # Delete all instances at once with force
        Write-Host "Deleting all stack instances with force option..."
        try {
            $deleteCmd = "aws cloudformation delete-stack-instances --stack-set-name $StackSetName --accounts $([string]::Join(' ', ($accountRegionPairs.Values.Account | Select-Object -Unique))) --regions $([string]::Join(' ', ($accountRegionPairs.Values.Region | Select-Object -Unique))) --retention-policy RetainStacks=false --operation-preferences MaxConcurrentCount=10 --no-retain-stacks $callAsParam"
            Write-Host "Running command: $deleteCmd"
            $deleteOutput = Invoke-Expression $deleteCmd | ConvertFrom-Json
            $operationId = $deleteOutput.OperationId
        } catch {
            Write-Host "Error deleting stack instances: $_"
            exit 1
        }
    } else {
        # Delete each account-region pair separately
        foreach ($pair in $accountRegionPairs.Values) {
            Write-Host "Deleting stack instances in account $($pair.Account), region $($pair.Region)..."
            try {
                $deleteCmd = "aws cloudformation delete-stack-instances --stack-set-name $StackSetName --accounts $($pair.Account) --regions $($pair.Region) --retention-policy RetainStacks=false --operation-preferences MaxConcurrentCount=10 --no-retain-stacks $callAsParam"
                Write-Host "Running command: $deleteCmd"
                $deleteOutput = Invoke-Expression $deleteCmd | ConvertFrom-Json
                $operationId = $deleteOutput.OperationId
                
                # Wait for operation to complete
                Write-Host "Waiting for delete operation to complete..."
                aws cloudformation wait stack-set-operation-complete --stack-set-name $StackSetName --operation-id $operationId $callAsParam
            } catch {
                Write-Host "Error deleting stack instance: $_"
                # Continue with next pair
            }
        }
    }
    
    if ($Force -and $operationId) {
        # Wait for the delete operation to complete
        Write-Host "Waiting for all delete operations to complete..."
        aws cloudformation wait stack-set-operation-complete --stack-set-name $StackSetName --operation-id $operationId $callAsParam
    }
    
    # Check if any stack instances still exist
    try {
        $remainingInstances = aws cloudformation list-stack-instances --stack-set-name $StackSetName $callAsParam | ConvertFrom-Json
        if ($remainingInstances.Summaries.Count -gt 0) {
            Write-Host "Warning: $($remainingInstances.Summaries.Count) stack instances still exist. Cannot delete StackSet."
            exit 1
        }
    } catch {
        Write-Host "Error checking remaining instances: $_"
    }
}

# Delete the StackSet
Write-Host "Deleting StackSet '$StackSetName'..."
try {
    aws cloudformation delete-stack-set --stack-set-name $StackSetName $callAsParam
    Write-Host "StackSet deletion complete!"
} catch {
    Write-Host "Error deleting stack set: $_"
    exit 1
}