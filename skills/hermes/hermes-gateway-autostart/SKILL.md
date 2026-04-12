---
name: hermes-gateway-autostart
description: Hermes Gateway 开机自启动排障指南 - 解决飞书网关在终端重启后不自动运行的问题
tags: [hermes, gateway, feishu, systemd, auto-start, linger]
---

# Hermes Gateway 开机自启动排障指南

## 症状
- 重启终端后飞书发消息没反应
- 网关进程不运行
- 需要手动 `hermes gateway restart` 才能恢复

## 排障步骤

### 1. 确认服务名称
**重要**：`systemd 服务名是 `hermes-gateway.service`，不是 `hermes-feishu`！

```bash
systemctl --user status hermes-gateway        # 查看服务状态
systemctl --user list-units --all | grep hermes  # 列出所有 hermes 相关服务
```

### 2. 检查服务是否 enabled（开机自启）
```bash
systemctl --user is-enabled hermes-gateway
```

### 3. 检查 linger 是否启用
linger 是让 systemd user service 在用户登出后继续运行的关键：
```bash
loginctl show-user $USER | grep Linger
```
如果 `Linger=no` 或没有输出，执行：
```bash
sudo loginctl enable-linger $USER
```

### 4. 重新安装网关服务
如果服务已 enabled 但仍不生效，强制重装：
```bash
hermes gateway install --force
```

### 5. 验证网关运行状态
```bash
hermes gateway status
systemctl --user status hermes-gateway
cat ~/.hermes/gateway_state.json   # 查看飞书连接状态
```

### 6. 查看 journal 日志
```bash
journalctl --user -u hermes-gateway -n 50 --no-pager
```

## 快速修复命令（按顺序执行）
```bash
# 1. 启用 linger
sudo loginctl enable-linger $USER

# 2. 重新安装网关服务
hermes gateway install --force

# 3. 启动服务
systemctl --user start hermes-gateway

# 4. 验证
systemctl --user status hermes-gateway
cat ~/.hermes/gateway_state.json
```

## 关键发现
- **服务名是 `hermes-gateway`**，不是 `hermes-feishu`（飞书集成在 gateway 内）
- linger 必须启用，否则用户登出后服务会停止
- 服务状态显示 `active (running)` 不代表飞书 websocket 真的连着，需查看 `gateway_state.json` 的 `feishu.state`
- 飞书断连时 systemd 服务进程可能还活着，只是飞书 websocket 断了
