param([string]$SourceDocx = (Join-Path $PSScriptRoot 'source/original-report.docx'))
$ErrorActionPreference = 'Stop'
$sourceFull = (Resolve-Path -LiteralPath $SourceDocx).Path
$destination = Join-Path $PSScriptRoot 'source/original-report.pdf'
$wordExport = New-Object -ComObject Word.Application
$wordExport.Visible = $false
$wordExport.DisplayAlerts = 0
$wordExport.AutomationSecurity = 3
try {
    $wordExport.Options.UpdateLinksAtOpen = $false
    $docExport = $wordExport.Documents.Open($sourceFull, $false, $true, $false)
    try { $docExport.ExportAsFixedFormat($destination, 17) }
    finally { $docExport.Close(0) }
} finally { $wordExport.Quit() }
Write-Output "Exported original report without saving changes: $destination"
Write-Output 'Run prepare_front_pages.py next, then compile main.tex.'
