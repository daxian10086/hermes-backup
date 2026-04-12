#!/bin/bash

# Android 构建环境检测脚本

echo "======================================"
echo "Android 构建环境检测"
echo "======================================"
echo ""

# 检测 Java
echo "📦 Java:"
if command -v java &> /dev/null; then
    java -version 2>&1 | head -n 1
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    echo "✓ Java 已安装"
else
    echo "✗ Java 未安装"
fi
echo ""

# 检测 ANDROID_HOME
echo "📱 Android SDK:"
if [ -n "$ANDROID_HOME" ]; then
    echo "✓ ANDROID_HOME 已配置: $ANDROID_HOME"
    if [ -d "$ANDROID_HOME" ]; then
        echo "  - 目录存在"
        if [ -d "$ANDROID_HOME/platforms" ]; then
            PLATFORM_COUNT=$(ls -1 "$ANDROID_HOME/platforms" 2>/dev/null | wc -l)
            echo "  - 已安装 $PLATFORM_COUNT 个平台"
        fi
    else
        echo "  ⚠ 目录不存在"
    fi
else
    echo "✗ ANDROID_HOME 未配置"
    echo "  提示: 设置环境变量 export ANDROID_HOME=/path/to/android-sdk"
fi
echo ""

# 检测 Gradle
echo "🔧 Gradle:"
if command -v gradle &> /dev/null; then
    gradle --version 2>&1 | head -n 1
    echo "✓ Gradle 已安装"
else
    echo "✗ Gradle 未安装"
fi
echo ""

# 检测 Gradle Wrapper
if [ -f "gradlew" ]; then
    echo "✓ Gradle Wrapper 已找到"
    if [ -x "gradlew" ]; then
        echo "  ✓ 可执行"
    else
        echo "  ⚠ 需要执行权限: chmod +x gradlew"
    fi
else
    echo "✗ Gradle Wrapper 未找到"
fi
echo ""

# 检测项目结构
echo "📁 项目结构:"
if [ -f "app/build.gradle" ] || [ -f "app/build.gradle.kts" ]; then
    echo "✓ app/build.gradle 存在"
else
    echo "✗ app/build.gradle 不存在"
fi

if [ -f "app/src/main/AndroidManifest.xml" ]; then
    echo "✓ AndroidManifest.xml 存在"
else
    echo "✗ AndroidManifest.xml 不存在"
fi

if [ -d "app/src/main/java" ] || [ -d "app/src/main/kotlin" ]; then
    echo "✓ 源代码目录存在"
else
    echo "✗ 源代码目录不存在"
fi
echo ""

# 检测存储空间
echo "💾 存储空间:"
PROJECT_SIZE=$(du -sh . | cut -f1)
echo "项目大小: $PROJECT_SIZE"
echo "======================================"

# 生成建议
echo ""
echo "💡 建议:"
JAVA_INSTALLED=false
SDK_CONFIGURED=false
GRADLE_INSTALLED=false

command -v java &> /dev/null && JAVA_INSTALLED=true
[ -n "$ANDROID_HOME" ] && SDK_CONFIGURED=true
command -v gradle &> /dev/null && GRADLE_INSTALLED=true

if $JAVA_INSTALLED && $SDK_CONFIGURED && $GRADLE_INSTALLED; then
    echo "✓ 环境完整，可以直接构建"
    echo "  运行: ./build-apk.sh <项目路径> release"
elif $JAVA_INSTALLED; then
    echo "⚠ 缺少 Android SDK 或 Gradle"
    echo "  方案1: 安装 Android Studio"
    echo "  方案2: 使用 Termux 构建（Android 设备）"
    echo "  方案3: 使用在线构建服务"
else
    echo "✗ 环境不完整，无法本地构建"
    echo "  建议: 使用 Android Studio 或在线构建服务"
    echo "  运行: ./generate-guide.sh <项目路径>"
fi

echo "======================================"
