#!/bin/bash

# 周易算卦 APK 一键构建脚本
# 支持 Linux/macOS/Windows (WSL)

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

echo "========================================"
echo "周易算卦 APK 一键构建"
echo "========================================"
echo ""

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

log_info "检测到系统: $MACHINE"

# 检查 Java
log_info "检查 Java..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    log_success "Java 已安装: $JAVA_VERSION"
else
    log_error "Java 未安装"
    log_info "请安装 Java 17 或更高版本"
    log_info "下载地址: https://adoptium.net/"
    exit 1
fi

# 检查 Java 版本
JAVA_MAJOR=$(java -version 2>&1 | head -n 1 | sed 's/.*version "\(.*\)".*/\1/' | cut -d'.' -f1)
if [ "$JAVA_MAJOR" -lt 17 ]; then
    log_warn "Java 版本较低，建议使用 Java 17+"
fi

# 检查 Android SDK
log_info "检查 Android SDK..."
if [ -z "$ANDROID_HOME" ]; then
    log_warn "ANDROID_HOME 未配置"

    # 检查常见位置
    POSSIBLE_PATHS=(
        "$HOME/Android/Sdk"
        "$HOME/Library/Android/sdk"
        "/opt/android-sdk"
        "$HOME/.android-sdk"
    )

    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -d "$path" ]; then
            log_success "找到 Android SDK: $path"
            export ANDROID_HOME="$path"
            break
        fi
    done

    if [ -z "$ANDROID_HOME" ]; then
        log_error "找不到 Android SDK"
        log_info "请安装 Android Studio 或配置 ANDROID_HOME 环境变量"
        exit 1
    fi
else
    log_success "ANDROID_HOME 已配置: $ANDROID_HOME"
fi

# 导出环境变量
export ANDROID_HOME
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/cmdline-tools/bin:$ANDROID_HOME/platform-tools"

# 检查 Gradle Wrapper
log_info "检查 Gradle Wrapper..."
if [ -f "gradlew" ]; then
    log_success "Gradle Wrapper 已找到"
    chmod +x gradlew
    GRADLE_CMD="./gradlew"
else
    log_warn "Gradle Wrapper 未找到，尝试创建..."

    # 下载 Gradle
    GRADLE_VERSION="8.5"
    GRADLE_DIR="$HOME/.gradle/wrapper/dists/gradle-$GRADLE_VERSION-bin"
    GRADLE_ZIP="$GRADLE_DIR/gradle-$GRADLE_VERSION-bin.zip"

    if [ ! -d "$GRADLE_DIR/gradle-$GRADLE_VERSION" ]; then
        log_info "下载 Gradle $GRADLE_VERSION..."
        mkdir -p "$GRADLE_DIR"

        if [ ! -f "$GRADLE_ZIP" ]; then
            wget "https://services.gradle.org/distributions/gradle-$GRADLE_VERSION-bin.zip" -O "$GRADLE_ZIP"
        fi

        unzip -q "$GRADLE_ZIP" -d "$GRADLE_DIR"
    fi

    export GRADLE_HOME="$GRADLE_DIR/gradle-$GRADLE_VERSION"
    export PATH="$PATH:$GRADLE_HOME/bin"
    GRADLE_CMD="gradle"
fi

# 清理之前的构建
log_info "清理之前的构建..."
$GRADLE_CMD clean --no-daemon || true

# 构建 APK
log_info "开始构建 APK..."
log_info "这可能需要 5-10 分钟，请耐心等待..."
echo ""

# 构建版本选择
BUILD_TYPE="${1:-release}"

case "$BUILD_TYPE" in
    "debug")
        log_info "构建 Debug 版本..."
        $GRADLE_CMD assembleDebug --no-daemon --stacktrace
        APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
        ;;
    "release")
        log_info "构建 Release 版本..."

        # 检查是否需要签名
        if [ ! -f "app/release.keystore" ]; then
            log_warn "未找到签名密钥，使用调试签名"
            # 修改 build.gradle 使用调试签名
            $GRADLE_CMD assembleRelease --no-daemon --stacktrace
        else
            log_info "使用签名密钥构建..."
            $GRADLE_CMD assembleRelease --no-daemon --stacktrace
        fi

        APK_PATH="app/build/outputs/apk/release/app-release.apk"
        ;;
    *)
        log_error "不支持的构建类型: $BUILD_TYPE"
        log_info "支持的类型: debug, release"
        exit 1
        ;;
esac

# 检查构建结果
if [ -f "$APK_PATH" ]; then
    APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
    echo ""
    echo "========================================"
    log_success "APK 构建成功！"
    echo ""
    echo "文件位置: $PWD/$APK_PATH"
    echo "文件大小: $APK_SIZE"
    echo "构建类型: $BUILD_TYPE"
    echo "========================================"

    # 复制到项目根目录
    APK_NAME="周易算卦-$(date +%Y%m%d-%H%M%S)-$BUILD_TYPE.apk"
    cp "$APK_PATH" "$APK_NAME"
    log_success "APK 已复制到: $PWD/$APK_NAME"

    # 获取版本信息
    if grep -q "versionName" app/build.gradle 2>/dev/null; then
        VERSION_NAME=$(grep "versionName" app/build.gradle | head -n1 | cut -d'"' -f2)
        VERSION_CODE=$(grep "versionCode" app/build.gradle | head -n1 | awk '{print $2}')
        echo ""
        echo "版本: $VERSION_NAME (versionCode: $VERSION_CODE)"
    fi

    echo ""
    echo "现在可以："
    echo "1. 安装到手机: adb install $APK_NAME"
    echo "2. 传输到手机: 通过数据线或云盘传输"
    echo ""

    exit 0
else
    log_error "APK 构建失败，找不到输出文件"
    log_info "期望位置: $PWD/$APK_PATH"
    log_info "请查看构建日志"
    exit 1
fi
