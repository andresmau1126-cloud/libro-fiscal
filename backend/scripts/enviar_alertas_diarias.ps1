$ErrorActionPreference = "Stop"

$backendPath = "C:\Users\MAURICIO\Desktop\libro fiscal\libro fiscal\libro_fiscal_v2\backend"
$pythonExe = "C:\Users\MAURICIO\Desktop\libro fiscal\libro fiscal\libro_fiscal_v2\.venv\Scripts\python.exe"

Set-Location $backendPath

# Envio diario solo por correo (WhatsApp se activara cuando haya API key valida).
& $pythonExe "manage.py" "enviar_alertas_correo"
