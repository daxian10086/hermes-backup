#!/bin/bash

# 简化构建脚本 - 使用系统已安装的工具

set -e

echo "======================================"
echo "周易算卦 APK 简化构建"
echo "======================================"

PROJECT_DIR="/workspace/projects/workspace/fortune-teller"
cd "$PROJECT_DIR"

# 设置环境变量
export ANDROID_HOME=/opt/android-sdk
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"

# 修改 build.gradle 降低 Gradle 版本要求
echo "调整项目配置..."
cat > build.gradle << 'EOF'
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.4.2'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
EOF

# 修改 app/build.gradle
cat > app/build.gradle << 'EOF'
plugins {
    id 'com.android.application'
    id 'kotlin-android'
}

android {
    namespace 'com.fortunetelling.i.ching'
    compileSdk 34

    defaultConfig {
        applicationId "com.fortunetelling.i.ching"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = '1.8'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}
EOF

echo "配置完成！"
