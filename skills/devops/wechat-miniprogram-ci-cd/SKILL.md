---
name: 微信小程序 CI/CD 自动上传
description: GitHub Actions 自动将代码上传到微信小程序后台，支持 version.txt 版本号管理
category: devops
---

# 微信小程序 CI/CD 自动上传

## 背景
通过 GitHub Actions 将代码 push 到 main 分支后，自动完成：
1. 更新版本号（app.json + index.js）
2. 上传到微信小程序后台
3. GitHub 提交版本号更新
4. version.txt 自动递增

## 核心文件（三个都要同步版本号）
- `.github/workflows/deploy.yml` — 部署 workflow
- `version.txt` — 当前版本号（如 `188`）
- `app.json` — 小程序配置，version 字段
- `pages/index/index.js` — 首页 JS，version 字段
- `app.js` — 全局数据，globalData.version 字段（**容易遗漏！**）

## 版本号规范
- 微信后台格式：`2.4.190`（三位数）
- GitHub 存储在 `version.txt`（纯数字，如 `190`）
- 代码内显示格式：`v2.4.190`
- **app.js 里的 globalData.version 是用户看到的版本号，必须同步更新！**

## Workflow 结构
```yaml
jobs:
  deploy:
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          persist-credentials: true
          fetch-depth: 0

      # 1. 读取当前版本
      - name: Read current version
        id: version
        run: |
          CURRENT_VER=$(cat version.txt)
          echo "current_ver=$CURRENT_VER" >> $GITHUB_OUTPUT

      # 2. 更新 app.json 版本号
      - name: Update app.json version
        run: |
          VERSION="2.4.${{ steps.version.outputs.current_ver }}"
          sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"v${VERSION}\"/" app.json
          sed -i "s/\"versionDate\": \"[^\"]*\"/\"versionDate\": \"$(date +%Y-%m-%d)\"/" app.json

      # 3. 更新 index.js 版本号
      - name: Update index.js version
        run: |
          VERSION="2.4.${{ steps.version.outputs.current_ver }}"
          sed -i "s/version: 'v[^']*'/version: 'v${VERSION}'/" pages/index/index.js

      # 4. 更新 app.js 版本号（容易遗漏！导致用户看到旧版本号）
      - name: Update app.js version
        run: |
          VERSION="2.4.${{ steps.version.outputs.current_ver }}"
          sed -i "s/version: 'v[^']*'/version: 'v${VERSION}'/" app.js
          sed -i "s/versionDate: '[^']*'/versionDate: '$(date +%Y-%m-%d)'/" app.js

      # 5. 上传到微信（版本冲突不失败，继续后续步骤）
      - name: Upload to WeChat Mini Program
        run: |
          VERSION="2.4.${{ steps.version.outputs.current_ver }}"
          npx miniprogram-ci upload \
            --appid $WEAPP_APPID \
            --projectPath . \
            --privateKeyPath ./private_key.pem \
            --upload-version "${VERSION}" \
            --upload-description "v${VERSION} - CI自动上传" \
            --robot 1
          EXIT_CODE=$?
          if [ $EXIT_CODE -eq 0 ]; then
            echo "upload_status=success" >> $GITHUB_OUTPUT
          else
            # 版本号冲突（微信已存在该版本）不算失败
            echo "upload_status=skipped" >> $GITHUB_OUTPUT
          fi

      # 6. 递增 version.txt 并 push
      - name: Increment version
        run: |
          CURRENT_VER=$(cat version.txt)
          NEW_VER=$((CURRENT_VER + 1))
          echo $NEW_VER > version.txt

      - name: Commit and push
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git diff --cached --quiet || git commit -m "ci: 版本号更新 to 2.4.${{ steps.version.outputs.current_ver }}"
          git push --force origin main
```

**关键经验**：
- sed 替换 `versionDate` 时要确保只匹配一行，否则可能出现 `'2026-04-12'2026-04-12'` 双重日期
- 版本号冲突（微信 code 20003）时不要让 workflow 整体失败，否则 version.txt 无法递增
- app.js 的 globalData.version 是小程序里用户看到的版本，必须同步更新

## GitHub 配置
需要提前设置两个 Variables：
- `WEAPP_APPID`：小程序 AppID（如 `wx8efbbb29c6b81122`）
- `WEAPP_PRIVATE_KEY_B64`：私钥 base64 编码（不用 Secrets 因为加密会失败）

```bash
# 设置 Variable
curl -X POST -H "Authorization: token ghp_XXX" \
  -H "Content-Type: application/json" \
  -d '{"name": "WEAPP_APPID", "value": "wx..."}' \
  "https://api.github.com/repos/USER/REPO/actions/variables"

# 私钥转 base64
cat private_key.pem | base64 -w0
```

## 常见错误

### app.json pages 路径不存在
错误：`could not find the corresponding file: "pages/divination/divination.wxml"`
解决：确保 app.json 的 pages 数组中的路径真实存在于仓库中，先用 `GET /repos/USER/REPO/contents/pages` 确认实际目录结构。

### git pull --rebase 失败
错误：`cannot pull with rebase: You have unstaged changes`
解决：去掉 `git pull --rebase`，用 `git push --force` 直接覆盖，因为 workflow 每次都是全新 checkout。

### 微信上传参数错误
错误：未知参数 `--version` `--desc`
解决：正确的参数是 `--upload-version` 和 `--upload-description`。

### app.js 版本号不同步（用户看到旧版本号）
表现：app.json 已更新到新版本，但小程序主界面显示的版本号还是旧的。
原因：app.js 里的 `globalData.version` 是默认值，微信会缓存。小程序启动时读取 app.js 的 globalData 作为版本号。
解决：workflow 里也要同时更新 app.js 的 globalData.version 和 globalData.versionDate。

### sed 双重替换导致日期变成 `'2026-04-12'2026-04-12'`
原因：sed 模式匹配到了多行，或者匹配范围太大。
表现：微信编译器报错 `Unexpected token, expected "," (84:29)`，app.js 第84行 versionDate 字段有两个日期。
解决：用精确的 sed 模式，确保只匹配一行一次。最好用 Python 脚本做字符串替换。

### 版本号冲突（微信已存在该版本）
错误：`code: 20003`
原因：同一个版本号被重复上传（workflow 失败后重试，或代码没变化但手动触发了两次）。
解决：workflow 里用 `exit 0` 而非 `exit 1`，让失败后 version.txt 仍能递增。版本号本身是自增的，冲突不影响大局。

### 版本号一直停在某个数字不推进
原因：通常是 workflow 某次上传失败后整体失败，导致 git commit 和 version.txt 递增那两步没执行。
解决：先手动确认 version.txt 值，然后重新触发 workflow。
