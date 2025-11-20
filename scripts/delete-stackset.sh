#!/bin/bash

# Function to display usage
function usage {
    echo "Usage: $0 [options] STACKSET_NAME"
    echo "Options:"
    echo "  -r, --region REGION     AWS region (default: eu-west-1)"
    echo "  -f, --force             Force delete all stack instances at once"
    echo "  -h, --help              Display this help message"
    exit 1
}

# Default values
AWS_REGION="eu-west-1"
FORCE_DELETE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -f|--force)
            FORCE_DELETE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            STACKSET_NAME="$1"
            shift
            ;;
    esac
done

# Check if stack set name is provided
if [ -z "$STACKSET_NAME" ]; then
    echo "Error: StackSet name is required."
    usage
fi

# Set AWS region
export AWS_DEFAULT_REGION="$AWS_REGION"

echo "=== CloudFormation StackSet Deletion Tool ==="
echo "StackSet Name: $STACKSET_NAME"
echo "AWS Region: $AWS_REGION"
if [ "$FORCE_DELETE" = true ]; then
    echo "Force Delete: Enabled"
else
    echo "Force Delete: Disabled"
fi
echo "=========================================="

# Check if StackSet exists
echo "Checking if StackSet '$STACKSET_NAME' exists..."
if ! aws cloudformation describe-stack-set --stack-set-name "$STACKSET_NAME" > /dev/null 2>&1; then
    echo "Error: StackSet '$STACKSET_NAME' not found. Please check the name and try again."
    exit 1
fi

# Get all stack instances in the StackSet
echo "Getting list of stack instances in StackSet '$STACKSET_NAME'..."
STACK_INSTANCES=$(aws cloudformation list-stack-instances --stack-set-name "$STACKSET_NAME" --query 'Summaries[].[Account,Region]' --output text)

if [ -n "$STACK_INSTANCES" ]; then
    INSTANCE_COUNT=$(echo "$STACK_INSTANCES" | wc -l)
    echo "Found $INSTANCE_COUNT stack instances that need to be deleted first."
    
    # Get unique combinations of account and region
    declare -A account_regions
    while read -r account region; do
        key="${account},${region}"
        account_regions["$key"]="$account $region"
    done <<< "$STACK_INSTANCES"
    
    if [ "$FORCE_DELETE" = true ]; then
        # Get unique accounts and regions
        ACCOUNTS=$(echo "$STACK_INSTANCES" | awk '{print $1}' | sort -u | tr '\n' ' ')
        REGIONS=$(echo "$STACK_INSTANCES" | awk '{print $2}' | sort -u | tr '\n' ' ')
        
        echo "Deleting all stack instances with force option..."
        OPERATION_ID=$(aws cloudformation delete-stack-instances \
            --stack-set-name "$STACKSET_NAME" \
            --accounts $ACCOUNTS \
            --regions $REGIONS \
            --retention-policy RetainStacks=false \
            --operation-preferences MaxConcurrentCount=10 \
            --no-retain-stacks \
            --query 'OperationId' --output text)
        
        echo "Waiting for delete operation $OPERATION_ID to complete..."
        aws cloudformation wait stack-set-operation-complete --stack-set-name "$STACKSET_NAME" --operation-id "$OPERATION_ID"
    else
        # Delete each account-region pair separately
        for key in "${!account_regions[@]}"; do
            account_region=(${account_regions[$key]})
            account=${account_region[0]}
            region=${account_region[1]}
            
            echo "Deleting stack instances in account $account, region $region..."
            OPERATION_ID=$(aws cloudformation delete-stack-instances \
                --stack-set-name "$STACKSET_NAME" \
                --accounts "$account" \
                --regions "$region" \
                --retention-policy RetainStacks=false \
                --operation-preferences MaxConcurrentCount=10 \
                --no-retain-stacks \
                --query 'OperationId' --output text)
            
            echo "Waiting for delete operation $OPERATION_ID to complete..."
            aws cloudformation wait stack-set-operation-complete --stack-set-name "$STACKSET_NAME" --operation-id "$OPERATION_ID"
        done
    fi
    
    # Check if any stack instances still exist
    REMAINING=$(aws cloudformation list-stack-instances --stack-set-name "$STACKSET_NAME" --query 'Summaries[].{Account:Account,Region:Region}' --output text)
    if [ -n "$REMAINING" ]; then
        REMAINING_COUNT=$(echo "$REMAINING" | wc -l)
        echo "Warning: $REMAINING_COUNT stack instances still exist. Cannot delete StackSet."
        exit 1
    fi
fi

# Delete the StackSet
echo "Deleting StackSet '$STACKSET_NAME'..."
aws cloudformation delete-stack-set --stack-set-name "$STACKSET_NAME"

echo "StackSet deletion complete!"