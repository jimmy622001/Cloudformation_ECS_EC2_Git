#!/bin/bash

# Script to install sonar-scanner CLI locally
# Usage: ./install-sonar-scanner.sh

echo "🔍 Installing SonarScanner CLI..."

# Create temp directory for scanner
TEMP_DIR="./sonar-scanner-temp"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  SCANNER_FILE_NAME="sonar-scanner-cli-7.0.2.4839-macosx.zip"
  SCANNER_URI="https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-7.0.2.4839-macosx.zip"
  SCANNER_UNZIP_FOLDER="sonar-scanner-7.0.2.4839-macosx"
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win"* ]]; then
  # Windows with Git Bash or similar
  SCANNER_FILE_NAME="sonar-scanner-cli-7.0.2.4839-windows.zip"
  SCANNER_URI="https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-7.0.2.4839-windows.zip"
  SCANNER_UNZIP_FOLDER="sonar-scanner-7.0.2.4839-windows"
else
  # Linux or other
  SCANNER_FILE_NAME="sonar-scanner-cli-7.0.2.4839-linux-x64.zip"
  SCANNER_URI="https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-7.0.2.4839-linux-x64.zip"
  SCANNER_UNZIP_FOLDER="sonar-scanner-7.0.2.4839-linux-x64"
fi

# Download scanner
echo "Downloading $SCANNER_URI..."
if command -v curl &> /dev/null; then
  curl -L -o "$SCANNER_FILE_NAME" "$SCANNER_URI"
elif command -v wget &> /dev/null; then
  wget -q -O "$SCANNER_FILE_NAME" "$SCANNER_URI"
else
  echo "Neither curl nor wget found. Cannot download sonar-scanner."
  exit 1
fi

# Unzip scanner
echo "Extracting scanner..."
if command -v unzip &> /dev/null; then
  unzip -q -o "$SCANNER_FILE_NAME"
else
  echo "Unzip command not found. Please extract $SCANNER_FILE_NAME manually."
  exit 1
fi

# Create path setup scripts
cd ..
SCRIPT_DIR="$(pwd)"

if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win"* ]]; then
  SONAR_SCANNER="${SCRIPT_DIR}/${TEMP_DIR}/$SCANNER_UNZIP_FOLDER/bin/sonar-scanner.bat"
  
  # Create a Windows script to add scanner to PATH
  echo "@echo off" > set-sonar-path.bat
  echo "set PATH=%PATH%;${SCRIPT_DIR}\\${TEMP_DIR}\\${SCANNER_UNZIP_FOLDER}\\bin" >> set-sonar-path.bat
  echo "echo SonarScanner CLI added to PATH" >> set-sonar-path.bat
  echo "sonar-scanner --version" >> set-sonar-path.bat

  echo -e "\n✅ SonarScanner CLI installed!"
  echo -e "To use it, run: set-sonar-path.bat"
  echo -e "Then you can run: sonar-scanner"
else
  SONAR_SCANNER="${SCRIPT_DIR}/${TEMP_DIR}/$SCANNER_UNZIP_FOLDER/bin/sonar-scanner"
  chmod +x "$SONAR_SCANNER"
  
  # Create a bash script to add scanner to PATH
  echo "#!/bin/bash" > set-sonar-path.sh
  echo "export PATH=\$PATH:${SCRIPT_DIR}/${TEMP_DIR}/${SCANNER_UNZIP_FOLDER}/bin" >> set-sonar-path.sh
  echo "echo SonarScanner CLI added to PATH" >> set-sonar-path.sh
  echo "sonar-scanner --version" >> set-sonar-path.sh
  chmod +x set-sonar-path.sh

  echo -e "\n✅ SonarScanner CLI installed!"
  echo -e "To use it, run: source ./set-sonar-path.sh"
  echo -e "Then you can run: sonar-scanner"
fi

# Create a Windows batch file for direct execution
echo "@echo off" > run-sonar-analysis.bat
echo "call ${SCRIPT_DIR}\\${TEMP_DIR}\\${SCANNER_UNZIP_FOLDER}\\bin\\sonar-scanner.bat %*" >> run-sonar-analysis.bat

# Create a bash script for direct execution
echo "#!/bin/bash" > run-sonar-analysis.sh
echo "\"${SCRIPT_DIR}/${TEMP_DIR}/${SCANNER_UNZIP_FOLDER}/bin/sonar-scanner\" \"\$@\"" >> run-sonar-analysis.sh
chmod +x run-sonar-analysis.sh

echo -e "\nYou can also use the following to run SonarScanner directly:"
echo "- Windows: run-sonar-analysis.bat"
echo "- Unix/Mac/Git Bash: ./run-sonar-analysis.sh"