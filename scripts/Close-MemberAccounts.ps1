param([string]$AccountId = "667021093945")

Write-Host "AWS Organization Member Account Closure" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow

# Get member accounts
$accountsResult = aws organizations list-accounts --output json 2>$null
if (-not $accountsResult) {
    Write-Host "ERROR: Cannot list accounts" -ForegroundColor Red
    exit 1
}

$allAccounts = $accountsResult | ConvertFrom-Json
$memberAccounts = $allAccounts.Accounts | Where-Object { $_.Id -ne $AccountId -and $_.Status -eq "ACTIVE" }

if (-not $memberAccounts -or $memberAccounts.Count -eq 0) {
    Write-Host "No active member accounts found" -ForegroundColor Green
    exit 0
}

Write-Host "Found $($memberAccounts.Count) active member accounts:" -ForegroundColor Cyan
foreach ($account in $memberAccounts) {
    Write-Host "  - $($account.Name) ($($account.Id))" -ForegroundColor White
}

Write-Host ""
Write-Host "WARNING: This will CLOSE (permanently delete) all member accounts" -ForegroundColor Red
Write-Host "All data and resources in these accounts will be LOST" -ForegroundColor Red
Write-Host "This action cannot be undone" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Type 'CLOSE' to confirm account closure"
if ($confirm -ne "CLOSE") {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 1
}

# Close each member account
foreach ($account in $memberAccounts) {
    Write-Host "Closing account: $($account.Name) ($($account.Id))" -ForegroundColor Yellow
    $result = aws organizations close-account --account-id $account.Id 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  SUCCESS: Account closure initiated" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: $result" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Account closure process initiated!" -ForegroundColor Green
Write-Host "Note: Account closure may take up to 90 days to complete." -ForegroundColor Yellow