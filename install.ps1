$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m pip install .
        if ($LASTEXITCODE -ne 0) { throw 'Package installation failed.' }
        & py -3 -m betterway install
        if ($LASTEXITCODE -ne 0) { throw 'Rule installation failed.' }
    } else {
        & python -m pip install .
        if ($LASTEXITCODE -ne 0) { throw 'Package installation failed.' }
        & python -m betterway install
        if ($LASTEXITCODE -ne 0) { throw 'Rule installation failed.' }
    }
    Write-Host 'Ready. Open run-ui.cmd to use the switch.'
} finally {
    Pop-Location
}
