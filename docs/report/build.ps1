param([string]$Engine = 'pdflatex')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'source/first-three-pages.pdf'))) {
    throw 'The original first three pages are missing. Export and prepare them before the final build.'
}
Push-Location $PSScriptRoot
try {
    if ($Engine -eq 'tectonic') {
        & tectonic --keep-logs main.tex
        if ($LASTEXITCODE -ne 0) { throw 'LaTeX compilation failed.' }
    } else {
        for ($pass = 1; $pass -le 3; $pass++) {
            & $Engine -interaction=nonstopmode -halt-on-error main.tex
            if ($LASTEXITCODE -ne 0) { throw "LaTeX pass $pass failed." }
        }
    }
    $destination = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../output/pdf'))
    New-Item -ItemType Directory -Force $destination | Out-Null
    Copy-Item -LiteralPath 'main.pdf' -Destination (Join-Path $destination 'NEXOS_Professional_Project_Report.pdf')
} finally { Pop-Location }
