# autorunner.ps1
$ErrorActionPreference = "Stop"

$VenvDir = "encryption_venv"
$ReqFile = "requirements.txt"
$ReqMarker = "$VenvDir\.requirements_installed"
$DotKeysDir = "DOTkeys"
$KeysDir = ".keys"

# Move DOTkeys/ to .keys/ if .keys/ doesn't already exist
if (Test-Path $DotKeysDir -and -not (Test-Path $KeysDir)) {
    Write-Host "Renaming $DotKeysDir to $KeysDir..."
    Rename-Item -Path $DotKeysDir -NewName $KeysDir
} elseif (Test-Path $KeysDir) {
    Write-Host "$KeysDir already exists, skipping DOTkeys rename."
}

# Check if virtual environment exists
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment in $VenvDir..."
    python -m venv $VenvDir
}

# Activate the virtual environment
$VenvActivate = Join-Path $VenvDir "Scripts\Activate.ps1"
if (-not (Test-Path $VenvActivate)) {
    Write-Error "Failed to find venv activation script at $VenvActivate"
    exit 1
}
# Dot-source to activate the venv in current session
. $VenvActivate

# Optional: upgrade pip
# python -m pip install --upgrade pip

# Install requirements if not already installed
if (-not (Test-Path $ReqMarker)) {
    Write-Host "Installing requirements from $ReqFile..."
    pip install -r $ReqFile
    # Create marker file
    New-Item -ItemType File -Path $ReqMarker -Force | Out-Null
} else {
    Write-Host "Requirements already installed, skipping..."
}

# Run the main script
python src\main.py
