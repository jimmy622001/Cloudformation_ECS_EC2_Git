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

# First, let's check if the StackSet exists
Write-Host "Checking if StackSet '$StackSetName' exists..."
$stackSetInfo = $null
try {
    $stackSetInfo = aws cloudformation describe-stack-set --stack-set-name $StackSetName | ConvertFrom-Json
    Write-Host "StackSet found: $($stackSetInfo.StackSet.StackSetId)"
} catch {
    Write-Host "StackSet '$StackSetName' not found. Please check the name and try again."
    exit 1
}

# Get all stack instances in the StackSet
Write-Host "Getting list of stack instances in StackSet '$StackSetName'..."
$stackInstances = aws cloudformation list-stack-instances --stack-set-name $StackSetName | ConvertFrom-Json
$instanceCount = $stackInstances.Summaries.Count

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
        $deleteOutput = aws cloudformation delete-stack-instances `
            --stack-set-name $StackSetName `
            --accounts $(($accountRegionPairs.Values.Account | Select-Object -Unique) -join " ") `
            --regions $(($accountRegionPairs.Values.Region | Select-Object -Unique) -join " ") `
            --retention-policy RetainStacks=false `
            --operation-preferences MaxConcurrentCount=10 `
            --no-retain-stacks | ConvertFrom-Json
        $operationId = $deleteOutput.OperationId
    } else {
        # Delete each account-region pair separately
        foreach ($pair in $accountRegionPairs.Values) {
            Write-Host "Deleting stack instances in account $($pair.Account), region $($pair.Region)..."
            $deleteOutput = aws cloudformation delete-stack-instances `
                --stack-set-name $StackSetName `
                --accounts $pair.Account `
                --regions $pair.Region `
                --retention-policy RetainStacks=false `
                --operation-preferences MaxConcurrentCount=10 `
                --no-retain-stacks | ConvertFrom-Json
            $operationId = $deleteOutput.OperationId
            
            # Wait for operation to complete
            Write-Host "Waiting for delete operation to complete..."
            aws cloudformation wait stack-set-operation-complete --stack-set-name $StackSetName --operation-id $operationId
        }
    }
    
    if ($Force -and $operationId) {
        # Wait for the delete operation to complete
        Write-Host "Waiting for all delete operations to complete..."
        aws cloudformation wait stack-set-operation-complete --stack-set-name $StackSetName --operation-id $operationId
    }
    
    # Check if any stack instances still exist
    $remainingInstances = aws cloudformation list-stack-instances --stack-set-name $StackSetName | ConvertFrom-Json
    if ($remainingInstances.Summaries.Count -gt 0) {
        Write-Host "Warning: $($remainingInstances.Summaries.Count) stack instances still exist. Cannot delete StackSet."
        exit 1
    }
}

# Delete the StackSet
Write-Host "Deleting StackSet '$StackSetName'..."
aws cloudformation delete-stack-set --stack-set-name $StackSetName

Write-Host "StackSet deletion complete!"