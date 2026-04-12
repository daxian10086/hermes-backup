---
name: wechat-miniprogram-ci-debug
description: 微信小程序 CI/CD 自动上传排障指南 — 解决 GitHub Actions 显示成功但小程序后台没收到更新的问题
tags:
  - github-actions
  - wechat
  - miniprogram
  - ci-cd
  - troubleshooting
---

# 微信小程序 CI/CD 自动上传排障指南

## 症状
GitHub Actions 显示 `success`，但小程序后台没有收到更新。

## 根因
`miniprogram-ci upload` 命令如果私钥无效或上传静默失败，可能只输出版本号（如 `2.1.31`）而不是上传结果。原 workflow 用 `$?` 判断 exit code，但命令本身 exit code 可能是 0（即使上传失败）。

## 排障步骤

### 1. 查看 Action 日志中的实际输出
```
RESPONSE=2.1.31
```
这说明 `npx miniprogram-ci upload` 输出的是版本号，不是上传结果。

### 2. 验证私钥是否有效
```bash
# 本地测试
npx miniprogram-ci upload \
  --appid <your-appid> \
  --privateKeyPath ./private_key.pem \
  --projectPath . \
  --version 1.0.0 \
  --desc 'test'
```
如果私钥无效，微信 API 会返回错误而不是静默失败。

### 3. Secret 可能存在但值为空（最常见根因）
GitHub API 检查 secret 是否就绪：
```bash
curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/USER/REPO/actions/secrets/SECRET_NAME" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Value: {bool(d.get(\"value\"))}, Key ID: {d.get(\"key_id\")}')"
```
- `Value: False, Key ID: None` = **secret 创建了但从未设置内容**（本 session 实际踩的坑）
- `Value: False, Key ID: ...` = 已设置内容，API 不返回明文（正常）
- Workflow 日志中 secret 显示空白（不是 `***`）也说明值为空

**解决方法**：网页端手动设置：仓库 → Settings → Secrets and variables → Actions → 点击 secret → Update → 填入真实值

### 4. workflow 改进（正确的命令参数）
```yaml
- name: Upload to WeChat Mini Program
  run: |
    # 用 printf 避免末尾换行符（echo 会加\n，导致 OpenSSL 解码失败）
    printf '%s' "${WEAPP_PRIVATE_KEY}" > private_key.pem
    
    npx miniprogram-ci upload \
      --appid $WEAPP_APPID \
      --privateKeyPath ./private_key.pem \
      --projectPath . \
      --upload-version "2.4.189" \
      --upload-description "v2.4.189 - CI自动上传" \
      --robot 1
    EXIT_CODE=$?
    echo "Exit code: $EXIT_CODE"
    if [ $EXIT_CODE -ne 0 ]; then
      echo "Upload failed"
      exit 1
    fi
```

**常见错误**：
- `--version` ❌ → 应为 `--upload-version`
- `--desc` ❌ → 应为 `--upload-description`
- 缺少 `--robot 1`

**echo 写私钥失败特征**：日志出现 `error:1E08010C:DECODER routines::unsupported`

### 5. 版本号每次必须递增
微信后台不会重复发布相同版本号，每次 push 都要更新 `deploy.yml` 里的 `--upload-version` 参数。

## 最可靠方案：GitHub Actions Variables（而非 Secrets）

**踩坑经验**：通过 GitHub REST API 加密 secret 时，NaCl/SealedBox 与 GitHub 使用的 libsodium 加密不兼容，导致 secret 始终为空（`key_id: null`），即使 API 返回 204 成功。

**解决方案**：改用 GitHub Actions Variables 存储 base64 编码的私钥，无需加密。

### 设置步骤

**Step 1. 本地 base64 编码私钥**
```bash
cat private.key | base64 -w0
```

**Step 2. 通过 API 创建 Variables（无需加密）**
```python
import requests
token = "ghp_xxx"
repo = "owner/repo"

# 创建 WEAPP_APPID 变量
requests.post(
    f"https://api.github.com/repos/{repo}/actions/variables",
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"},
    json={"name": "WEAPP_APPID", "value": "wx1234567890"}
)

# 创建 base64 编码的私钥变量
b64_key = open("private.key").read().encode()
import base64
b64 = base64.b64encode(b64_key).decode()

requests.post(
    f"https://api.github.com/repos/{repo}/actions/variables",
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"},
    json={"name": "WEAPP_PRIVATE_KEY_B64", "value": b64}
)
```

**Step 3. Workflow 配置（Variables 版本）**
```yaml
- name: Save private key
  run: |
    echo "${{ vars.WEAPP_PRIVATE_KEY_B64 }}" | base64 -d > private_key.pem

- name: Upload to WeChat Mini Program
  env:
    WEAPP_APPID: ${{ vars.WEAPP_APPID }}
  run: |
    npx miniprogram-ci upload \
      --appid $WEAPP_APPID \
      --projectPath . \
      --privateKeyPath ./private_key.pem \
      --upload-version "2.4.189" \
      --upload-description "v2.4.189 - CI自动上传" \
      --robot 1
```

**为什么不用 Secrets**：
- GitHub Secrets 加密需要用 libsodium sealed box，NaCl Python 库的 SealedBox 与 GitHub 实现的加密结果不兼容
- API 返回 204 成功，但 GitHub 实际无法解密，导致 secret 值为空
- Variables 明文存储，但私有仓库安全，且可以通过 base64 间接存储任意内容

## 相关文件
- `.github/workflows/deploy.yml` — GitHub Actions 部署配置
- `app.json` — 小程序版本号配置
- Variables: `WEAPP_APPID`, `WEAPP_PRIVATE_KEY_B64`（替代 Secrets）

### app.json 的 pages 列表必须与实际目录结构完全匹配（重要！）

**常见失败**：`miniprogram-ci upload` 时报错找不到某个 `.wxml` 文件，例如：
```
pages/divination/divination.wxml not found
pages/history/history.wxml not found
```

**原因**：上传时微信检查 `app.json` 里 `pages` 数组中列出的每个路径，如果文件不存在就失败。

**解决方法**：修改 `app.json` 前，先查清楚实际存在的页面目录：
```bash
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/contents/pages" \
  | python3 -c "import json,sys; [print(i['name']) for i in json.load(sys.stdin)]"
```
只列出实际存在的页面，如 `["pages/index/index", "pages/query/query", "pages/result/result"]`。

### git pull --rebase 在 workflow 中失败（重要！）

**失败症状**：
```
git pull --rebase origin main
  -> error: cannot pull with rebase: you have unstaged changes
  -> fatal: could not execute git pull
```

**原因**：workflow 前面步骤（sed）修改了 `version.txt`，但修改未被 staged。此时 `git pull --rebase` 会因为存在未暂存更改而拒绝执行。

**解决方法**：移除 `git pull --rebase`，直接提交即可：
```yaml
- name: Commit and push
  run: |
    git config --global user.name "github-actions[bot]"
    git config --global user.email "github-actions[bot]@users.noreply.github.com"
    git add -A
    git diff --cached --quiet || git commit -m "ci: update version"
    git push --force origin main
```

**核心原则**：不要在 workflow 里同时做 `git pull` 和修改同一个文件（version.txt）的操作。

### 批量更新多个文件时，每次都要重新获取 SHA

当通过 GitHub API 连续更新多个文件时（如一次更新 version.txt、app.json、index.js 三个文件），每个 PUT 请求都需要提供文件当前的 SHA。由于 API 提交是串行的，每次成功提交后 HEAD 都会前移，所以必须在每次更新前重新获取最新 SHA，否则后续文件会报 409 Conflict 错误。

正确做法（串行更新时）：
```python
sha_v = get_sha("version.txt")      # 立即使用
update_file("version.txt", ...)
sha_app = get_sha("app.json")       # 每次更新前重新获取
update_file("app.json", ...)
sha_js = get_sha("pages/index/index.js")  # 同上
update_file("pages/index/index.js", ...)
```

## Workflow 失败排查流程（重要补充）

### Step 1: 确认哪个 step 失败了
```python
import requests
TOKEN = "ghp_xxx"
REPO = "owner/repo"

# 获取最新的 run
r = requests.get(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=1",
    headers={"Authorization": f"token {TOKEN}"})
run_id = r.json()["workflow_runs"][0]["id"]

# 获取 job 详情和所有 step 的结果
r = requests.get(f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/jobs",
    headers={"Authorization": f"token {TOKEN}"})
for job in r.json()["jobs"]:
    for step in job["steps"]:
        if step["conclusion"] not in (None, "success"):
            print(f"FAIL: {step['name']}: {step['conclusion']}")
```

### Step 2: 下载并读取日志
```bash
# 下载日志zip（整个workflow的日志）
curl -L -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs" \
  -o /tmp/logs.zip

# 解压后日志命名规则：
# {job_name}/{step_number}_{step_name}.txt
# 例如：deploy/9_Upload to WeChat Mini Program.txt
unzip -o /tmp/logs.zip -d /tmp/logs
cat "/tmp/logs/deploy/11_Commit and push.txt"
```

### Step 3: 常见失败模式
| Step 失败 | 原因 | 解决方法 |
|-----------|------|---------|
| Upload to WeChat | app.json pages 列表错误 | 见上方"app.json pages 列表"章节 |
| Commit and push | git pull --rebase 有未暂存文件 | 移除 --rebase，直接 push |
| Post Setup Node.js | 上游步骤失败被跳过 | 先解决上游问题 |
| 整个 run 显示 failure 但 upload 实际成功 | commit/push 步骤失败 | 查日志确认是哪个 step |

### 关键经验：微信已上传但 GitHub push 失败的情况
如果日志显示 "Upload completed successfully" 但整个 run 仍然 failure，说明微信上传成功了，只是 git push 步骤失败。这时：
1. 微信后台已经有新版本了
2. 需要修复 deploy.yml 后重新 push
3. 不要再手动触发 workflow（否则 version.txt 会再次递增）

## 当 git push 失败时的备选方案：GitHub API 更新文件

如果 SSH/HTTPS 推送失败（如网络超时），可用 GitHub REST API 直接更新文件：

```bash
# 1. 获取目标文件的 SHA
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/{owner}/{repo}/contents/{path}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['sha'])"

# 2. 用 base64 编码文件内容并推送
CONTENT_B64=$(cat file.json | base64 -w0)
curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"更新说明\",
    \"sha\": \"\$FILE_SHA\",
    \"content\": \"\$CONTENT_B64\"
  }" \
  "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
```

适用场景：修改 `deploy.yml` 版本号、`app.json` 版本号等小改动，无需 clone 整个仓库。
