---
name: github-backup-proxy-fix
description: GitHub 备份脚本在大陆服务器无法连接 GitHub 的问题排查和修复
tags: [github, backup, proxy, mainland-china]
created: 2026-04-13
---

# GitHub 备份脚本配置 - 中国大陆服务器

## 概述
`~/.hermes/backup.sh` 是 Hermes Agent 的自动备份脚本，每天凌晨执行将 `.hermes` 目录备份到 GitHub。

## 已知问题
**push 失败 "No such device or address" 或 "Failed to connect to github.com port 443"**

原因：中国大陆无法直接访问 GitHub，需要配置代理。

## 备份脚本位置
```
~/.hermes/backup.sh
```

## 排查步骤

### 1. 检查网络连通性
```bash
curl -I --connect-timeout 5 https://github.com
```
如果超时，说明没有代理。

### 2. 检查代理软件
```bash
ps aux | grep -E 'clash|v2ray|xray|shadowsocks|qv2ray|surge' | grep -v grep
# 或检查常见端口
ss -tlnp | grep -E '7890|7891|1080|8118|8080|10808'
```

### 3. 检查环境变量
```bash
env | grep -i proxy
```

## 解决方案

### 方案1：配置 git 使用代理
假设代理端口为 7890（Clash 默认）：
```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### 方案2：使用 SSH 方式（推荐）
```bash
# 生成 SSH key（如果没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到 GitHub Settings -> SSH Keys

# 改用 SSH remote
git remote set-url origin git@github.com:username/repo.git
```

### 方案3：配置系统代理环境变量
```bash
# 在 /etc/environment 或 ~/.bashrc 中添加
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
```

## 手动测试备份
```bash
cd ~/.hermes && bash backup.sh
```

## 验证备份成功
```bash
cd ~/.hermes && git log --oneline -3
# 应该看到最新的 commit
```

## 相关文件
- 备份脚本：`~/.hermes/backup.sh`
- Git remote：`~/.hermes/.git/config`
