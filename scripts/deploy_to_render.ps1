param(
    [string]$RemoteUrl
)

# Comprueba que estamos en un repositorio git
if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    Write-Error "No parece ser un repositorio git. Ejecuta 'git init' primero."
    exit 1
}

# Si no se pasa RemoteUrl, intenta usar origin existente
if (-not $RemoteUrl) {
    $existing = git remote get-url origin 2>$null
    if ($existing) { $RemoteUrl = $existing }
}

if (-not $RemoteUrl) {
    Write-Host "No se encontró remoto 'origin'. Pasa la URL como argumento: .\deploy_to_render.ps1 -RemoteUrl 'https://github.com/usuario/repo.git'"
    exit 1
}

# Asegura rama main
$branch = git rev-parse --abbrev-ref HEAD
if ($branch -ne 'main') {
    Write-Host "Cambiando a rama 'main' (se creará si no existe)"
    git checkout -b main
}

# Añadir y commitear
git add .
$commit = git commit -m "Preparar despliegue en Render" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "No hay cambios para commitear o el commit falló."
}

# Añadir remoto si no existe
$hasOrigin = git remote | Select-String -Pattern '^origin$' -Quiet
if (-not $hasOrigin) {
    Write-Host "Añadiendo remoto origin -> $RemoteUrl"
    git remote add origin $RemoteUrl
}

# Push
Write-Host "Haciendo push a origin main..."
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error haciendo push. Revisa tus credenciales o la URL remota."
    exit 1
}

Write-Host "Push completado."
Write-Host "Sigue estos pasos en Render:"
Write-Host "1) Abre https://dashboard.render.com -> New -> Web Service -> Connect a repository"
Write-Host "2) Selecciona tu repo y la rama 'main'"
Write-Host "3) Render detectará 'render.yaml' y creará la DB PostgreSQL automáticamente"
Write-Host "Variables que debes añadir en Settings -> Environment (si no están ya):"
Write-Host "  DEBUG=false"
Write-Host "  SECRET_KEY=<genera con: python -c \"import secrets; print(secrets.token_urlsafe(50))\">"
Write-Host "  DJANGO_SETTINGS_MODULE=config.settings"
Write-Host "  ALLOWED_HOSTS=*"
Write-Host "Cuando el deploy termine, revisa Logs -> Events para verificar migraciones y build."
