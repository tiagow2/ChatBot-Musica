<#
install_ffmpeg.ps1

Baixa um build estático do ffmpeg (Gyan) para a pasta ./ffmpeg no repositório,
extrai e adiciona temporariamente o bin ao PATH desta sessão do PowerShell.

Uso:
  .\install_ffmpeg.ps1        # pergunta confirmação e baixa

Observação: o PATH só é atualizado para a sessão atual do PowerShell. Para tornar
permanente, adicione manualmente o caminho mostrado em "Passo final" às Variáveis de
Ambiente do Windows.
#>

Write-Host "== install_ffmpeg.ps1 =="

$dest = Join-Path -Path $PSScriptRoot -ChildPath "ffmpeg"
$zipFile = Join-Path -Path $PSScriptRoot -ChildPath "ffmpeg-release.zip"
$zipUrl = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'

if (-Not (Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
}

Write-Host "Baixando ffmpeg de: $zipUrl"
try {
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Error "Falha ao baixar o arquivo: $_"
    exit 1
}

Write-Host "Extraindo..."
try {
    Expand-Archive -LiteralPath $zipFile -DestinationPath $dest -Force
} catch {
    Write-Error "Falha ao extrair: $_"
    exit 1
}

# encontra a subpasta extraída que contém bin\
$sub = Get-ChildItem -Directory -Path $dest | Select-Object -First 1
if (-not $sub) {
    Write-Error "Não encontrei a pasta extraída dentro de $dest"
    exit 1
}
$ffbin = Join-Path -Path $sub.FullName -ChildPath 'bin'

# adicionar temporariamente ao PATH desta sessão
$env:Path = "$env:Path;$ffbin"

Write-Host "ffmpeg extraído em: $($sub.FullName)"
Write-Host "Bin adicionado ao PATH da sessão atual: $ffbin"

Write-Host "Testando ffmpeg..."
try {
    & ffmpeg -version
} catch {
    Write-Warning "Não foi possível invocar 'ffmpeg' automaticamente. Verifique se o PATH foi atualizado na sessão atual."
}

Write-Host "\nPasso final (opcional): para tornar o ffmpeg disponível permanentemente no sistema, adicione o caminho abaixo às Variáveis de Ambiente -> Path do Windows:\n"
Write-Host $ffbin
Write-Host "\nSe preferir, mova a pasta extraída para um local permanente (ex: C:\\tools\\ffmpeg) e adicione o bin ao Path via Painel de Controle."

# não remove o zip para que o usuário possa inspecionar, mas podemos limpar se desejar
# Remove-Item -Path $zipFile -Force

Write-Host "Concluído. Agora rode 'ffmpeg -version' para confirmar (feche/reabra o terminal se atualizou PATH permanentemente)."