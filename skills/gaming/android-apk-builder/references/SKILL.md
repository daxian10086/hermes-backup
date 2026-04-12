# Android APK 构建技能

## 功能
为 Android 项目构建 APK 文件，支持多种构建方式。

## 使用场景
当用户要求构建 Android APK 时使用此技能。

## 支持的构建方式

### 1. 本地构建（如果环境已配置）
- 使用 Android SDK + Gradle 构建
- 支持 Debug 和 Release 版本
- 自动检测环境并选择合适方式

### 2. 使用 Termux 构建（Android 终端）
- 在 Android 设备上使用 Termux 构建
- 自动安装必要工具
- 支持 Release 版本构建

### 3. 使用在线构建服务
- 使用 GitHub Actions 自动构建
- 或使用 Replit 等在线 IDE
- 自动生成并下载 APK

### 4. 生成构建指导文档
- 如果无法构建，生成详细的构建指南
- 包含 Android Studio、AIDE 等多种方法的步骤

## 使用流程

### 步骤1：检查项目结构
确认项目包含：
- `app/build.gradle`
- `app/src/main/AndroidManifest.xml`
- 必要的源代码文件

### 步骤2：检测构建环境
检查是否已安装：
- Android SDK (`ANDROID_HOME`)
- Java (JDK)
- Gradle 或 Gradle Wrapper (`./gradlew`)

### 步骤3：选择构建方式

#### 如果环境完整 → 本地构建
```bash
cd /path/to/project
./gradlew clean
./gradlew assembleRelease
```

#### 如果是 Android 设备 → Termux 构建
```bash
# 在 Termux 中
pkg install openjdk-17 gradle
# 配置 Android SDK
cd /path/to/project
./gradlew assembleRelease
```

#### 如果需要在线构建 → GitHub Actions
创建 `.github/workflows/build.yml`

#### 如果环境不完整 → 生成构建指南
生成详细的构建文档，指导用户使用：
- Android Studio
- AIDE
- 在线 IDE

### 步骤4：处理构建结果
- 成功：返回 APK 文件路径
- 失败：提供错误信息和解决方案

## 环境要求

### 本地构建
- Android SDK API 24+
- Java 8+
- Gradle 7.0+

### Termux 构建
- Termux 应用
- 2GB+ 可用存储
- 稳定网络（下载 SDK）

### 在线构建
- GitHub 账号
- 网络连接

## 常见问题

### Q1: 提示找不到 Android SDK
**解决：**
- 本地：安装 Android Studio 并配置 SDK
- Termux：使用 `sdkmanager` 安装必要组件
- 在线：使用 GitHub Actions

### Q2: Gradle 同步失败
**解决：**
- 检查网络连接
- 清理 Gradle 缓存：`./gradlew clean`
- 删除 `.gradle` 文件夹后重试

### Q3: 签名问题
**解决：**
- Debug 构建：使用默认调试签名
- Release 构建：创建签名密钥或使用 GitHub Actions 自动签名

### Q4: 构建超时
**解决：**
- 增加构建超时时间
- 清理旧构建文件
- 使用更快的构建方式

## 输出格式

### 成功时
```
✅ APK 构建成功！

文件位置: /path/to/app-release.apk
文件大小: 2.5 MB
构建类型: Release
版本信息: v1.0 (versionCode: 1)

[APK 文件已准备好，可以直接安装]
```

### 失败时
```
❌ APK 构建失败

错误信息: [具体错误]
可能原因: [原因分析]

解决方案:
1. [方案1]
2. [方案2]
3. [方案3]

📖 详细构建指南已生成: [文档路径]
```

## 最佳实践

1. **优先使用本地构建**（如果环境已配置）
2. **Android 设备用 Termux**（移动开发）
3. **复杂项目用在线构建**（GitHub Actions）
4. **简单测试用 AIDE**（快速原型）
5. ** always 生成构建指南**（提供备用方案）

## 相关命令

### 检查环境
```bash
echo $ANDROID_HOME
java -version
./gradlew --version
```

### 清理构建
```bash
./gradlew clean
rm -rf .gradle/ build/ app/build/
```

### 构建 Debug
```bash
./gradlew assembleDebug
```

### 构建 Release
```bash
./gradlew assembleRelease
```

### 查找 APK
```bash
find . -name "*.apk" -type f
```

## 更新日志

### v1.0 (2026-03-16)
- 初始版本
- 支持本地、Termux、在线构建
- 自动环境检测
- 生成构建指南
