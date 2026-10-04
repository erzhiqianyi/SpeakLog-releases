[English](README.md) · **简体中文** · [日本語](README.ja.md)

# SpeakLog

**先说出来，再慢慢改好。**

SpeakLog 是给外语学习者的 Mac 应用：导入或录下你用外语说的话，本机转录，对照原话和更自然的说法，导出字幕、学习博客和逐词高亮的字幕视频。

官网：https://speak.erzhiqian.cc

## 下载

| | |
|---|---|
| **安装包（推荐）** | [SpeakLog.pkg](https://github.com/erzhiqianyi/SpeakLog-releases/releases/latest/download/SpeakLog.pkg)：双击安装到「应用程序」 |
| 磁盘映像 | 在 [Releases](https://github.com/erzhiqianyi/SpeakLog-releases/releases/latest) 下载 `SpeakLog-<版本>.dmg`，把应用拖进「应用程序」 |
| 历史版本 | [全部 Releases](https://github.com/erzhiqianyi/SpeakLog-releases/releases)，每个版本附 `SHA256SUMS` |

0.1.1 需要 Apple silicon Mac（M 系列芯片）及 macOS 26 或更高版本。当前安装包不支持 Intel Mac。安装包和磁盘映像都用 Developer ID 签名并经过 Apple 公证。

## 使用指南

- [开始使用](https://speak.erzhiqian.cc/guides/getting-started/)
- [完成一次口语练习](https://speak.erzhiqian.cc/guides/speaking-practice/)
- [导出字幕、博客和视频](https://speak.erzhiqian.cc/guides/export/)
- [隐私与数据流](https://speak.erzhiqian.cc/privacy/)

转录、渲染和导出在本机执行。云端 AI 功能会发送所需文字和上下文；画面分析会把抽取的帧或照片交给 Claude Code 或 Codex，即使全局选择端侧模型也是如此。自动 AI 校对默认开启，导入私人内容前请检查「设置 → AI」。

## 这个仓库里有什么

- **Releases**：每个版本的 PKG、DMG、校验和与更新说明。
- **`website/`**：官网 speak.erzhiqian.cc 的静态页面（简体中文、English、日本語），部署方式见 [`website/README.md`](website/README.md)。

应用的源码不在这里。

## 联系

- X：[@itsuki_maer](https://x.com/itsuki_maer)
- 邮件：[speaklog@erzhiqian.cc](mailto:speaklog@erzhiqian.cc)

问题和建议也可以直接在本仓库开 Issue。
