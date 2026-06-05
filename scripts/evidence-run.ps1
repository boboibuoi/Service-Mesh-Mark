param(
    [string]$BaseUrl = "http://127.0.0.1:18080",
    [string]$Namespace = "meshmart",
    [string]$EvidenceDir = "evidence",
    [switch]$RunLoadTest,
    [switch]$RunScalingScenario
)

$ErrorActionPreference = "Stop"

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-Order {
    param(
        [string]$ProductId,
        [string]$PaymentMode,
        [string]$IdempotencyKey,
        [string]$UserId
    )

    $payload = @{
        user_id = if ($UserId) { $UserId } else { "customer-001-$([guid]::NewGuid().ToString('N').Substring(0, 8))" }
        product_id = $ProductId
        quantity = 1
        payment_mode = $PaymentMode
    } | ConvertTo-Json -Compress

    $headers = @{}
    if ($IdempotencyKey) {
        $headers["Idempotency-Key"] = $IdempotencyKey
    }

    Invoke-RestMethod -Method Post -Uri "$BaseUrl/orders" -ContentType "application/json" -Headers $headers -Body $payload -TimeoutSec 30
}

function Get-HttpStatus {
    param([string]$Url)
    curl.exe -sS -o NUL -w "%{http_code}" $Url
}

function Start-KindGatewayForward {
    if (-not (Test-Command "kubectl")) {
        throw "kubectl is required for load/scaling scenario port-forward"
    }

    $listener = Get-NetTCPConnection -LocalPort 18081 -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        return
    }

    $tmp = Join-Path (Get-Location) ".tmp-kind"
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    $out = Join-Path $tmp "platform-ingress-18081.out.log"
    $err = Join-Path $tmp "platform-ingress-18081.err.log"
    Start-Process -FilePath "kubectl" -ArgumentList @(
        "port-forward",
        "--address",
        "0.0.0.0",
        "-n",
        "istio-system",
        "svc/istio-ingressgateway",
        "18081:80"
    ) -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err | Out-Null
    Start-Sleep -Seconds 4
}

function Invoke-K6 {
    param([string]$Name)

    if (-not (Test-Command "docker")) {
        throw "docker is required to run k6 through grafana/k6"
    }

    Start-KindGatewayForward

    $summaryPath = Join-Path $EvidenceDir "$Name.json"
    if (Test-Path $summaryPath) {
        Remove-Item -LiteralPath $summaryPath -Force
    }

    docker run --rm `
        -e BASE_URL="http://host.docker.internal:18081" `
        -e VUS=10 `
        -e DURATION=10s `
        --mount "type=bind,source=$((Get-Location).Path),target=/scripts" `
        grafana/k6:latest run `
        --summary-export "/scripts/$EvidenceDir/$Name.json" `
        /scripts/load-test.js | Out-Host

    $summary = Get-Content -Raw $summaryPath | ConvertFrom-Json
    $metrics = $summary.metrics
    $duration = $metrics.http_req_duration
    return [ordered]@{
        http_reqs = $metrics.http_reqs.count
        failed_rate = $metrics.http_req_failed.value
        avg_ms = [math]::Round($duration.avg, 2)
        p95_ms = [math]::Round($duration.'p(95)', 2)
    }
}

New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null

Write-Host "1. Products"
$productsResponse = Invoke-RestMethod -Method Get -Uri "$BaseUrl/products" -TimeoutSec 20
$product = $productsResponse.products[0]
Write-Host "   OK product=$($product.id) $($product.name)"

Write-Host "2. Normal order"
$normalOrder = Invoke-Order -ProductId $product.id -PaymentMode "success"
Write-Host "   OK order=$($normalOrder.order_id) status=$($normalOrder.order_status)"

Write-Host "3. Payment failure order"
$failedOrder = Invoke-Order -ProductId $product.id -PaymentMode "failed"
Write-Host "   OK order=$($failedOrder.order_id) status=$($failedOrder.order_status)"

Write-Host "4. Idempotency retry"
$idempotencyKey = "order-$([guid]::NewGuid().ToString('N'))"
$idempotencyUserId = "idempotent-user-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
$idempotentOrderFirst = Invoke-Order -ProductId $product.id -PaymentMode "success" -IdempotencyKey $idempotencyKey -UserId $idempotencyUserId
$idempotentOrderSecond = Invoke-Order -ProductId $product.id -PaymentMode "success" -IdempotencyKey $idempotencyKey -UserId $idempotencyUserId
if ($idempotentOrderFirst.order_id -ne $idempotentOrderSecond.order_id) {
    throw "Idempotency failed: first=$($idempotentOrderFirst.order_id), second=$($idempotentOrderSecond.order_id)"
}
Write-Host "   OK key=$idempotencyKey order=$($idempotentOrderFirst.order_id)"

Write-Host "5. Payment timeout scenario"
$slowStatus = Get-HttpStatus "$BaseUrl/payment?mode=slow"
Write-Host "   OK /payment?mode=slow returned HTTP $slowStatus"

$observability = [ordered]@{}
try {
    $prometheus = Invoke-RestMethod -Uri "http://127.0.0.1:19090/api/v1/query?query=istio_requests_total" -TimeoutSec 10
    $observability.prometheus_status = $prometheus.status
    $observability.prometheus_istio_series = $prometheus.data.result.Count
} catch {
    $observability.prometheus_status = "not available"
}

try {
    $jaeger = Invoke-RestMethod -Uri "http://127.0.0.1:16686/jaeger/api/services" -TimeoutSec 10
    $observability.jaeger_service_count = $jaeger.data.Count
    $observability.jaeger_services = $jaeger.data
} catch {
    $observability.jaeger_service_count = 0
}

$kubernetes = [ordered]@{}
if (Test-Command "kubectl") {
    $kubernetes.meshmart_pods = kubectl get pods -n $Namespace --no-headers
    $kubernetes.istio_system_pods = kubectl get pods -n istio-system --no-headers
}

$load = [ordered]@{}
if ($RunLoadTest) {
    Write-Host "6. k6 load test"
    $load.normal = Invoke-K6 -Name "k6-platform"
}

$scaling = [ordered]@{}
if ($RunScalingScenario) {
    if (-not (Test-Command "kubectl")) {
        throw "kubectl is required for scaling scenario"
    }

    Write-Host "7. Scaling scenario"
    kubectl scale -n $Namespace deployment/order-service deployment/product-service deployment/payment-service deployment/notification-service --replicas=1 | Out-Host
    foreach ($deployment in @("order-service", "product-service", "payment-service", "notification-service")) {
        kubectl rollout status -n $Namespace deployment/$deployment --timeout=300s | Out-Host
    }
    $scaling.one_replica = Invoke-K6 -Name "k6-one-replica"

    kubectl scale -n $Namespace deployment/order-service deployment/product-service deployment/payment-service deployment/notification-service --replicas=3 | Out-Host
    foreach ($deployment in @("order-service", "product-service", "payment-service", "notification-service")) {
        kubectl rollout status -n $Namespace deployment/$deployment --timeout=300s | Out-Host
    }
    $scaling.three_replicas = Invoke-K6 -Name "k6-three-replicas"
}

$evidence = [ordered]@{
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    base_url = $BaseUrl
    normal_order = $normalOrder
    failed_order = $failedOrder
    idempotency = [ordered]@{
        key = $idempotencyKey
        first_order_id = $idempotentOrderFirst.order_id
        second_order_id = $idempotentOrderSecond.order_id
        duplicate_prevented = $idempotentOrderFirst.order_id -eq $idempotentOrderSecond.order_id
    }
    slow_payment_http_status = $slowStatus
    observability = $observability
    kubernetes = $kubernetes
    load = $load
    scaling = $scaling
}

$evidencePath = Join-Path $EvidenceDir "evidence-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$evidence | ConvertTo-Json -Depth 20 | Set-Content -Path $evidencePath -Encoding UTF8

Write-Host "Evidence written to $evidencePath"
