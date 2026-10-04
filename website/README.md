# SpeakLog 产品介绍页

纯静态页面，没有构建步骤，整个 `website/` 目录直接部署到任意静态托管（Cloudflare Pages、GitHub Pages、Netlify、Vercel 等）的站点根目录即可。

## 多语言

| 路径 | 语言 | 示例内容 |
|---|---|---|
| `/` | 简体中文 | 学日语的例句，中文解释 |
| `/en/` | English | 学日语的例句，英文解释 |
| `/ja/` | 日本語 | 学英语的例句，日文解释（日本用户多半在学英语） |

- 每种语言是一个独立的 HTML 文件，搜索引擎能分别收录；页面之间用 `hreflang` 互相标注，`x-default`（不匹配任何语言的访客）指向英文版。
- 不按浏览器语言自动跳转（会妨碍搜索引擎抓取），访客用右上角的语言切换。
- 样式和脚本是三种语言共用的：`assets/site.css`、`assets/site.js`、`assets/analytics.js`。
- 改文案时三个文件要一起改；常见问题改了，同一个文件里 JSON-LD 的 `FAQPage` 也要跟着改。
- 新增语言：复制一份目录（比如 `ko/index.html`）翻译，然后在**所有**页面的 `hreflang` 和语言切换里加上它，`sitemap.xml` 里也加一组，`make-og.swift` 里加一张分享图。

## 文件

| 文件 | 作用 |
|---|---|
| `index.html`、`en/index.html`、`ja/index.html` | 页面：SEO meta、Open Graph / Twitter 卡片、JSON-LD（WebSite、SoftwareApplication、FAQPage） |
| `404.html` | 不存在的路径返回真正的 404（没有它 Pages 会把任何路径都当首页返回） |
| `deploy.sh` | 部署到 Cloudflare Pages |
| `assets/analytics.js` | GA4，衡量 ID 只写在这里 |
| `assets/site.css`、`assets/site.js` | 共用样式；逐词高亮演示和统计事件 |
| `robots.txt`、`sitemap.xml` | 给搜索引擎，sitemap 里带各语言版本的对应关系 |
| `site.webmanifest`、`assets/icon-*.png` | 网站图标，由应用源码仓库里的 `build/icon-1024.png` 缩放 |
| `assets/og.png`、`og-en.png`、`og-ja.png` | 各语言的 1200×630 社交分享图，由 `make-og.swift` 生成 |

## 部署

部署在 Cloudflare Pages 项目 `speaklog`，域名 https://speak.erzhiqian.cc （备用地址 https://speaklog.pages.dev ）。

```bash
website/deploy.sh
```

脚本把站点文件复制到临时目录（不带 `README.md`、`deploy.sh`、`make-og.swift`），再用 `wrangler pages deploy` 上传。需要 Node，并且已经用 `npx wrangler login` 登录 Cloudflare。

## 统计

**GA4 衡量 ID** `G-MB3812Z1TL`，只在 `assets/analytics.js`。换 ID 时改这一处，再把三个页面和 `404.html` 里 `analytics.js` 的 `?v=` 加一（见下文），然后部署。

## 统计的事件

除了 GA4 默认的页面浏览和增强型衡量，页面还会发（`page_language` 会随页面浏览一起上报，可以按语言拆分）：

| 事件 | 参数 | 触发 |
|---|---|---|
| `cta_click` | `location`（header / hero / hero_secondary）、`link_text` | 点「获取 Mac 版」「看看怎么用」 |
| `download_click` | `location`、`link_text` | 点底部下载按钮 |
| `language_switch` | `location`（目标语言） | 点语言切换 |
| `faq_open` | `question` | 展开常见问题 |

给任意链接加 `data-track="事件名" data-track-location="位置"` 就能多统计一个点击。

如果面向欧盟 / 英国用户，需要另外加 Cookie 同意横幅并接入 Google Consent Mode。

## 本地预览和重新生成

```bash
python3 -m http.server 8765 --directory website
```

```bash
swift website/make-og.swift <源码仓库>/build/icon-1024.png website/assets
```

改了页面内容后，记得同步更新 `sitemap.xml` 的 `lastmod`。改了 `assets/` 里的 CSS / JS 后，把三个页面里的 `?v=3` 加一，否则访客浏览器可能还在用缓存的旧文件：

```bash
sed -i '' 's/?v=3"/?v=4"/g' website/index.html website/en/index.html website/ja/index.html website/404.html
```
