#!/bin/bash

# 周易算卦 APK 构建脚本

echo "======================================"
echo "周易算卦 APK 构建脚本"
echo "======================================"
echo ""

# 检查是否安装了Android SDK
if [ -z "$ANDROID_HOME" ]; then
    echo "错误: 未找到ANDROID_HOME环境变量"
    echo "请先安装Android SDK并设置环境变量"
    exit 1
fi

# 清理之前的构建
echo "清理之前的构建..."
./gradlew clean

# 构建Debug版本
echo ""
echo "构建Debug版本..."
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Debug APK构建成功!"
    echo "位置: app/build/outputs/apk/debug/app-debug.apk"
else
    echo ""
    echo "✗ Debug APK构建失败!"
    exit 1
fi

# 构建Release版本
echo ""
echo "构建Release版本..."
./gradlew assembleRelease

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Release APK构建成功!"
    echo "位置: app/build/outputs/apk/release/app-release.apk"
else
    echo ""
    echo "✗ Release APK构建失败!"
    exit 1
fi

echo ""
echo "======================================"
echo "构建完成!"
echo "======================================"
