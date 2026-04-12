#!/bin/bash

# 大仙周易小程序 - 自动上传和备份脚本
# 功能：上传到微信小程序平台 + 备份到 GitHub

# 不自动退出，遇到错误继续执行
# set -e

# 配置变量
PROJECT_DIR="/workspace/projects/workspace/daxianzhouyi-miniprogram-v2.3.25"
GITHUB_REPO="git@github.com:daxian10086/daxianzhouyi-miniprogram.git"
BRANCH="main"
VERSION_FILE="${PROJECT_DIR}/project.config.json"

# 日志文件
LOG_FILE="/tmp/miniprogram_upload.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== [${DATE}] 开始上传和备份 ===" | tee -a ${LOG_FILE}

# 1. 检查项目目录
if [ ! -d "${PROJECT_DIR}" ]; then
    echo "❌ 错误：项目目录不存在 ${PROJECT_DIR}" | tee -a ${LOG_FILE}
    exit 1
fi

echo "✅ 项目目录检查通过" | tee -a ${LOG_FILE}

# 2. 获取当前版本
if [ -f "${VERSION_FILE}" ]; then
    VERSION=$(grep '"versionName"' ${VERSION_FILE} | awk -F'"' '{print $4}')
    echo "📦 当前版本：${VERSION}" | tee -a ${LOG_FILE}
else
    echo "⚠️  警告：未找到版本配置文件" | tee -a ${LOG_FILE}
    VERSION="unknown"
fi

# 3. 备份到 GitHub
echo "📤 开始备份到 GitHub..." | tee -a ${LOG_FILE}

cd ${PROJECT_DIR}

# 检查是否是 Git 仓库
if [ ! -d ".git" ]; then
    echo "⚠️  不是 Git 仓库，跳过 GitHub 备份" | tee -a ${LOG_FILE}
else
    # 配置 Git 用户信息（如果未配置）
    if ! git config user.name > /dev/null 2>&1; then
        git config user.name "daxian10086"
        git config user.email "daxian10086@github.com"
    fi

    # 添加远程仓库（如果未配置）
    if ! git remote get-url origin > /dev/null 2>&1; then
        echo "🔧 添加远程仓库..." | tee -a ${LOG_FILE}
        git remote add origin ${GITHUB_REPO}
    fi

    # 添加所有文件
    git add . 2>&1 | tee -a ${LOG_FILE}

    # 检查是否有改动
    if git diff --cached --quiet; then
        echo "ℹ️  没有改动，跳过提交" | tee -a ${LOG_FILE}
    else
        # 提交
        git commit -m "v${VERSION} - 自动备份 ${DATE}" 2>&1 | tee -a ${LOG_FILE}

        # 推送到 GitHub
        echo "⏳ 推送到 GitHub..." | tee -a ${LOG_FILE}
        git push -u origin ${BRANCH} --force 2>&1 | tee -a ${LOG_FILE}

        if [ $? -eq 0 ]; then
            echo "✅ GitHub 备份成功" | tee -a ${LOG_FILE}
        else
            echo "❌ GitHub 备份失败（继续执行微信上传）" | tee -a ${LOG_FILE}
        fi
    fi
fi

# 4. 上传到微信小程序平台
echo "📱 开始上传到微信小程序平台..." | tee -a ${LOG_FILE}

# 检查是否安装了 miniprogram-ci
if ! command -v npx &> /dev/null; then
    echo "❌ 错误：未找到 npx，请先安装 Node.js" | tee -a ${LOG_FILE}
    exit 1
fi

# 使用 miniprogram-ci 上传
npx miniprogram-ci upload \
    --project ${PROJECT_DIR}/project.config.json \
    --version ${VERSION} \
    --desc "v${VERSION} - 自动上传 ${DATE}" \
    --robot 1 \
    2>&1 | tee -a ${LOG_FILE}

if [ $? -eq 0 ]; then
    echo "✅ 微信小程序上传成功" | tee -a ${LOG_FILE}
else
    echo "❌ 微信小程序上传失败" | tee -a ${LOG_FILE}
    exit 1
fi

# 5. 完成
echo "=== [${DATE}] 上传和备份完成 ===" | tee -a ${LOG_FILE}
echo "" | tee -a ${LOG_FILE}

exit 0
