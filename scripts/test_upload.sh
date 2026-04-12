#!/bin/bash

# 测试上传脚本

cd /workspace/projects/workspace/daxianzhouyi-miniprogram-v2.3.25

echo "开始测试上传..."
echo "项目目录: $(pwd)"
echo "配置文件: project.config.json"
echo "密钥文件: private.key"
echo ""

# 检查文件
if [ ! -f "project.config.json" ]; then
    echo "❌ 错误：未找到 project.config.json"
    exit 1
fi

if [ ! -f "private.key" ]; then
    echo "❌ 错误：未找到 private.key"
    exit 1
fi

echo "✅ 文件检查通过"
echo ""

# 获取版本号
VERSION=$(grep '"versionName"' project.config.json | awk -F'"' '{print $4}')
echo "📦 当前版本：${VERSION}"
echo ""

# 尝试上传
echo "⏳ 开始上传..."
npx miniprogram-ci@2.1.31 upload \
    --appid wx8efbbb29c6b81122 \
    --project-path . \
    --private-key-path ./private.key \
    --upload-version "${VERSION}" \
    --upload-description "v${VERSION} - 自动上传" \
    --robot 1

UPLOAD_RESULT=$?

if [ $UPLOAD_RESULT -eq 0 ]; then
    echo ""
    echo "✅ 上传成功"
    # 记录日志
    echo "$(date '+%Y-%m-%d %H:%M:%S') - v${VERSION} 上传成功" >> /tmp/miniprogram_upload.log
else
    echo ""
    echo "❌ 上传失败，返回码：$UPLOAD_RESULT"
    # 记录错误
    echo "$(date '+%Y-%m-%d %H:%M:%S') - v${VERSION} 上传失败 (返回码: $UPLOAD_RESULT)" >> /tmp/miniprogram_upload.log
fi

exit $UPLOAD_RESULT
