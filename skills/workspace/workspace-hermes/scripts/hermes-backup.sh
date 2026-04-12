#!/bin/bash
# Hermes 备份工具 - 备份配置和记忆到 GitHub
# 用法: ./hermes-backup.sh [push]

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Hermes 备份工具${NC}"
echo -e "${GREEN}========================================${NC}"

# 配置
HERMES_DIR="$HOME/.hermes"
BACKUP_DIR="/tmp/hermes-backup"
GITHUB_USER="daxian10086"
REPO_NAME="hermes-backup"
COMMIT_MSG="Hermes backup $(date '+%Y-%m-%d %H:%M')"

# 要备份的目录/文件
BACKUP_PATHS=(
    "$HERMES_DIR/skills"
    "$HERMES_DIR/memories"
    "$HERMES_DIR/config.yaml"
    "$HERMES_DIR/SOUL.md"
)

# 1. 初始化备份目录
echo -e "\n${YELLOW}[1/4] 初始化备份目录...${NC}"
mkdir -p "$BACKUP_DIR"

# 2. 复制文件
echo -e "\n${YELLOW}[2/4] 复制文件...${NC}"
for path in "${BACKUP_PATHS[@]}"; do
    if [ -e "$path" ]; then
        dest="$BACKUP_DIR/$(basename "$path")"
        cp -r "$path" "$dest"
        echo -e "✓ $path"
    else
        echo -e "${YELLOW}○ 跳过 $path (不存在)${NC}"
    fi
done

# 3. Git 操作
cd "$BACKUP_DIR"
echo -e "\n${YELLOW}[3/4] Git 提交...${NC}"

# 初始化 git（如果是新的）
if [ ! -d ".git" ]; then
    git init
    git add -A
    git commit -m "Initial Hermes backup"
    echo -e "${GREEN}✓ Git 仓库已初始化${NC}"
else
    git add -A
    if git diff --staged --quiet; then
        echo -e "${YELLOW}没有变更需要提交${NC}"
    else
        git commit -m "$COMMIT_MSG"
        echo -e "${GREEN}✓ 已提交: $COMMIT_MSG${NC}"
    fi
fi

# 4. 推送到 GitHub（如果指定了 push 参数）
if [ "$1" = "push" ]; then
    echo -e "\n${YELLOW}[4/4] 推送到 GitHub...${NC}"
    
    # 检查 gh 是否登录
    if ! gh auth status &>/dev/null; then
        echo -e "${RED}✗ GitHub CLI 未登录，请运行: gh auth login${NC}"
        echo -e "${YELLOW}或者手动推送:${NC}"
        echo -e "  cd $BACKUP_DIR"
        echo -e "  git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git"
        echo -e "  git push -u origin main"
        exit 1
    fi
    
    # 设置远程仓库
    REPO_URL="git@github.com:$GITHUB_USER/$REPO_NAME.git"
    if git remote get-url origin &>/dev/null; then
        git remote set-url origin "$REPO_URL"
    else
        git remote add origin "$REPO_URL"
    fi
    
    # 推送
    git push -u origin main 2>&1
    echo -e "${GREEN}✓ 推送成功！${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}备份完成！${NC}"
echo -e "${GREEN}备份位置: $BACKUP_DIR${NC}"
echo -e "${GREEN}========================================${NC}"
