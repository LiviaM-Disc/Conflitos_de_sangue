param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$output = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $output -Force | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    foreach ($name in @('Manual_do_Jogador', 'Guia_de_Respostas')) {
        $source = Join-Path $PSScriptRoot ($name + '.docx')
        $document = $word.Documents.Open($source, $false, $true)
        try {
            $document.ExportAsFixedFormat((Join-Path $output ($name + '.pdf')), 17)
            Write-Output ($name + ': ' + $document.ComputeStatistics(2) + ' paginas')
        } finally {
            $document.Close(0)
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
        }
    }
} finally {
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}
