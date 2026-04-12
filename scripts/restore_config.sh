#!/bin/bash
# OpenClaw 配置恢复脚本
# 从 GitHub 恢复配置

set -e

# 配置
WORKSPACE="/workspace/projects/workspace"
BACKUP_DIR="/tmp/openclaw-backup"
GITHUB_USER=""
GITHUB_REPO="openclaw-backup"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OpenClaw 配置恢复工具${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查参数
if [ -z "$1" ]; then
    echo -e "\n${RED}错误: 请指定 GitHub 仓库地址${NC}"
    echo -e "\n用法:"
    echo -e "  $0 <github-repo-url>"
    echo -e "\n示例:"
    echo -e "  $0 https://github.com/username/openclaw-backup.git"
    echo -e "  $0 github:username/openclaw-backup"
    exit 1
fi

REPO_URL="$1"

# 1. 清理旧备份
echo -e "\n${YELLOW}[1/6] 清理旧备份...${NC}"
rm -rf "$BACKUP_DIR"

# 2. 克隆仓库
echo -e "\n${YELLOW}[2/6] 从 GitHub 克隆备份...${NC}"
git clone "$REPO_URL" "$BACKUP_DIR"

if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}错误: 克隆失败${NC}"
    exit 1
fi

# 3. 备份当前配置
echo -e "\n${YELLOW}[3/6] 备份当前配置...${NC}"
CURRENT_BACKUP="/tmp/openclaw-config-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$CURRENT_BACKUP"
if [ -d "$WORKSPACE" ]; then
    cp -r "$WORKSPACE" "$CURRENT_BACKUP/workspace" 2>/dev/null || true
fi
if [ -f "/workspace/projects/openclaw.json" ]; then
    cp "/workspace/projects/openclaw.json" "$CURRENT_BACKUP/" 2>/dev/null || true
fi
echo -e "  当前配置已备份到: $CURRENT_BACKUP"

# 4. 恢复工作区
echo -e "\n${YELLOW}[4/6] 恢复工作区配置...${NC}"
if [ -d "$BACKUP_DIR/workspace" ]; then
    cp -r "$BACKUP_DIR/workspace"/* "$WORKSPACE/" 2>/dev/null || true
    echo -e "  ✓ 工作区已恢复"
fi

# 5. 恢复 OpenClaw 配置
echo -e "\n${YELLOW}[5/6] 恢复 OpenClaw 配置...${NC}"
if [ -f "$BACKUP_DIR/openclaw-config/openclaw.json" ]; then
    cp "$BACKUP_DIR/openclaw-config/openclaw.json" "/workspace/projects/openclaw.json"
    echo -e "  ✓ openclaw.json 已恢复"
fi

# 6. 恢复技能（可选）
echo -e "\n${YELLOW}[6/6] 恢复技能...${NC}"
if [ -d "$BACKUP_DIR/skills" ] && [ -d "$BACKUP_DIR/skills" ]; then
    echo -e "  技能目录位置: $BACKUP_DIR/skills"
    echo -e "  请手动复制技能文件到 ~/.openclaw/skills/"
fi

# 生成恢复报告
cat > "$BACKUP_DIR/restore-report.txt" << EOF
========================================
OpenClaw 配置恢复报告
========================================

恢复时间: $(date '+%Y-%m-%d %H:%M:%S')
备份来源: $REPO_URL

恢复统计:
  - 恢复文件数: $(find "$BACKUP_DIR" -type f | wc -l)
  - 恢复目录数: $(find "$BACKUP_DIR" -type d | wc -l)

重要文件:
  - SOUL.md: $([ -f "$WORKSPACE/SOUL.md" ] && echo "✓" || echo "✗")
  - MEMORY.md: $([ -f "$WORKSPACE/MEMORY.md" ] && echo "✓" || echo "✗")
  - AGENTS.md: $([ -f "$WORKSPACE/AGENTS.md" ] && echo "✓" || echo "✗")
  - TOOLS.md: $([ -f "$WORKSPACE/TOOLS.md" ] && echo "✓" || echo "✗")
  - openclaw.json: $([ -f "/workspace/projects/openclaw.json" ] && echo "✓" || echo "✗")

旧配置备份: $CURRENT_BACKUP

恢复状态: 完成 ✓

========================================
EOF

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}恢复完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n查看恢复报告:"
echo -e "  cat $BACKUP_DIR/restore-report.txt"
echo -e "\n旧配置备份位置:"
echo -e "  $CURRENT_BACKUP"
echo -e "\n${YELLOW}注意: 需要重启 Gateway 才能生效！${NC}"
echo -e "\n重启命令:"
echo -e "  sh /workspace/projects/scripts/restart.sh"
