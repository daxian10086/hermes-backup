#!/bin/bash

# Termux Android APK 构建脚本
# 用于在 Android 设备上使用 Termux 构建 APK

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在 Termux 中
if [ ! -d "/data/data/com.termux" ]; then
    log_error "此脚本必须在 Termux 中运行"
    exit 1
fi

log_info "Termux APK 构建环境配置"
echo ""

# 更新包管理器
log_info "更新包管理器..."
pkg update -y
pkg upgrade -y

# 安装基础工具
log_info "安装基础工具..."
pkg install -y wget unzip git

# 安装 Java
log_info "安装 OpenJDK 17..."
pkg install -y openjdk-17

# 验证 Java 安装
java -version
log_success "Java 安装成功"
echo ""

# 安装 Gradle
log_info "安装 Gradle..."
pkg install -y gradle

# 验证 Gradle 安装
gradle --version
log_success "Gradle 安装成功"
echo ""

# 创建 SDK 目录
SDK_DIR="$HOME/android-sdk"
mkdir -p "$SDK_DIR/cmdline-tools/latest"

log_info "下载 Android SDK 命令行工具..."
cd "$HOME"

# 下载命令行工具
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip

log_info "解压命令行工具..."
unzip -q commandlinetools-linux-9477386_latest.zip -d "$SDK_DIR/cmdline-tools/"
mv "$SDK_DIR/cmdline-tools/cmdline-tools"/* "$SDK_DIR/cmdline-tools/latest/"
rm -rf "$SDK_DIR/cmdline-tools/cmdline-tools"
rm commandlinetools-linux-9477386_latest.zip

log_success "命令行工具安装成功"
echo ""

# 配置环境变量
log_info "配置环境变量..."

cat >> ~/.bashrc << 'EOF'

# Android SDK
export ANDROID_HOME=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
EOF

source ~/.bashrc

log_success "环境变量配置完成"
echo ""

# 接受许可
log_info "接受 Android SDK 许可..."
yes | sdkmanager --licenses > /dev/null 2>&1 || true

# 安装必要组件
log_info "安装 Android SDK 组件..."
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

log_success "Android SDK 组件安装完成"
echo ""

# 显示安装信息
log_info "环境信息："
echo "  Java: $(java -version 2>&1 | head -n 1)"
echo "  Gradle: $(gradle --version 2>&1 | head -n 1)"
echo "  Android SDK: $ANDROID_HOME"
echo ""

log_success "Termux 构建环境配置完成！"
echo ""
echo "======================================"
echo "现在可以构建 APK 了："
echo ""
echo "cd 项目路径"
echo "./gradlew assembleDebug   # 构建 Debug"
echo "./gradlew assembleRelease # 构建 Release"
echo ""
echo "或使用构建脚本："
echo "./build-apk.sh 项目路径 release"
echo "======================================"
