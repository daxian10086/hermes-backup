# 周易算卦 APK

一个基于易经64卦的随机算卦Android应用。

## 功能特点

- **摇一摇算卦** - 支持手机摇动触发算卦，更真实更有趣
- **震动反馈** - 摇动和结果显示时有震动反馈
- **分享解锁** - 内容隐藏，分享后才能查看完整运势
- **随机生成64卦之一**
- 显示上卦、下卦
- 显示整体卦象含义
- 详细展示六爻（从下到上）
- 每爻包含爻词和爻词解说
- 运势详解（运势、财运、家庭、健康）
- 中国风UI设计

## 核心功能说明

### 摇一摇算卦
1. 点击"算一卦"按钮
2. 显示"📱 摇动手机开始算卦"提示
3. 用力摇晃手机（上下左右都可以）
4. 检测到摇动后显示"正在摇卦..."
5. 停止摇动后，显示"算卦中..."（2秒）
6. 显示算卦结果

### 震动反馈
- 摇动手机时持续震动（每80ms一次）
- 停止摇动后震动停止
- 显示结果时震动一次提示
- 解锁内容后震动确认

### 分享解锁功能
- **运势详解**：需要分享后才能查看
- **选中爻**：需要分享后才能查看
- **其他爻**：需要分享后才能查看
- 点击右上角菜单 → "分享"
- 分享成功后，所有内容自动解锁
- 可以通过菜单中的"重置分享状态"重新锁定
- 点击"分享解锁"按钮后，1秒后自动解锁

## 项目结构

```
fortune-teller/
├── app/
│   ├── src/main/
│   │   ├── java/com/fortunetelling/i/ching/
│   │   │   ├── MainActivity.kt              # 主界面（新增摇一摇、震动、分享功能）
│   │   │   ├── Hexagram.kt                  # 卦象数据类
│   │   │   ├── Trigrams.kt                  # 八卦数据
│   │   │   ├── HexagramGenerator.kt         # 随机生成器（新增 currentHexagram 属性）
│   │   │   ├── HexagramsData.kt             # 64卦完整数据
│   │   │   └── HexagramFortunes.kt            # 运势详解数据
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   ├── activity_main.xml        # 主界面布局
│   │   │   │   ├── layout_shake_hint_large.xml  # 摇动提示布局
│   │   │   │   ├── view_share_blur.xml        # 内容模糊提示布局
│   │   │   │   ├── dialog_share.xml          # 分享引导弹窗布局
│   │   │   │   └── dialog_loading.xml        # 加载对话框布局
│   │   │   ├── menu/
│   │   │   │   └── main.xml                 # 选项菜单（分享、重置）
│   │   │   ├── drawable/
│   │   │   │   ├── bg_shake_hint_large.xml  # 摇动提示背景
│   │   │   │   └── bg_share_blur.xml        # 内容模糊背景
│   │   │   └── values/
│   │   │       ├── strings.xml
│   │   │       ├── colors.xml
│   │   │       └── themes.xml
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── build.gradle
├── settings.gradle
├── gradle.properties
└── VERSION.md                           # 版本信息
```

## 构建APK

### 前置要求

- Android Studio Arctic Fox 或更高版本
- JDK 8 或更高版本
- Android SDK API 34

### 构建步骤

1. 使用Android Studio打开项目：
   ```bash
   open fortune-teller
   ```

2. 等待Gradle同步完成

3. 构建Release版本APK：
   - 菜单: Build → Generate Signed Bundle / APK
   - 选择 APK
   - 创建或选择签名密钥
   - 选择 release 构建类型
   - APK会生成在 `app/release/app-release.apk`

### 或使用命令行构建

```bash
cd fortune-teller

# 构建Debug版本
./gradlew assembleDebug

# 构建Release版本
./gradlew assembleRelease
```

APK位置：
- Debug: `app/build/outputs/apk/debug/app-debug.apk`
- Release: `app/build/outputs/apk/release/app-release.apk`

## 使用说明

1. 安装APK到Android设备
2. 打开应用
3. 点击"算一卦"按钮
4. 摇动手机算卦
5. 查看卦象结果
6. 点击右上角菜单分享给好友
7. 分享后查看完整运势详解

## 卦象数据

包含完整的64卦数据：
- 卦序（1-64）
- 卦名
- 上卦和下卦
- 六爻爻词（从下到上）
- 爻词解说
- 整体卦象含义

## 运势详解

包含四个维度的运势分析：
- **运势**：整体运势和运势走向
- **财运**：财运和投资建议
- **家庭**：家庭和人际关系
- **健康**：健康和生活建议

## 技术栈

- Kotlin
- Android SDK
- Material Components
- ConstraintLayout
- CardView
- 传感器管理器（加速度传感器）
- 震动管理器（Vibrator）

## 权限说明

应用需要以下权限：
- `android.permission.VIBRATE` - 震动反馈

## 许可证

MIT License
