## Ubuntu 24.04 环境配置 (2026-04-12)
- 用户: wdmms123
- 系统: Ubuntu 24.04, tty1终端 + GDM桌面
- Auto-login: 已配置 getty@tty1 --autologin wdmms123 (systemd override)
- Hermes: 已从用户级切换到系统级服务 (sudo systemctl enable/start)

## 平台接入
- 飞书: 已配置 (FEISHU_APP_ID/secret在config.yaml)
- 微信: 支持！通过 iLink Bot API → `hermes gateway setup` → 选择 Weixin
  - 依赖已安装 (aiohttp, cryptography in venv)
  - 方式: 扫码登录，无需公众号
  - 文档: ~/.hermes/hermes-agent/website/docs/user-guide/messaging/weixin.md
§
大仙叫我"小马"🐴
§
股票持仓: 蓝色光标(300058), 浙文互联(600986)
§
股票分析数据源: 腾讯财经(实时) + BaoStock(K线历史)
§
GitHub备份: https://github.com/daxian10086/openclaw-backup (完整记忆和脚本已同步到~/.hermes/)
§
## OpenClaw → Hermes 迁移经验 (2026-04-11)

**教训**：从 OpenClaw 迁移 skills/workspace 时，备份路径是 `/tmp/openclaw-backup/workspace/`，里面已有完整文件。
- 迁移前先检查备份中是否有对应文件
- **不要先创建简化版再替换**，直接用备份完整版
- 记忆文件在 `workspace/memory/`（75个）
- Workspace 核心文件：SOUL.md(388行), AGENTS.md(340行), MEMORY.md(321行), TOOLS.md(49行)
- Skills 在 `workspace/skills/` 下
§
用户股票持仓（2026-04-10）：
- 蓝色光标(sz300058)：现价16.49，止损位MA5(16.28)
- 浙文互联(sh600986)：现价10.34，止损位10.00

定时任务：
- 08:30 财经早报
- 16:00 涨停池采集
- 17:00 龙虎榜数据
- 18:30 市场情绪分析

大仙叫我"小马"🐴
§
## 早报习惯 (2026-04-12)
大仙看早报的格式偏好（经多次纠正后确定）：
1. **今天是周一时**：大盘数据取前一个交易日（周五）收盘；消息面需要4月10日7:30之后的所有消息（4月10日+11日+12日）
2. **今天是周二至周五时**：消息面需要从前一个交易日早上7:30之后开始
3. **颜色标注**：所有市场统一涨🔴跌🟢（所有市场一致，美股/A股/期货全部如此）
4. **消息面要求**：标注发布日期+发布时间，格式[MM月DD日 HH:MM]
5. **内容**：大盘指数、热门板块、连板梯队、美股（纳指/英伟达/特斯拉/阿里/金龙）、期货外盘（原油/贵金属）、详细消息解读、推荐板块和个股
6. **数据源**：腾讯财经(实时)、BaoStock(历史K线)、新浪财经(新闻)、华尔街见闻

定时任务已创建（job_id: d597f107a5c4）：
- 每日早上7:30发送早报（周一至周五）
- 发送至origin（飞书/微信）
§
早报格式偏好更新(2026-04-13)：涨停股池改成连板池(连板梯队)
§
GitHub备份问题(2026-04-13)：push失败 "No such device or address"，token可能有问题。当前remote: https://github.com/daxian10086/hermes-backup.git