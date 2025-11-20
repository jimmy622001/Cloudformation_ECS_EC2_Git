param([string]$AccountId = "667021093945")

Write-Host "AWS Organization Member Account Removal" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow

# Get member accounts
$accountsResult = aws organizations list-accounts --output json 2>$null
if (-not $accountsResult) {
    Write-Host "ERROR: Cannot list accounts" -ForegroundColor Red
    exit 1
}

$allAccounts = $accountsResult | ConvertFrom-Json
$memberAccounts = $allAccounts.Accounts | Where-Object { $_.Id -ne $AccountId }

if (-not $memberAccounts -or $memberAccounts.Count -eq 0) {
    Write-Host "No member accounts found" -ForegroundColor Green
    exit 0
}

Write-Host "Found $($memberAccounts.Count) member accounts:" -ForegroundColor Cyan
foreach ($account in $memberAccounts) {
    Write-Host "  - $($account.Name) ($($account.Id)) - Status: $($account.Status)" -ForegroundColor White
}

Write-Host ""
Write-Host "WARNING: This will remove ALL member accounts from the organization" -ForegroundColor Red
Write-Host "Member accounts will become standalone AWS accounts" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Do you want to remove all member accounts? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 1
}

# Remove each member account
foreach ($account in $memberAccounts) {
    if ($account.Status -eq "ACTIVE") {
        Write-Host "Removing: $($account.Name) ($($account.Id))" -ForegroundColor Yellow
        $result = aws organizations remove-account-from-organization --account-id $account.Id 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  SUCCESS: Account removed" -ForegroundColor Green
        } else {
            Write-Host "  ERROR: $result" -ForegroundColor Red
        }
    } else {
        Write-Host "Skipping: $($account.Name) - Status: $($account.Status)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Member account removal completed!" -ForegroundColor Green
Write-Host "You can now run the organization removal script." -ForegroundColor Green