param([string]$AccountId = "667021093945")

Write-Host "AWS Suspended Account Removal" -ForegroundColor Yellow
Write-Host "=============================" -ForegroundColor Yellow

# Get all accounts
$accountsResult = aws organizations list-accounts --output json 2>$null
if (-not $accountsResult) {
    Write-Host "ERROR: Cannot list accounts" -ForegroundColor Red
    exit 1
}

$allAccounts = $accountsResult | ConvertFrom-Json
$suspendedAccounts = $allAccounts.Accounts | Where-Object { $_.Id -ne $AccountId -and $_.Status -eq "SUSPENDED" }

if (-not $suspendedAccounts -or $suspendedAccounts.Count -eq 0) {
    Write-Host "No suspended accounts found" -ForegroundColor Green
    exit 0
}

Write-Host "Found $($suspendedAccounts.Count) suspended accounts:" -ForegroundColor Cyan
foreach ($account in $suspendedAccounts) {
    Write-Host "  - $($account.Name) ($($account.Id))" -ForegroundColor White
}

Write-Host ""
Write-Host "Removing suspended accounts from organization..." -ForegroundColor Yellow

# Remove each suspended account
foreach ($account in $suspendedAccounts) {
    Write-Host "Removing: $($account.Name) ($($account.Id))" -ForegroundColor Yellow
    $result = aws organizations remove-account-from-organization --account-id $account.Id 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  SUCCESS: Account removed" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: $result" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Suspended account removal completed!" -ForegroundColor Green