$ErrorActionPreference = 'Stop'
$studioRoot = Split-Path -Parent $PSScriptRoot
$blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'

if (-not (Test-Path -LiteralPath $blender)) {
    $found = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($found) {
        $blender = $found.Source
    } else {
        throw 'Blender tidak ditemukan. Pastikan Blender terpasang di sistem.'
    }
}

$template = Join-Path $studioRoot '01_STUDIO\Studio_Lifestyle.blend'
$startup = Join-Path $PSScriptRoot 'mulai_sesi.py'

if (-not (Test-Path -LiteralPath $template)) {
    throw "Template studio tidak ditemukan di: $template"
}

Start-Process -FilePath $blender -ArgumentList @(('"' + $template + '"'), '--window-maximized', '--python', ('"' + $startup + '"')) -WindowStyle Normal
