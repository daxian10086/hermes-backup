#!/bin/bash

# Android APK 构建脚本
# 支持多种构建方式：本地、Termux、在线

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
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

# 检查参数
if [ $# -eq 0 ]; then
    log_error "请指定项目路径"
    echo "用法: $0 <项目路径> [构建类型: debug|release]"
    echo "示例: $0 /path/to/project release"
    exit 1
fi

PROJECT_PATH="$1"
BUILD_TYPE="${2:-debug}"
BUILD_TYPE=$(echo "$BUILD_TYPE" | tr '[:upper:]' '[:lower:]')

log_info "开始构建 APK..."
log_info "项目路径: $PROJECT_PATH"
log_info "构建类型: $BUILD_TYPE"

# 检查项目路径
if [ ! -d "$PROJECT_PATH" ]; then
    log_error "项目路径不存在: $PROJECT_PATH"
    exit 1
fi

cd "$PROJECT_PATH"

# 检查是否是 Android 项目
if [ ! -f "app/build.gradle" ] && [ ! -f "app/build.gradle.kts" ]; then
    log_error "不是有效的 Android 项目，找不到 app/build.gradle"
    exit 1
fi

# 检查环境
log_info "检查构建环境..."

# 检查 Java
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    log_success "Java 已安装: $JAVA_VERSION"
else
    log_warn "Java 未安装"
fi

# 检查 Android SDK
if [ -n "$ANDROID_HOME" ]; then
    log_success "Android SDK 已配置: $ANDROID_HOME"
else
    log_warn "ANDROID_HOME 未配置"
fi

# 检查 Gradle
if [ -f "gradlew" ]; then
    log_success "Gradle Wrapper 已找到"
    GRADLE_CMD="./gradlew"
elif command -v gradle &> /dev/null; then
    log_success "Gradle 已安装"
    GRADLE_CMD="gradle"
else
    log_error "找不到 Gradle"
    log_info "请安装 Gradle 或确保项目包含 gradlew"
    exit 1
fi

# 清理之前的构建
log_info "清理之前的构建..."
$GRADLE_CMD clean

# 构建
log_info "开始构建 $BUILD_TYPE APK..."

case "$BUILD_TYPE" in
    "debug")
        $GRADLE_CMD assembleDebug
        APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
        ;;
    "release")
        # 检查是否需要签名
        if [ ! -f "app/release.keystore" ] && [ ! -f "app/build.gradle" ]; then
            log_warn "未找到签名密钥，将使用默认配置"
        fi
        $GRADLE_CMD assembleRelease
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
    log_success "APK 构建成功！"
    echo ""
    echo "======================================"
    echo "APK 文件位置: $PROJECT_PATH/$APK_PATH"
    echo "文件大小: $APK_SIZE"
    echo "构建类型: $BUILD_TYPE"
    echo "======================================"

    # 尝试获取版本信息
    if grep -q "versionName" app/build.gradle 2>/dev/null; then
        VERSION_NAME=$(grep "versionName" app/build.gradle | head -n1 | cut -d'"' -f2)
        VERSION_CODE=$(grep "versionCode" app/build.gradle | head -n1 | awk '{print $2}')
        echo "版本: $VERSION_NAME (versionCode: $VERSION_CODE)"
        echo "======================================"
    fi

    # 复制到项目根目录
    APK_NAME="app-$(date +%Y%m%d-%H%M%S)-$BUILD_TYPE.apk"
    cp "$APK_PATH" "$APK_NAME"
    log_success "APK 已复制到: $PROJECT_PATH/$APK_NAME"

    exit 0
else
    log_error "APK 构建失败，找不到输出文件"
    log_info "期望位置: $PROJECT_PATH/$APK_PATH"
    log_info "请检查构建日志"
    exit 1
fi
