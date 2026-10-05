# SpeakLog 静态网站

这是独立于原生应用的公开产品网站。源文件在 `website/`，没有前端构建依赖。生产域名为 <https://speak.erzhiqian.cc>，Cloudflare Pages 项目为 `speaklog`。

## 页面与多语言

共有 15 个可索引页面，每个主题都有中文、英文和日文版本：

| 主题 | 中文 | English | 日本語 |
|---|---|---|---|
| 首页 | `/` | `/en/` | `/ja/` |
| 开始使用 | `/guides/getting-started/` | `/en/guides/getting-started/` | `/ja/guides/getting-started/` |
| 口语练习 | `/guides/speaking-practice/` | `/en/guides/speaking-practice/` | `/ja/guides/speaking-practice/` |
| 导出 | `/guides/export/` | `/en/guides/export/` | `/ja/guides/export/` |
| 隐私 | `/privacy/` | `/en/privacy/` | `/ja/privacy/` |

- 每页有自己的 canonical、标题、描述和 `og:url`
- `hreflang` 和语言切换都指向**同一主题**的三个语言版本；`x-default` 指向该主题的英文页面
- 不按浏览器语言自动跳转；`404.html` 使用 `noindex`，托管层必须给不存在的路径返回 HTTP 404
- `sitemap.xml` 覆盖所有 15 页，并包含各页的对应语言和更新时间
- 首页的 `SoftwareApplication.softwareVersion`、所有首页/指南的 `data-version` 属性和显示版本应一致，三种语言同时更新
- FAQ 的 JSON-LD 问题与答案必须和可见内容一致。社交分享图不是应用截图，不要写入 `screenshot`

添加新主题或语言时，同时更新页面、导航、sitemap 和 `scripts/validate_website.py` 中的 `TOPICS` / `LANGUAGES`。发布文件采用明确的允许列表，未登记的页面不会自动上线。

## 环境与本地验证

需要 Python 3.10+ 和 Node.js 22+。验证只使用标准库，不运行 npm install，不联网，不发送分析事件。

从仓库根目录运行：

```bash
# 完整检查：页面契约、Python 回归测试、JS 行为测试和语法检查
scripts/check_website.sh

# 单独检查内容；也可传入构建后的目录
python3 scripts/validate_website.py website

# 单独运行回归测试，不生成 __pycache__
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/site-behavior.test.cjs

# 安全默认：完整检查 + 临时发布构建；不调用 Wrangler，不上传
website/deploy.sh
# 与默认相同
website/deploy.sh --dry-run
```

自动化覆盖：

- 15 个 canonical、HTML 语言、同主题 hreflang 互链和语言切换
- 本地链接、静态资源、片段锚点、重复 ID、404 noindex
- FAQ 可见文字与结构化数据一致；禁止把 OG 图标为应用截图
- 三语软件版本以及显示版本一致；安装包与发布页分析事件分开
- sitemap 覆盖范围、alternate 对应、lastmod 日期、robots 和 manifest 图标
- JS 在分析脚本缺失或报错、非元素点击、FAQ 关闭、示例元素不完整时安全运行
- 减少动态效果偏好、隐藏标签页暂停、动画单次播放在四秒活动时间内停止；本地/预览域名不加载 GA
- 构建不带内部文件，拒绝符号链接和非空输出目录；本地 HTTP smoke 测试

`.github/workflows/website-validation.yml` 在相关 push、pull request 和手动触发时做同样的 dry run。它只有只读仓库权限，不含 Cloudflare 凭据和部署任务。

## 构建与预览

不要直接上传整个 `website/`。使用公共文件允许列表生成独立目录：

```bash
OUT=$(mktemp -d)
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_website.py "$OUT"
python3 scripts/validate_website.py "$OUT"
python3 -m http.server 8765 --directory "$OUT"
# 停止预览后自行删除这个临时目录
```

构建会复制已登记的页面、`404.html`、robots、sitemap、manifest、可选 `_headers` / `_redirects`、两个公开 JS、CSS 和图片/字体/视频等资源。README、部署脚本、Swift 生成器、内部 JS、source map、隐藏文件及仓库目录不会进入输出。输出必须是新的或空目录，脚本不会清理已有文件。

Python HTTP 服务器足够本地预览，但不模拟 Cloudflare 自定义 404 文案、重定向或响应头配置。

## 自动生产部署

`.github/workflows/deploy-pages.yml` 在 `main` 的 `website/`、`scripts/`、`tests/` 或部署工作流变更时自动发布，也支持在 GitHub Actions 中手动运行（仅允许 `main`）。

仓库 Actions Secrets 必须配置 `CLOUDFLARE_API_TOKEN`（目标账户的 Cloudflare Pages Edit 权限）和 `CLOUDFLARE_ACCOUNT_ID`。不要放在 Actions Variables 中。

工作流执行 `website/deploy.sh --production`：先通过全部验证和测试，再发布到现有 `speaklog` Pages 项目，最后对 `https://speak.erzhiqian.cc` 执行逐文件 smoke 检查。生产部署串行执行；原有 Website validation 工作流仍只做离线验证。

## 手动生产部署

只有显式传入 `--production` 才会上传。生产部署要求：

1. 所有检查通过
2. 当前分支为 `main`，工作区干净，包括没有未跟踪文件；准备发布的代码已审阅并提交
3. 本地有 npm，并已拥有获准使用的 Cloudflare 登录或最小范围部署凭据；脚本不会替你创建凭据或改变权限
4. 确认要发布到项目 `speaklog` 的生产分支 `main`

Wrangler 固定为 `4.147.0`，版本记录在 `scripts/wrangler-version.txt`，不使用会漂移的 `@4` 或 `@latest`。该版本已通过 npm registry 核实，要求 Node >=22。工具信息：[Cloudflare 官方发布记录](https://github.com/cloudflare/workers-sdk/releases/tag/wrangler%404.147.0)。更新时明确修改版本文件并重新验证。首次显式部署会由 npm 解析和下载该固定版本及其依赖；普通验证不会下载它。

```bash
# 仅在明确决定发布后执行
website/deploy.sh --production
```

脚本在提供 Token 和 Account ID 时直接使用 Pages 接口认证；本地登录模式先执行只读 `wrangler whoami`。随后上传允许列表构建，并记录当前 Git commit。它不会自动登录、提交、推送、部署预览或更改 Cloudflare 设置。不要将 `--production` 加入验证 CI。若 Git 集成在 Cloudflare 控制台另有自动部署设置，本仓库不会替你改变它；发布前需自行确认。

## 部署后只读检查

部署完成后，先用 Wrangler 返回的实际部署 URL 检查，再检查生产域名：

```bash
python3 scripts/smoke_website.py --base-url https://<deployment>.speaklog.pages.dev
python3 scripts/smoke_website.py --base-url https://speak.erzhiqian.cc
```

smoke 脚本只发送 GET 请求，不执行网页 JS、不上传文件。它将公开文件与当前 checkout 逐字节比较、检查主要 Content-Type，并确认根路径及英语/日语 guides 下随机不存在的路径确实返回 HTTP 404。字节不符可表示部署版本错误或缓存未更新；先确认所查 URL 与 commit 再处理。检查默认每个请求超时 15 秒，可用 `--timeout 30` 调整。必须显式指定目标地址，生产检查不会被默认运行。

## 分析事件

GA4 ID 只在 `assets/analytics.js` 配置。仅 `speak.erzhiqian.cc` 加载远程 GA 脚本，localhost、Cloudflare 预览域名和备用域名不会进入生产页面浏览统计。拦截 GA 不应影响导航或 FAQ。事件包含 `page_language`：

| 事件 | 触发 | 主要参数 |
|---|---|---|
| `cta_click` | 页内主要行动链接 | `location`、`link_text` |
| `package_download_click` | 直接下载 PKG 安装包 | `location`、`link_text` |
| `release_page_click` | 打开 GitHub 发布页/历史版本 | `location`、`link_text` |
| `language_switch` | 语言切换 | `location`、`link_text` |
| `guide_click` | 打开使用指南 | `location`、`link_text` |
| `faq_open` | 展开 FAQ | `question` |
| `page_not_found` | 打开 404 页 | `path` |

不要重新把安装包和发布页合并成 `download_click`。点击事件衡量点击意图，不证明安装或下载完成。GA 隐私/同意方案需要根据实际服务地区另行评估；这里没有新增同意横幅或更改账户设置。

## 更新资源

共享资源为 `assets/site.css`、`assets/site.js`、`assets/analytics.js`。修改后同步提高所有页面的对应 `?v=` 缓存版本，包含 404 和指南/隐私页。修改可索引页面时更新 sitemap 的实际 `lastmod`。

社交图片仍可以用已有 Swift 生成器重新生成：

```bash
swift website/make-og.swift <应用源码仓库>/build/icon-1024.png website/assets
```

该生成器只在本地使用，不会进入发布输出。
