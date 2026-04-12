#!/bin/bash
# OpenClaw 配置备份脚本 - 排除大文件
# 将整个工作区备份到 GitHub

set -e

# 配置
WORKSPACE="/workspace/projects/workspace"
BACKUP_DIR="/tmp/openclaw-backup"
GITHUB_USER="daxian10086"
GITHUB_REPO="openclaw-backup"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OpenClaw 配置备份工具（排除大文件）${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 清理并创建备份目录
echo -e "\n${YELLOW}[1/6] 创建备份目录...${NC}"
rm -rf "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# 2. 复制工作区（排除大文件）
echo -e "\n${YELLOW}[2/6] 复制配置文件（排除大文件）...${NC}"
rsync -av --exclude='*.gguf' \
          --exclude='*.bin' \
          --exclude='*.safetensors' \
          --exclude='node_modules' \
          --exclude='.git' \
          --exclude='temp' \
          --exclude='*.zip' \
          --exclude='*.exe' \
          "$WORKSPACE/" "$BACKUP_DIR/workspace/" 2>/dev/null || true

# 3. 复制 OpenClaw 配置
echo -e "\n${YELLOW}[3/6] 复制 OpenClaw 配置...${NC}"
mkdir -p "$BACKUP_DIR/openclaw-config"
if [ -f "/workspace/projects/openclaw.json" ]; then
    cp "/workspace/projects/openclaw.json" "$BACKUP_DIR/openclaw-config/"
fi

# 4. 复制脚本
echo -e "\n${YELLOW}[4/6] 复制脚本...${NC}"
mkdir -p "$BACKUP_DIR/scripts"
cp -r /workspace/projects/scripts/* "$BACKUP_DIR/scripts/" 2>/dev/null || true

# 5. 生成备份清单
echo -e "\n${YELLOW}[5/6] 生成备份清单...${NC}"
cat > "$BACKUP_DIR/backup-manifest.txt" << EOF
OpenClaw 配置备份
备份时间: $(date '+%Y-%m-%d %H:%M:%S')
版本: $(openclaw version 2>/dev/null || echo "未知")

备份内容:
- 工作区: $WORKSPACE
- 配置文件: openclaw.json
- 脚本目录: /workspace/projects/scripts

排除的大文件:
- *.gguf (Embedding 模型文件)
- *.bin (二进制文件)
- *.safetensors (模型文件)
- node_modules (Node.js 依赖)
- temp/ (临时文件)

文件清单:
EOF

find "$BACKUP_DIR" -type f | wc -l >> "$BACKUP_DIR/backup-manifest.txt"

# 6. 初始化 Git
echo -e "\n${YELLOW}[6/6] 初始化 Git 仓库...${NC}"
cd "$BACKUP_DIR"

# 移除旧的 Git 配置
rm -rf .git 2>/dev/null || true

# 初始化新的 Git
git init 2>/dev/null || true
git config user.email "backup@openclaw.local" 2>/dev/null
git config user.name "OpenClaw Backup" 2>/dev/null

# 添加所有文件
git add . 2>/dev/null || true

# 提交
git commit -m "OpenClaw 备份 - $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || echo "无更改需要提交"

# 生成备份报告
cat > "$BACKUP_DIR/backup-report.txt" << EOF
========================================
OpenClaw 配置备份报告
========================================

备份时间: $(date '+%Y-%m-%d %H:%M:%S')
备份位置: $BACKUP_DIR

备份统计:
  - 总文件数: $(find "$BACKUP_DIR" -type f | wc -l)
  - 总目录数: $(find "$BACKUP_DIR" -type d | wc -l)
  - 备份大小: $(du -sh "$BACKUP_DIR" | cut -f1)

重要文件:
  - SOUL.md: $([ -f "$WORKSPACE/SOUL.md" ] && echo "✓" || echo "✗")
  - MEMORY.md: $([ -f "$WORKSPACE/MEMORY.md" ] && echo "✓" || echo "✗")
  - AGENTS.md: $([ -f "$WORKSPACE/AGENTS.md" ] && echo "✓" || echo "✗")
  - TOOLS.md: $([ -f "$WORKSPACE/TOOLS.md" ] && echo "✓" || echo "✗")
  - openclaw.json: $([ -f "$BACKUP_DIR/openclaw-config/openclaw.json" ] && echo "✓" || echo "✗")

排除的文件:
  - embeddinggemma-300m-qat-Q8_0.gguf (314MB)
  - 其他大文件和临时文件

备份状态: 完成 ✓

========================================
EOF

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}备份完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n备份位置: $BACKUP_DIR"
echo -e "\n查看备份报告:"
echo -e "  cat $BACKUP_DIR/backup-report.txt"
echo -e "\n推送到 GitHub:"
echo -e "  cd $BACKUP_DIR"
echo -e "  git remote add origin https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
echo -e "  git push -u origin main"
