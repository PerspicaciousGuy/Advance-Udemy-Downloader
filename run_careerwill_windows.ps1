<#
.SYNOPSIS
  Windows PowerShell runner for Careerwill downloader.

.DESCRIPTION
  Installs optional dependencies, extracts JWT from a Netscape `cookies.txt`, and runs
  `careerwill.py` to list or download enrolled courses or a single course.

.PARAMETER ListEnrolled
  Lists enrolled courses for the authenticated user.

.PARAMETER DownloadEnrolled
  Downloads all discovered enrolled courses.

.PARAMETER CourseUrl
  Download a single course by URL.

.PARAMETER BearerToken
  Optional explicit bearer (JWT) token. If not provided, the script will try to read
  the token from `cookies.txt` in the current directory (cookie name: token).

.PARAMETER OutDir
  Output directory for downloads. Default: .\careerwill_out

.PARAMETER InstallDeps
  If set, installs Python dependencies from `requirements.txt` and `yt-dlp`.

Examples:
  .\run_careerwill_windows.ps1 -ListEnrolled -BearerToken "<JWT>"
  .\run_careerwill_windows.ps1 -DownloadEnrolled -InstallDeps
  .\run_careerwill_windows.ps1 -CourseUrl "https://web.careerwill.com/..." -OutDir C:\Downloads
#>

[CmdletBinding()]
param(
    [switch]$ListEnrolled,
    [switch]$DownloadEnrolled,
    [string]$CourseUrl,
    [string]$BearerToken,
    [string]$OutDir = "$PWD\careerwill_out",
    [switch]$InstallDeps
)

Set-StrictMode -Version Latest

# Move to script directory (assumes script lives at repo root)
Set-Location -Path $PSScriptRoot

function Get-TokenFromCookies {
    param([string]$CookieFile = "$PSScriptRoot\cookies.txt")
    if (-Not (Test-Path $CookieFile)) { return $null }
    try {
        $lines = Get-Content -Raw -Path $CookieFile -ErrorAction Stop -Encoding UTF8
        foreach ($line in $lines -split "\r?\n") {
            if ($line.StartsWith('#') -or [string]::IsNullOrWhiteSpace($line)) { continue }
            $parts = $line -split "\t"
            if ($parts.Length -ge 7 -and $parts[5] -eq 'token') {
                return $parts[6].Trim()
            }
        }
    } catch {
        Write-Warning "Failed to read cookies file: $_"
    }
    return $null
}

if ($InstallDeps) {
    Write-Host "Installing Python dependencies..."
    python -m pip install --upgrade pip
    if (Test-Path requirements.txt) { python -m pip install -r requirements.txt }
    python -m pip install yt-dlp
}

if (-not $BearerToken) {
    $BearerToken = Get-TokenFromCookies
    if ($BearerToken) { Write-Host "Extracted bearer token from cookies.txt" }
}

if (-not $BearerToken) {
    Write-Warning "No bearer token provided and none found in cookies.txt. Authenticated operations will fail.";
}

$python = "python"

if ($ListEnrolled) {
    $cmd = @($python, 'careerwill.py', '--list-enrolled')
    if ($BearerToken) { $cmd += @('-b', $BearerToken) }
    Write-Host "Running: $($cmd -join ' ')"
    & $cmd
    exit $LASTEXITCODE
}

if ($DownloadEnrolled) {
    $cmd = @($python, 'careerwill.py', '--download-enrolled', '-o', $OutDir)
    if ($BearerToken) { $cmd += @('-b', $BearerToken) }
    Write-Host "Running: $($cmd -join ' ')"
    & $cmd
    exit $LASTEXITCODE
}

if ($CourseUrl) {
    $cmd = @($python, 'careerwill.py', '-c', $CourseUrl, '-o', $OutDir)
    if ($BearerToken) { $cmd += @('-b', $BearerToken) }
    Write-Host "Running: $($cmd -join ' ')"
    & $cmd
    exit $LASTEXITCODE
}

Write-Host "No action specified. Use -ListEnrolled, -DownloadEnrolled, or -CourseUrl. Use -InstallDeps to install requirements." -ForegroundColor Yellow
