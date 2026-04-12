# Android APK 构建技能

为 Android 项目构建 APK 的完整解决方案，支持多种构建方式。

## 📖 目录

- [功能](#功能)
- [快速开始](#快速开始)
- [构建方式](#构建方式)
- [使用指南](#使用指南)
- [常见问题](#常见问题)

## ✨ 功能

- ✅ 支持本地构建（Android SDK + Gradle）
- ✅ 支持 Termux 构建（Android 设备）
- ✅ 支持在线构建（GitHub Actions）
- ✅ 自动环境检测
- ✅ 生成详细构建指南
- ✅ 一键构建脚本

## 🚀 快速开始

### 检查环境
```bash
./check-env.sh
```

### 构建 APK（本地）
```bash
./build-apk.sh /path/to/project release
```

### 生成构建指南
```bash
./generate-guide.sh /path/to/project
```

### 配置 Termux 环境
```bash
./termux-build.sh
```

## 🛠️ 构建方式

### 1. 本地构建

**要求：**
- Android SDK 已安装
- Java 8+
- Gradle 或 Gradle Wrapper

**使用：**
```bash
./build-apk.sh 项目路径 release
```

### 2. Termux 构建

**要求：**
- Android 设备
- Termux 应用已安装
- 2GB+ 可用存储

**步骤：**
1. 在 Termux 中运行：
```bash
./termux-build.sh
```

2. 配置完成后构建：
```bash
cd 项目路径
./gradlew assembleRelease
```

### 3. 在线构建（GitHub Actions）

**要求：**
- GitHub 账号
- 项目已上传到 GitHub

**步骤：**
1. 复制 `templates/github-workflow.yml` 到项目的 `.github/workflows/` 目录
2. 推送到 GitHub
3. 在 Actions 页面触发构建或等待自动构建
4. 下载构建的 APK

**手动触发：**
- 进入 GitHub 仓库
- 点击 "Actions" 标签
- 选择 "Build Android APK"
- 点击 "Run workflow" 按钮

### 4. AIDE 构建

**要求：**
- Android 设备
- AIDE 应用

**步骤：**
1. 在应用商店安装 AIDE
2. 导入项目
3. 点击 "Run" 按钮

## 📖 使用指南

### 构建脚本说明

#### `check-env.sh` - 环境检测

检测当前构建环境是否完整：
- Java 版本
- Android SDK 配置
- Gradle 安装
- 项目结构

**使用：**
```bash
./check-env.sh
```

#### `build-apk.sh` - 构建 APK

自动化构建脚本，支持 Debug 和 Release 版本。

**参数：**
- 第1个参数：项目路径（必填）
- 第2个参数：构建类型 `debug|release`（可选，默认 debug）

**使用：**
```bash
# 构建 Debug 版本
./build-apk.sh /path/to/project debug

# 构建 Release 版本
./build-apk.sh /path/to/project release
```

**输出：**
- APK 文件位于项目目录
- 文件名格式：`app-YYYYMMDD-HHMMSS-[debug|release].apk`

#### `generate-guide.sh` - 生成构建指南

生成详细的 APK 构建指南，包含多种构建方法的说明。

**参数：**
- 第1个参数：项目路径（必填）
- 第2个参数：输出文件名（可选，默认 `APK构建指南.md`）

**使用：**
```bash
./generate-guide.sh /path/to/project
./generate-guide.sh /path/to/project 我的构建指南.md
```

#### `termux-build.sh` - Termux 环境配置

在 Termux 中配置完整的 Android 构建环境。

**使用：**
1. 在 Termux 中运行脚本：
```bash
./termux-build.sh
```

2. 等待所有工具安装完成（需要约10-20分钟）

3. 构建项目：
```bash
cd 项目路径
./gradlew assembleRelease
```

### 模板文件

#### `templates/github-workflow.yml` - GitHub Actions 配置

用于在 GitHub 上自动构建 APK。

**特性：**
- 自动构建 Debug 和 Release 版本
- 支持手动触发
- 支持签名构建（需要配置 Secrets）
- 自动上传构建产物

**配置签名（可选）：**

在 GitHub 仓库设置中添加 Secrets：
- `KEYSTORE_BASE64`: keystore 文件的 Base64 编码
- `KEYSTORE_PASSWORD`: keystore 密码
- `KEY_ALIAS`: 密钥别名
- `KEY_PASSWORD`: 密钥密码

**生成 keystore Base64：**
```bash
base64 -i app/release.keystore
```

## ❓ 常见问题

### Q1: 提示找不到 Java

**解决方案：**
```bash
# 安装 Java (Ubuntu/Debian)
sudo apt install openjdk-17-jdk

# 安装 Java (macOS)
brew install openjdk@17

# 安装 Java (Windows)
下载并安装 JDK 17+
```

### Q2: 提示找不到 Android SDK

**解决方案：**
```bash
# 设置环境变量
export ANDROID_HOME=/path/to/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools

# 永久设置（添加到 ~/.bashrc）
echo 'export ANDROID_HOME=/path/to/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

### Q3: Gradle 构建失败

**解决方案：**
```bash
# 清理构建
./gradlew clean

# 删除缓存
rm -rf .gradle/
rm -rf build/
rm -rf app/build/

# 重新构建
./gradlew assembleRelease
```

### Q4: Termux 构建时内存不足

**解决方案：**
```bash
# 增加 Termux 内存
echo "export GRADLE_OPTS='-Xmx2g -XX:MaxMetaspaceSize=512m'" >> ~/.bashrc
source ~/.bashrc
```

### Q5: GitHub Actions 构建失败

**解决方案：**
- 检查 workflow 文件路径是否正确（`.github/workflows/build.yml`）
- 确保项目包含 `gradlew` 文件
- 查看 Actions 日志获取详细错误信息
- 确保仓库配置了正确的 GitHub Actions 权限

### Q6: APK 安装失败

**可能原因：**
1. 签名问题：确保使用正确的签名密钥
2. 版本冲突：卸载旧版本后重新安装
3. 权限问题：在手机上开启"允许安装未知来源应用"

## 📝 注意事项

1. **保存好签名密钥**
   - keystore 文件必须安全保存
   - 如果丢失密钥，将无法更新已发布的 APK
   - 建议备份到多个安全位置

2. **版本号管理**
   - 每次发布新版本时，`versionCode` 必须增加
   - `versionName` 用于显示给用户

3. **构建时间**
   - 首次构建需要下载依赖（约5-10分钟）
   - 后续构建会使用缓存，速度更快

4. **存储空间**
   - Android SDK 需要约 2GB 存储空间
   - 构建过程会产生临时文件

## 🔗 相关资源

- [Android 官方文档](https://developer.android.com/)
- [Gradle 官方文档](https://gradle.org/docs/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Termux Wiki](https://wiki.termux.com/)
- [AIDE 官网](https://github.com/apps4avh/aide)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

祝你构建成功！🎉
