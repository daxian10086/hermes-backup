# AI Agent Harness 深度学习笔记

## claw-code 项目 (instructkr)

### 核心信息
- **地址**: https://github.com/instructkr/claude-code
- **Stars**: 126k（2小时达50k，创历史记录）
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

---

## claw-code-haha 项目 (NanmiCoder)

### 核心信息
- **地址**: https://github.com/NanmiCoder/claude-code-haha
- **Stars**: 3.3k
- **语言**: TypeScript 100%
- **本质**: 原始泄露的Claude Code源码，修复后本地可运行

### 两个项目对比
| 项目 | claw-code | claw-code-haha |
|------|-----------|-----------------|
| **性质** | 清洁室重写（Rust/Python） | 原始泄露源码修复版 |
| **语言** | Rust 92.9%, Python 7.1% | TypeScript 100% |
| **Stars** | 126k | 3.3k |
| **目的** | 避免法律风险的合法重写 | 让泄露代码本地可运行 |

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

---

## 对OpenClaw的启发

### 1. 工具设计（Tool Design）
- 工具连接方式比工具本身更重要
- 标准化工具注册和发现流程
- 清晰的tools/commands/skills/services分离

### 2. 上下文管理（Context Management）
- 运行上下文管理决定Agent能力上限
- Session状态、上下文压缩机制
- MCP（Model Context Protocol）协议支持

### 3. 模块化架构
- 更清晰的目录结构分离
- 插件化hook扩展机制
- 降级模式设计（Recovery模式）

### 4. 可立即应用的改进
1. **子代理编排优化**: 参考claw-code的$team模式，并行处理独立任务
2. **上下文压缩**: 当session过长时自动压缩历史
3. **工具注册机制**: 建立标准化的工具注册表
4. **降级模式**: 核心功能损坏时自动切换到简单模式

---

## 关键术语表

| 术语 | 解释 |
|------|------|
| Harness | Agent的运行框架/工具链 |
| Tool Wiring | 工具连接方式 |
| MCP | Model Context Protocol，标准化上下文协议 |
| $team mode | 并行代码审查模式 |
| $ralph mode | 持久执行循环模式 |
| Cleanroom pass | 清洁室审查（命名、QA、发布验证） |
| Recovery CLI | 降级恢复模式 |

---

*创建时间: 2026-04-02*
*来源: instructkr/claude-code + NanmiCoder/claude-code-haha*
