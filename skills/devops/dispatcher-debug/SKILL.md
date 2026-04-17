---
name: dispatcher-debug
description: OpenClaw Dispatcher架构、回调机制、小龙工作流
category: devops
---

# Dispatcher 架构与小龙工作流（2026-04-17 更新）

## 架构
```
大仙 → Hermes (小马) → dispatcher (8080) → 小龙执行
                                        ↓
                              dragon_report.txt (小马监控)
                              飞书消息 → 龙马群 (大仙看到)
```

## 工作流程（精简版）

### 小龙任务完成后输出到两个地方：
1. **dragon_report.txt** (`/home/wdmms123/.hermes/cron/output/dragon_report.txt`)
   - 小马的 watcher 实时监控这个文件
   - 小马自己看日志，不打扰大仙
2. **飞书消息到龙马群** (chat_id: `oc_c9ca98528b2a6d38f528696e11cb0ae4`)
   - 大仙直接在飞书群看到结果

### 小马的 watcher
- 服务名: `dragon-report-watcher`
- systemd 服务: `/etc/systemd/system/dragon-report-watcher.service`
- 监控文件: `/home/wdmms123/.hermes/cron/output/dragon_report.txt`
- 日志查看: `sudo journalctl -u dragon-report-watcher -f`
- 进程查看: `ps aux | grep dragon_report_watcher`

## 回调服务（2026-04-17 确认必须运行）
- **18080 callback_server** — 必须运行！小龙通过它callback到飞书群
  - 进程: `python3 -u /tmp/callback_server.py` (PID: 61921)
  - 接口: `POST /callback` → 飞书群 (chat_id: oc_c9ca98528b2a6d38f528696e11cb0ae4)
- ~~18282 dragon_callback_server~~ — 已废弃
- 启动命令: `python3 -u /tmp/callback_server.py &`
- 验证: `curl -s -X POST http://127.0.0.1:18080/callback -d "test"`

## 发送任务给小龙
```bash
curl -X POST http://192.168.1.100:8080/dispatch \
  -H "Content-Type: application/json" \
  -d '{"task": "任务内容", "type": "stock|general", "timeout": 120}'
```

- `type=stock`: 股票分析任务
- `type=general`: 通用任务
