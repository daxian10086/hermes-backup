---
name: feishu-bot
description: Connect a Feishu (飞书) bot with official event-driven architecture using WebSocket event subscription. Includes token获取, message sending, and official documentation references.
version: 1.0.0
author: community
license: MIT
metadata:
  hermes:
    tags: [Feishu, 飞书, Bot, Webhook, Event]
    homepage: https://open.feishu.cn
prerequisites:
  commands: [curl]
---

# Feishu Bot Development

Connect a Feishu (飞书) bot with official event-driven architecture.

## Architecture (Official)

**Do NOT use polling** - Feishu uses WebSocket event subscription (Persistent Connection).

```
User sends message → Feishu Server → WebSocket push to your server → Bot replies
```

### Key Components

1. **Event Subscription**: `im.message.receive_v1` - receives messages
2. **Connection Type**: Persistent connection (WebSocket)
3. **Reply APIs**:
   - Private chat (p2p): Send message API
   - Group chat: Reply to message using `message_id`

### Required Permissions
- `im:message.p2p_msg:readonly` - Read direct messages to bot
- `im:message:send_as_bot` - Send messages as app
- `im:message.group_at_msg:readonly` - Read group @mentions

## Official Documentation
- Tutorial: https://open.feishu.cn/document/develop-an-echo-bot/introduction
- Implementation: https://open.feishu.cn/document/develop-an-echo-bot/development-steps
- FAQ: https://open.feishu.cn/document/develop-an-echo-bot/faq

## Token获取

```bash
curl -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}'
```

Response:
```json
{"code":0,"expire":7200,"msg":"ok","tenant_access_token":"t-xxx"}
```

## Send Message

```bash
curl -X POST 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "receive_id": "oc_xxx",
    "msg_type": "text",
    "content": "{\"text\":\"Hello\"}"
  }'
```

## Get Messages (for debugging)

```bash
curl -X GET 'https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=chat&container_id=oc_xxx&page_size=10' \
  -H 'Authorization: Bearer <token>'
```

## Get Bot Info

```bash
curl -X GET 'https://open.feishu.cn/open-apis/bot/v3/info' \
  -H 'Authorization: Bearer <token>'
```

## Get Chat List

```bash
curl -X GET 'https://open.feishu.cn/open-apis/im/v1/chats' \
  -H 'Authorization: Bearer <token>'
```

## Pitfalls

- Long-polling does NOT work reliably for receiving messages
- Must use WebSocket persistent connection for production
- App must be published (not just in test mode) for event subscription to work
- Token expires ~2 hours, cache and refresh it

## Known Working Credentials (for reference)

- App ID: `cli_a953503d09789bd2`
- Bot Name: hermes
- Bot Open ID: `ou_bea8a12b36d05d33e77b5136dd1524f2`