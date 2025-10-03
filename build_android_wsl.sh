#!/bin/bash
# Script per build Android APK usando WSL2 su Windows
# Eseguire questo script da WSL2 Ubuntu

set -e  # Exit on any error

echo "🚀 MONUMENT RECOGNIZER - Android Build per WSL2"
echo "================================================"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se stiamo eseguendo in WSL2
if [[ ! -f /proc/version ]] || ! grep -q "Microsoft\|WSL" /proc/version; then
    print_error "Questo script deve essere eseguito in WSL2!"
    exit 1
fi

print_success "WSL2 detected - proceeding with setup"

# Step 1: Update sistema e installa dipendenze
print_step "1/8 - Aggiornamento sistema e installazione dipendenze base"
sudo apt update -qq
sudo apt install -y build-essential git wget unzip curl python3 python3-pip \
    python3-dev python3-venv zlib1g-dev libffi-dev libssl-dev \
    libncurses5-dev libncursesw5-dev cmake openjdk-17-jdk

# Step 2: Setup Python
print_step "2/8 - Setup ambiente Python"
python3 -m pip install --upgrade pip setuptools wheel
pip3 install buildozer cython==0.29.33

print_success "Python environment configured"

# Step 3: Setup Android SDK
print_step "3/8 - Setup Android SDK"
export ANDROID_HOME=$HOME/android-sdk
mkdir -p $ANDROID_HOME

# Download Android SDK command line tools
print_step "Downloading Android SDK command line tools..."
cd /tmp
wget -q https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip -O cmdtools.zip
unzip -q cmdtools.zip
mv cmdline-tools $ANDROID_HOME/cmdline-tools-temp
mkdir -p $ANDROID_HOME/cmdline-tools/latest
mv $ANDROID_HOME/cmdline-tools-temp/* $ANDROID_HOME/cmdline-tools/latest/
rmdir $ANDROID_HOME/cmdline-tools-temp
rm cmdtools.zip

# Setup PATH
export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

print_success "Android SDK command line tools installed"

# Step 4: Accept licenses and install SDK components
print_step "4/8 - Accept Android licenses and install SDK components"
yes | sdkmanager --licenses >/dev/null 2>&1 || true
sdkmanager "platform-tools" "platforms;android-31" "build-tools;31.0.0"

print_success "Android SDK components installed"

# Step 5: Install Android NDK 25b
print_step "5/8 - Installing Android NDK 25b"
cd /tmp
wget -q https://dl.google.com/android/repository/android-ndk-r25b-linux.zip -O ndk25.zip
unzip -q ndk25.zip
mv android-ndk-r25b $ANDROID_HOME/ndk-r25b
rm ndk25.zip

export ANDROID_NDK_ROOT=$ANDROID_HOME/ndk-r25b

print_success "Android NDK 25b installed"

# Step 6: Crea environment script per riuso futuro
print_step "6/8 - Creating environment setup script"
cat > $HOME/android-env.sh << 'EOF'
#!/bin/bash
# Android environment variables
export ANDROID_HOME=$HOME/android-sdk
export ANDROID_SDK_ROOT=$HOME/android-sdk
export ANDROID_NDK_ROOT=$HOME/android-sdk/ndk-r25b
export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

export ANDROIDSDK=$ANDROID_HOME
export ANDROIDNDK=$ANDROID_NDK_ROOT
export ANDROIDAPI="31"
export NDKAPI="21"

echo "Android environment loaded:"
echo "  ANDROID_HOME: $ANDROID_HOME"
echo "  ANDROID_NDK_ROOT: $ANDROID_NDK_ROOT"
EOF

chmod +x $HOME/android-env.sh
source $HOME/android-env.sh

print_success "Environment setup script created at $HOME/android-env.sh"

# Step 7: Naviga alla directory del progetto (assumendo che sia montata in WSL)
print_step "7/8 - Navigating to project directory"

# Trova la directory del progetto - potrebbe essere in /mnt/c/ se montata da Windows
if [ -d "/mnt/c/Users/$USER/MonumentRecognizer" ]; then
    PROJECT_DIR="/mnt/c/Users/$USER/MonumentRecognizer"
elif [ -d "$HOME/MonumentRecognizer" ]; then
    PROJECT_DIR="$HOME/MonumentRecognizer"
elif [ -d "./MonumentRecognizer" ]; then
    PROJECT_DIR="./MonumentRecognizer"
else
    print_warning "Project directory not found. Please navigate to your project directory and run buildozer manually."
    print_warning "Use these commands:"
    echo "  source $HOME/android-env.sh"
    echo "  buildozer android debug"
    exit 0
fi

cd "$PROJECT_DIR"
print_success "Found project directory: $PROJECT_DIR"

# Step 8: Install app requirements and build
print_step "8/8 - Installing app requirements and building APK"

# Install app requirements if available
if [ -f "requirements.txt" ]; then
    print_step "Installing app requirements..."
    pip3 install -r requirements.txt
fi

# Verifica buildozer.spec
if [ ! -f "buildozer.spec" ]; then
    print_error "buildozer.spec not found! Run 'buildozer init' first."
    exit 1
fi

# Backup original buildozer.spec
cp buildozer.spec buildozer.spec.backup

# Aggiorna buildozer.spec per WSL
print_step "Updating buildozer.spec for WSL environment..."
sed -i 's|^android\.ndk.*=.*|android.ndk = 25b|g' buildozer.spec
sed -i 's|^android\.api.*=.*|android.api = 31|g' buildozer.spec
sed -i 's|^android\.minapi.*=.*|android.minapi = 21|g' buildozer.spec
sed -i 's|^android\.sdk.*=.*|android.sdk = 31|g' buildozer.spec

# Aggiungi configurazioni specifiche per WSL
echo "" >> buildozer.spec
echo "# WSL specific paths" >> buildozer.spec
echo "android.ndk_path = $ANDROID_NDK_ROOT" >> buildozer.spec
echo "android.sdk_path = $ANDROID_HOME" >> buildozer.spec
echo "android.skip_update = True" >> buildozer.spec

print_success "buildozer.spec updated for WSL"

# Build APK
print_step "Starting APK build..."
echo "This may take 10-30 minutes for the first build..."

if buildozer android debug --verbose; then
    print_success "🎉 BUILD SUCCESS!"
    
    # Find and display APK info
    if [ -d "bin" ] && ls bin/*.apk >/dev/null 2>&1; then
        echo ""
        echo "Generated APK files:"
        ls -la bin/*.apk
        
        # Get APK info
        for apk in bin/*.apk; do
            echo ""
            print_success "APK: $apk"
            echo "  Size: $(du -h "$apk" | cut -f1)"
            echo "  Type: $(file "$apk")"
        done
        
        echo ""
        print_success "APK build completed successfully!"
        print_success "Your APK is ready in the bin/ directory"
    else
        print_warning "APK files not found in bin/ directory"
    fi
    
else
    print_error "Build failed!"
    echo ""
    echo "To retry the build:"
    echo "  1. source $HOME/android-env.sh"
    echo "  2. cd '$PROJECT_DIR'"
    echo "  3. buildozer android debug"
    exit 1
fi

# Cleanup instructions
echo ""
echo "🔧 Future builds:"
echo "  source $HOME/android-env.sh"
echo "  cd '$PROJECT_DIR'"
echo "  buildozer android debug"
echo ""
print_success "Setup complete! Android development environment ready in WSL2"