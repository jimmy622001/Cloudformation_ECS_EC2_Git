# PowerShell script to delete and recreate a stack in ROLLBACK_COMPLETE state

param (
    [Parameter(Mandatory=$true)]
    [string]$StackName,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "eu-west-1"
)

# Check if stack exists
Write-Host "Checking if stack $StackName exists..."
try {
    $stack = aws cloudformation describe-stacks --stack-name $StackName --region $Region | ConvertFrom-Json
    
    # Get stack status
    $stackStatus = $stack.Stacks[0].StackStatus
    
    if ($stackStatus -eq "ROLLBACK_COMPLETE") {
        Write-Host "Stack $StackName is in ROLLBACK_COMPLETE state. Deleting stack..."
        
        # Delete the stack
        aws cloudformation delete-stack --stack-name $StackName --region $Region
        
        Write-Host "Waiting for stack deletion to complete..."
        aws cloudformation wait stack-delete-complete --stack-name $StackName --region $Region
        
        Write-Host "Stack $StackName has been deleted successfully."
        Write-Host "You can now redeploy the stack using your normal deployment process."
    } else {
        Write-Host "Stack $StackName is in $stackStatus state, not ROLLBACK_COMPLETE."
        Write-Host "No action taken. If you still want to delete it, use the AWS console or AWS CLI directly."
    }
} catch {
    Write-Host "Stack $StackName does not exist or there was an error: $_"
}