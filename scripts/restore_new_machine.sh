#!/bin/bash
# 新机器一键恢复脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}新机器一键恢复脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 配置
REPO_URL="https://github.com/daxian10086/openclaw-backup.git"
TEMP_DIR="/tmp/openclaw-backup"
WORKSPACE="/workspace/projects/workspace"

# 1. 克隆仓库
echo -e "\n${YELLOW}[1/6] 克隆备份仓库...${NC}"
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi
git clone "$REPO_URL" "$TEMP_DIR"

# 2. 创建目录
echo -e "\n${YELLOW}[2/6] 创建目录...${NC}"
mkdir -p "$WORKSPACE"
mkdir -p /workspace/projects/scripts

# 3. 恢复工作区
echo -e "\n${YELLOW}[3/6] 恢复工作区...${NC}"
cp -r "$TEMP_DIR/workspace/"* "$WORKSPACE/" 2>/dev/null || true

# 4. 恢复脚本
echo -e "\n${YELLOW}[4/6] 恢复脚本...${NC}"
cp -r "$TEMP_DIR/scripts/"* /workspace/projects/scripts/ 2>/dev/null || true

# 5. 恢复配置
echo -e "\n${YELLOW}[5/6] 恢复配置...${NC}"
cp "$TEMP_DIR/openclaw-config/openclaw.json" /workspace/projects/ 2>/dev/null || true

# 6. 安装备份工具
echo -e "\n${YELLOW}[6/6] 安装备份工具...${NC}"
chmod +x /workspace/projects/scripts/openclaw-backup
chmod +x /workspace/projects/scripts/backup_config.sh
chmod +x /workspace/projects/scripts/restore_config.sh
ln -sf /workspace/projects/scripts/openclaw-backup /usr/local/bin/openclaw-backup

# 验证
echo -e "\n${GREEN}验证安装...${NC}"
openclaw-backup help

# 检查核心文件
echo -e "\n${GREEN}核心文件检查:${NC}"
for file in SOUL.md MEMORY.md AGENTS.md TOOLS.md; do
    if [ -f "$WORKSPACE/$file" ]; then
        echo -e "  ✓ $file"
    else
        echo -e "  ✗ $file (未找到)"
    fi
done

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}恢复完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}需要重启 Gateway 使配置生效:${NC}"
echo -e "  sh /workspace/projects/scripts/restart.sh"
echo -e "\n${YELLOW}查看备份状态:${NC}"
echo -e "  openclaw-backup status"
