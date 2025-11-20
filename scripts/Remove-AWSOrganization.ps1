param([string]$AccountId = "667021093945")

Write-Host "AWS Organization Removal Script" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow

# Check AWS CLI
$awsVersion = aws --version 2>$null
if (-not $awsVersion) {
    Write-Host "ERROR: AWS CLI not found" -ForegroundColor Red
    exit 1
}
Write-Host "AWS CLI found: $awsVersion" -ForegroundColor Green

# Verify account
Write-Host "Verifying account..." -ForegroundColor Cyan
$currentAccount = aws sts get-caller-identity --query Account --output text 2>$null
if (-not $currentAccount) {
    Write-Host "ERROR: Cannot verify account. Check credentials." -ForegroundColor Red
    exit 1
}
if ($currentAccount -ne $AccountId) {
    Write-Host "ERROR: Account mismatch. Expected: $AccountId, Current: $currentAccount" -ForegroundColor Red
    exit 1
}
Write-Host "Account confirmed: $currentAccount" -ForegroundColor Green

# Check organization
Write-Host "Checking organization..." -ForegroundColor Cyan
$orgResult = aws organizations describe-organization 2>$null
if (-not $orgResult) {
    Write-Host "No organization found" -ForegroundColor Yellow
    exit 0
}
$orgInfo = $orgResult | ConvertFrom-Json
Write-Host "Organization found: $($orgInfo.Organization.Id)" -ForegroundColor Green

# Check member accounts
Write-Host "Checking member accounts..." -ForegroundColor Cyan
$accountsResult = aws organizations list-accounts --output json 2>$null
if ($accountsResult) {
    $allAccounts = $accountsResult | ConvertFrom-Json
    $memberAccounts = $allAccounts.Accounts | Where-Object { $_.Id -ne $AccountId }
    
    if ($memberAccounts -and $memberAccounts.Count -gt 0) {
        Write-Host "WARNING: Found $($memberAccounts.Count) member account(s):" -ForegroundColor Red
        foreach ($account in $memberAccounts) {
            Write-Host "  - $($account.Name) ($($account.Id)) - Status: $($account.Status)" -ForegroundColor Yellow
        }
        Write-Host "Attempting to delete organization anyway..." -ForegroundColor Yellow
    } else {
        Write-Host "No member accounts found" -ForegroundColor Green
    }
}

# Final confirmation
Write-Host ""
Write-Host "FINAL WARNING: This will permanently delete the AWS Organization" -ForegroundColor Red
Write-Host "This action cannot be undone" -ForegroundColor Red
Write-Host ""

$finalConfirm = Read-Host "Type 'DELETE' to confirm"
if ($finalConfirm -ne "DELETE") {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 1
}

# Delete organization
Write-Host "Deleting organization..." -ForegroundColor Red
$deleteResult = aws organizations delete-organization 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Organization deleted successfully!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to delete organization" -ForegroundColor Red
    Write-Host $deleteResult -ForegroundColor Red
    exit 1
}

Write-Host "Organization removal completed!" -ForegroundColor Green