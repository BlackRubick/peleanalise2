Write-Host ""
Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       PeleAnálise — Dev Server       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── 1. .env ────────────────────────────────────────────────────────────────────
if (-not (Test-Path ".env")) {
    Write-Host "⚙  .env no encontrado → creando desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓  .env creado. Edítalo con tus credenciales antes de continuar." -ForegroundColor Green
    Read-Host "   Presiona Enter cuando hayas configurado el .env"
}

# Cargar variables del .env
Get-Content ".env" | Where-Object { $_ -match "^\s*[^#]" -and $_ -match "=" } | ForEach-Object {
    $parts = $_ -split "=", 2
    $key   = $parts[0].Trim()
    $value = $parts[1].Trim().Trim('"')
    [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
}
Write-Host "✓  .env cargado" -ForegroundColor Green

# ── 2. Dependencias Node ───────────────────────────────────────────────────────
Write-Host ""
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias Node..." -ForegroundColor Yellow
    npm install
    Write-Host "✓  Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "✓  node_modules OK" -ForegroundColor Green
}

# ── 3. Prisma ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "🗄  Sincronizando tablas (Prisma db push)..." -ForegroundColor Yellow
npx prisma db push --accept-data-loss
Write-Host "✓  Tablas sincronizadas" -ForegroundColor Green

# ── 4. Seed ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "🌱 Verificando seed..." -ForegroundColor Yellow
npx tsx prisma/seed.ts
Write-Host "✓  Seed OK" -ForegroundColor Green

# ── 5. Python venv ────────────────────────────────────────────────────────────
Write-Host ""
$venvDir = "..\python-ai\venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "🐍 Creando entorno virtual Python..." -ForegroundColor Yellow
    python -m venv $venvDir
    Write-Host "✓  Entorno virtual creado" -ForegroundColor Green
}

$pipExe    = "$venvDir\Scripts\pip.exe"
$pythonExe = "$venvDir\Scripts\python.exe"

if (-not (& $pythonExe -c "import uvicorn" 2>$null; $LASTEXITCODE -eq 0)) {
    Write-Host "🐍 Instalando dependencias Python..." -ForegroundColor Yellow
    & $pipExe install --upgrade pip --quiet
    & $pipExe install -r ..\python-ai\requirements.txt
    Write-Host "✓  Dependencias Python instaladas" -ForegroundColor Green
} else {
    Write-Host "✓  Dependencias Python OK" -ForegroundColor Green
}

# ── 6. Arrancar servidores ────────────────────────────────────────────────────
Write-Host ""
Write-Host "🚀 Iniciando servidores..." -ForegroundColor Green
Write-Host "   Nuxt   → http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Python → http://localhost:8000" -ForegroundColor Magenta
Write-Host ""

npx concurrently `
    -n "nuxt,python" `
    -c "cyan,magenta" `
    --kill-others-on-fail `
    "nuxt dev" `
    "..\python-ai\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000 --app-dir ..\python-ai"
