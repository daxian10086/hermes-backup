#!/bin/bash
# OpenClaw 备份工具 - 手动创建 GitHub 仓库后推送

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OpenClaw 备份推送工具${NC}"
echo -e "${GREEN}========================================${NC}"

# 配置
BACKUP_DIR="/tmp/openclaw-backup"
GITHUB_USER="daxian10086"
REPO_NAME="openclaw-backup"

# 1. 检查备份是否存在
echo -e "\n${YELLOW}[1/4] 检查备份...${NC}"
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}备份不存在，先执行备份...${NC}"
    openclaw-backup backup
fi

# 2. 配置远程仓库
echo -e "\n${YELLOW}[2/4] 配置远程仓库...${NC}"
cd "$BACKUP_DIR"

# 获取 token
TOKEN=$(gh auth token)
REPO_URL="https://${GITHUB_USER}:${TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

if git remote get-url origin >/dev/null 2>&1; then
    echo -e "✓ 远程仓库已配置"
    git remote set-url origin "$REPO_URL"
else
    echo -e "✓ 添加远程仓库"
    git remote add origin "$REPO_URL"
fi

# 3. 检查仓库是否存在
echo -e "\n${YELLOW}[3/4] 检查 GitHub 仓库...${NC}"
if curl -s -o /dev/null -w "%{http_code}" "https://github.com/${GITHUB_USER}/${REPO_NAME}" | grep -q "200"; then
    echo -e "✓ 仓库已存在"
    REPO_EXISTS=true
else
    echo -e "${YELLOW}仓库不存在，需要手动创建${NC}"
    REPO_EXISTS=false
fi

# 4. 推送
echo -e "\n${YELLOW}[4/4] 推送到 GitHub...${NC}"

if [ "$REPO_EXISTS" = true ]; then
    # 仓库存在，直接推送
    echo -e "正在推送..."
    git push -u origin main 2>&1
    echo -e "${GREEN}✓ 推送成功！${NC}"
else
    # 仓库不存在，显示手动创建步骤
    echo -e "${YELLOW}需要先手动创建 GitHub 仓库${NC}"
    echo -e "\n请按以下步骤操作："

    echo -e "\n${GREEN}方法1: 使用网页创建仓库${NC}"
    echo -e "1. 访问: https://github.com/new"
    echo -e "2. 仓库名: ${REPO_NAME}"
    echo -e "3. 可见性: Public（公开）或 Private（私有）"
    echo -e "4. 不要初始化 README、.gitignore 或 LICENSE"
    echo -e "5. 点击「Create repository」"
    echo -e "6. 创建后，再次运行此脚本"

    echo -e "\n${GREEN}方法2: 升级 GitHub Token 权限${NC}"
    echo -e "1. 访问: https://github.com/settings/tokens"
    echo -e "2. 创建新 Token 或编辑现有 Token"
    echo -e "3. 勾选「repo」权限（包含 repo:status, repo_deployment, public_repo 等）"
    echo -e "4. 保存后，运行: gh auth login"
    echo -e "5. 再次运行此脚本"

    echo -e "\n${GREEN}创建仓库后，运行推送命令：${NC}"
    echo -e "  cd $BACKUP_DIR"
    echo -e "  git push -u origin main"

    exit 1
fi

# 显示结果
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}备份推送完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n仓库地址:"
echo -e "  https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo -e "\n以后更新备份，只需运行:"
echo -e "  openclaw-backup backup-push"
