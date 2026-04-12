# 🐴 Hermes Workspace - 基于 OpenClaw 优化

这是专为 **Hermes Agent** 适配的 **OpenClaw** 工作区系统。

## 📁 文件结构

```
workspace-hermes/
├── SKILL.md          # 工作区核心指南
├── SOUL.md           # 核心执行规则
├── USER.md           # 用户信息模板
├── IDENTITY.md       # AI 身份定义
├── scripts/
│   ├── hermes-backup.sh    # 备份工具
│   └── hermes-health.sh    # 健康检查
└── README.md
```

## 🚀 快速开始

### 1. 初始化用户信息

编辑 `USER.md` 填入你的信息：
- 名字
- 联系方式
- 偏好和习惯

### 2. 定义 AI 身份

编辑 `IDENTITY.md` 设置 AI 的：
- 名字
- 风格
- Emoji

### 3. 备份配置

```bash
# 创建备份（不推送）
~/.hermes/skills/workspace-hermes/scripts/hermes-backup.sh

# 创建备份并推送到 GitHub
~/.hermes/skills/workspace-hermes/scripts/hermes-backup.sh push
```

### 4. 健康检查

```bash
# 运行健康检查
~/.hermes/skills/workspace-hermes/scripts/hermes-health.sh

# 查看日志
cat /tmp/hermes-health.log
```

## 📋 主要功能

### 消息处理流程
```
收到消息 → 立即回复"收到" → 执行任务 → 汇报结果
```

### 任务执行优先级
1. API 直接调用
2. 已安装的 Skill
3. 搜索社区方案
4. 浏览器自动化（最后手段）

### 内存管理
- **每日笔记**: `memory/YYYY-MM-DD.md`
- **长期记忆**: `MEMORY.md`
- **上下文刷新**: 根据使用率自动管理

## 🔧 与 OpenClaw 的差异

| OpenClaw | Hermes Workspace |
|----------|------------------|
| sessions_spawn | delegate_task |
| openclaw 命令 | hermes 内置工具 |
| 微信插件 | 飞书集成 |
| 自定义 Gateway | Hermes Gateway |

## 📝 移植自 OpenClaw 的脚本

### hermes-backup.sh
- 备份 skills、memories、配置
- 支持推送到 GitHub
- 自动创建 git 提交

### hermes-health.sh
- 检查 Hermes 进程
- 检查日志新鲜度
- 检查 cron 任务
- 检查 skills 安装
- 检查数据库大小

## 💡 使用技巧

### 1. 立即回复
收到消息后**先回复再执行**，这是核心规则。

### 2. 主动汇报
任务完成后**主动汇报结果**，不需要用户追问。

### 3. 写下来
重要信息**写到文件**，不要只靠记忆。

### 4. 子代理并行
复杂任务用 `delegate_task` **并行处理**。

## 📚 参考资料

- OpenClaw 源项目: https://github.com/daxian10086/openclaw-backup
- Hermes Agent: Nous Research

---

_适配版本 v1.0 - 基于 OpenClaw 优化_
