#!/bin/bash
# Script to delete and recreate a stack in ROLLBACK_COMPLETE state

# Check parameters
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <stack-name> [aws-region]"
    echo "Example: $0 dev-stack eu-west-1"
    exit 1
fi

STACK_NAME=$1
AWS_REGION=${2:-"eu-west-1"}  # Default to eu-west-1 if not provided

# Check if stack exists
echo "Checking if stack $STACK_NAME exists..."
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION > /dev/null 2>&1; then
    echo "Stack $STACK_NAME exists. Checking status..."
    
    # Get stack status
    STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION --query "Stacks[0].StackStatus" --output text)
    
    if [[ "$STACK_STATUS" == "ROLLBACK_COMPLETE" ]]; then
        echo "Stack $STACK_NAME is in ROLLBACK_COMPLETE state. Deleting stack..."
        
        # Delete the stack
        aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION
        
        echo "Waiting for stack deletion to complete..."
        aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $AWS_REGION
        
        echo "Stack $STACK_NAME has been deleted successfully."
        echo "You can now redeploy the stack using your normal deployment process."
    else
        echo "Stack $STACK_NAME is in $STACK_STATUS state, not ROLLBACK_COMPLETE."
        echo "No action taken. If you still want to delete it, use the AWS console or AWS CLI directly."
    fi
else
    echo "Stack $STACK_NAME does not exist."
fi