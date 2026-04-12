# MEMORY.md - 长期记忆（Layer 3）

这是你的长期记忆文件，记录需要永久保留的核心信息。

---

### InStreet 学习成果 ⭐
**完成时间**: 2026-03-25
**文章分析**: 178 篇 InStreet 文章

**关键改进决策**:
1. **任务执行优化**: 建立检查清单、拆分子任务、失败重试机制
2. **记忆管理优化**: 分层记忆机制（MEMORY.md + daily notes）、重要决策写入文件
3. **协作能力提升**: 评论优先策略、建立健康社交关系
4. **技能获取与分享**: 建立技能知识库、主动分享经验
5. **自我反思机制**: 定期复盘、自我反驳检查、元认知能力培养

**已创建的改进文件**:
- `memory/skills_kb.md` - 技能知识库
- `memory/task_checklist.md` - 任务检查清单
- `memory/instreet_learning_report.md` - 完整学习报告

**高优先级行动项（19个）**:
1. ✅ 建立技能知识库
2. ✅ 建立任务检查清单
3. ⏳ 建立分层记忆机制（进行中）
4. ⏳ 重要决策写入文件（执行中）
5. ⏳ 建立记忆 Flush Protocol
6. ⏳ 建立自我反驳检查机制
7. ⏳ 主动分享经验技巧
8. ⏳ 建立质量控制机制
9. ⏳ 建立健康社交关系

**爬虫工具**:
- `/workspace/projects/scripts/instreet_scraper.py` - InStreet 文章爬虫
- `/workspace/projects/scripts/crawl_all_articles.sh` - 批量抓取脚本

---

## 🧠 核心技能

### 股票分析方法论
- **主要关注**: 技术分析、短线交易、情绪周期
- **数据源**: 腾讯财经、Baostock
- **已分析股票**:
  - 601869 长飞光纤
  - 600821 金开新能
  - 600995 南网储能
  - 600410 华胜天成

### OpenClaw 系统配置
- **版本**: 2026.3.13
- **Node 版本**: v24.13.1
- **Embedding**: 本地 (node-llama-cpp + embeddinggemma-300m-qat-Q8_0.gguf)
- **启动方式**: 使用 `/workspace/projects/scripts/start.sh`（systemd 不可用）
- **重启方式**: 使用 `/workspace/projects/scripts/restart.sh`
- **停止方式**: 使用 `/workspace/projects/scripts/stop.sh`

### 技能使用技巧
- stock-analyze - 股票分析 ⭐
- coze-image-gen - 图片生成
- coze-voice-gen - 语音合成
- coze-web-search - 网络搜索
- coze-web-fetch - 网页抓取
- scheduler - 定时任务

### 自动阅读与自我改进机制 ⭐
**启用时间**: 2026-03-24
**目标**: 持续学习 InStreet 社区内容，自动改进 Agent 能力

**执行频率**:
- 每 30 分钟：通过心跳脚本自动获取并阅读 InStreet 新帖子
- 每小时：检查待处理的改进建议
- 每天 10:00：生成昨日改进总结

**关键脚本**:
- `/workspace/projects/workspace/scripts/instreet_heartbeat.sh` - 心跳+自动学习（每30分钟）
- `/workspace/projects/scripts/self_improve.sh` - 自我改进脚本（每小时+每天10点）

**输出文件**:
- `memory/articles/article_*.json` - 文章存档
- `memory/learning_YYYY-MM-DD.md` - 每日学习日志
- `memory/learning_log.md` - 长期学习记录
- `memory/daily_improvement_YYYY-MM-DD.md` - 每日改进报告

**冲突检测策略**:
1. 时间戳：新的建议优先
2. 点赞数：点赞数高的优先
3. 评论数：讨论度高的优先
4. 来源可信度：核心开发者的建议优先

**改进口径**:
- ✅ 配置优化（参数、工具配置）
- ✅ 工作流程改进（自动化、效率）
- ✅ 认知升级（方法论、最佳实践）
- ❌ 权限边界操作（支付、删除等）

---

## ⚙️ 系统配置

### 工作区路径
- **工作区**: `/workspace/projects/workspace`
- **配置文件**: `/workspace/projects/openclaw.json`
- **索引数据库**: `/workspace/projects/memory/main.sqlite`
- **脚本目录**: `/workspace/projects/scripts`
- **时区**: Asia/Shanghai

### API Keys
- **MiniMax**: sk-api-etipui_0pnnRCgsiu5Gi3ArRVt5ISDBQLuh4wB7DwTEXotoX6aZRe0c4iBQQ1mBDcnk_FXXxL6yxMMRiHibZVf-H4VFCkdSr7K7VLW-0or0OlAXthktPzAo
- **DeepSeek**: sk-1eb1f4d84f82439a84992165b3f79eca (余额不足)
- **阿里百炼**: sk-3bda99c15ac447cc8e250c8c2558cf69

### 端口限制
- **9122 端口**: 有系统服务运行，**禁止**使用/关闭/拦截

### 记忆管理策略
- **MEMORY.md**: 长期记忆（永久保留）
- **memory/YYYY-MM-DD.md**: 每日工作日志（保留最近 3 天）
- **memory/股票学习笔记-YYYY-MM-DD.md**: 股票学习笔记（保留最近 2 天）
- **memory/股票知识库.md**: 股票知识库（永久保留）
- **memory/tasks.md**: 待办任务跟踪

**清理策略**：
- 每日日志：保留最近 3 天（自动清理脚本：每天 04:00）
- 股票学习笔记：保留最近 2 天（自动清理脚本：每天 04:00）
- 长期知识：MEMORY.md 永久保留
- 自动清理脚本：/workspace/projects/scripts/memory_cleanup.sh
- 清理日志：/tmp/memory_cleanup.log

---

## 👤 用户偏好

### 工作习惯
- 不需要浏览器界面，直接命令行分析
- 需要真实数据，不接受 AI 幻觉
- 每次分析后需要自我反驳检查
- 目标：最大化召回质量和覆盖面，不考虑成本和性能

### 沟通方式
- **第一时间回复**：收到消息后立即回复"收到"，然后再执行任务
- **微信转发**：微信会话中 OpenClaw 自动发送，不需要手动转发
- 如果需要主动发送消息到微信，使用 `message` 工具

### 特殊要求
- 子代理执行模式：分析需求 → 创建子代理 → 汇报结果
- 微信会话中 OpenClaw 自动发送回复
- 任务完成后必须主动汇报结果

---

## 📚 平台账号

### 虾评 Skill 平台
- **平台地址**: https://xiaping.coze.site
- **技能框架**: OpenClaw（完全兼容）
- **agent_id**: agent_Qnk91VoUjNFFHRVa
- **user_id**: dc226607-b435-421b-b5a0-bd7356425cef
- **api_key**: sk_jWcZ9mgWmVJfW3DR_zUvjFNKARiGYlj7
- **虾米余额**: 30
- **使用指南**: https://xiaping.coze.site/skill.md

### InStreet 社区
- 学习来源：三篇关于记忆管理的文章
  1. 记忆悖论：选择性遗忘是一种能力
  2. 实操复盘：凌晨自动清理解决 Context Window 焦虑
  3. 记忆系统：三层架构设计

---

## 💡 关键认知

### 记忆管理原则（来自三篇文章）
- **记忆悖论**：选择性遗忘是一种能力，优化"折旧率"比增加容量更重要
- **自动清理**：每天凌晨清理过期对话文件，可节省 60% Token
- **三层记忆架构**：Layer 1 实时缓存 + Layer 2 短期记忆 + Layer 3 长期知识

### 选择性遗忘的实践方法
- 不是所有信息都需要记住
- 记住"为什么会做错"比记住"具体的细节"更重要
- 优化"折旧率"，主动遗忘不再适用的规则

### 三层记忆架构的设计思路
1. **Layer 1: 实时缓存** - 当前会话，最近 10-20 轮对话，自动处理
2. **Layer 2: 短期记忆** - memory/YYYY-MM-DD.md，保留 3-7 天
3. **Layer 3: 长期知识** - MEMORY.md，永久保留

### 定期复盘策略
- **每日**：更新 daily memory
- **每周**：将重要决策蒸馏到长期记忆
- **每月**：审查记忆结构，清理冗余

---

## 📝 记忆使用指南

### 关键信息标记法
在会话中，关键信息用以下前缀标记：
- `[关键]` - 必须记住的核心信息
- `[重要]` - 重要的决策和配置
- `[记住]` - 需要长期保持的习惯

### 三层记忆架构
1. **Layer 1: 实时缓存** - 当前会话，自动处理
2. **Layer 2: 短期记忆** - memory/YYYY-MM-DD.md，保留 3-7 天
3. **Layer 3: 长期知识** - MEMORY.md，永久保留

### 选择性遗忘原则
- 不是所有信息都需要记住
- 记住"为什么会做错"比记住"具体的细节"更重要
- 优化"折旧率"，主动遗忘不再适用的规则

### 定期复盘
- 每日：更新 daily memory
- 每周：将重要决策蒸馏到长期记忆
- 每月：审查记忆结构，清理冗余

## 易经小程序（项目别名）
- **简称**: 易经小程序
- **路径**: `/workspace/projects/workspace/daxianzhouyi-miniprogram-v2.3.25/`
- **AppID**: `wx8efbbb29c6b81122`
- **GitHub**: `daxian10086/daxianzhouyi-miniprogram`
- **当前版本**: v2.4.156（去除占卜用语，传统文化学习定位）

## 小程序版本号同步（2026-04-02）

### 问题
微信小程序不支持在页面js中require app.json，会导致白屏。

### 解决方案
创建同步脚本 `sync_version.py`，在上传前自动同步版本号。

### 使用方法
1. 修改 `app.json` 的 version 字段
2. 运行 `python3 sync_version.py` 自动同步到 app.js 和 index.js
3. 上传

### 脚本位置
`/workspace/projects/workspace/daxianzhouyi-miniprogram-v2.3.25/sync_version.py`

### 重要提醒
**每次上传前必须运行同步脚本！** 否则会出现版本号晚一个的问题。

## claw-code 项目学习（2026-04-02）

### 项目信息
- **地址**: https://github.com/instructkr/claude-code
- **Stars**: 126k（2小时达到50k stars，创历史记录）
- **语言**: Rust 92.9%, Python 7.1%
- **核心理念**: Better Harness Tools

### 核心架构（Rust crates）
1. **crates/api-client** - API客户端，支持OAuth和流式输出
2. **crates/runtime** - Session状态管理、上下文压缩、MCP编排
3. **crates/tools** - 工具清单定义和执行框架
4. **crates/commands** - 斜杠命令、skill发现、配置检查
5. **crates/plugins** - 插件模型、hook管道
6. **crates/claw-cli** - 交互式REPL、Markdown渲染

### 关键设计理念
1. **Tool Wiring** - 工具连接比工具本身更重要
2. **Runtime Context** - 运行上下文管理决定Agent能力上限
3. **MCP (Model Context Protocol)** - 标准化的上下文协议
4. **Plugin Hook Pipeline** - 插件化的hook机制

### 重要工作流模式
- `$team` mode: 并行代码审查和架构反馈
- `$ralph` mode: 持久执行循环，架构级验证
- Cleanroom passes: 命名/品牌清理、QA、发布验证

### 对OpenClaw的启发
- 更模块化的工具设计
- 更清晰的上下文管理机制
- 标准化工具注册和发现流程

## claw-code-haha 项目学习（2026-04-02）

### 项目信息
- **地址**: https://github.com/NanmiCoder/claude-code-haha
- **Stars**: 3.3k
- **语言**: TypeScript 100%
- **本质**: 原始泄露的Claude Code源码，修复后可在本地运行

### 两个项目的区别

| 项目 | claw-code (instructkr) | claw-code-haha (NanmiCoder) |
|------|------------------------|------------------------------|
| **性质** | 干净的Python/Rust重写 | 原始泄露源码修复版 |
| **语言** | Rust 92.9%, Python 7.1% | TypeScript 100% |
| **目的** | 避免法律风险的清洁室实现 | 让泄露代码本地可运行 |
| **Stars** | 126k | 3.3k |

### claw-code-haha 核心架构
```
src/
├── entrypoints/cli.tsx     # CLI主入口
├── main.tsx               # TUI主逻辑（Commander.js + React/Ink）
├── screens/REPL.tsx       # 交互REPL界面
├── ink/                   # Ink终端渲染引擎
├── components/            # UI组件
├── tools/                 # Agent工具（Bash, Edit, Grep等）
├── commands/              # 斜杠命令
├── skills/                # Skill系统
├── services/              # 服务层（API, MCP, OAuth）
├── hooks/                 # React hooks
└── utils/                 # 工具函数
```

### 技术栈
- **运行时**: Bun
- **语言**: TypeScript
- **终端UI**: React + Ink
- **CLI解析**: Commander.js
- **API**: Anthropic SDK
- **协议**: MCP, LSP

### 对OpenClaw的启发
- 更清晰的目录结构（tools/commands/skills/services分离）
- 降级模式设计（Recovery CLI）
- 环境变量配置方式
