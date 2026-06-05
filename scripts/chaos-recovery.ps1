param(
    [string]$BaseUrl = "http://127.0.0.1:18080",
    [string]$Namespace = "meshmart",
    [string]$EvidenceDir = "evidence"
)

$ErrorActionPreference = "Stop"

function Invoke-PlatformOrder {
    $payload = @{
        user_id = "chaos-user-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
        product_id = "PROD-001"
        quantity = 1
        payment_mode = "success"
    } | ConvertTo-Json -Compress

    Invoke-RestMethod -Method Post -Uri "$BaseUrl/orders" -ContentType "application/json" -Body $payload -TimeoutSec 30
}

New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null

Write-Host "1. Baseline order before chaos"
$before = Invoke-PlatformOrder
Write-Host "   OK order=$($before.order_id) status=$($before.order_status)"

Write-Host "2. Delete one payment-service pod"
$pod = kubectl get pod -n $Namespace -l app=payment-service -o jsonpath="{.items[0].metadata.name}"
if (-not $pod) {
    throw "No payment-service pod found"
}
kubectl delete pod -n $Namespace $pod | Out-Host

Write-Host "3. Wait for Deployment recovery"
kubectl rollout status -n $Namespace deployment/payment-service --timeout=300s | Out-Host
$paymentPods = kubectl get pods -n $Namespace -l app=payment-service --no-headers

Write-Host "4. Order after recovery"
$after = Invoke-PlatformOrder
Write-Host "   OK order=$($after.order_id) status=$($after.order_status)"

$evidence = [ordered]@{
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    deleted_pod = $pod
    before_order_status = $before.order_status
    after_order_status = $after.order_status
    payment_pods_after_recovery = $paymentPods
}

$path = Join-Path $EvidenceDir "chaos-evidence-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$evidence | ConvertTo-Json -Depth 10 | Set-Content -Path $path -Encoding UTF8
Write-Host "Evidence written to $path"
