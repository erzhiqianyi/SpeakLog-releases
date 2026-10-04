**English** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

# SpeakLog

**Speak first. Polish it later.**

SpeakLog is a Mac app for language learners: import or record yourself speaking a foreign language, transcribe it on your Mac, compare what you said with a more natural version, and export subtitles, a study blog post and word-highlighted subtitle videos.

Website: https://speak.erzhiqian.cc/en/

## Download

| | |
|---|---|
| **Installer (recommended)** | [SpeakLog.pkg](https://github.com/erzhiqianyi/SpeakLog-releases/releases/latest/download/SpeakLog.pkg): double-click to install into Applications |
| Disk image | Download `SpeakLog-<version>.dmg` from [Releases](https://github.com/erzhiqianyi/SpeakLog-releases/releases/latest) and drag the app into Applications |
| Previous versions | [All releases](https://github.com/erzhiqianyi/SpeakLog-releases/releases), each with `SHA256SUMS` |

Version 0.1.1 requires an Apple silicon Mac (M-series chip) running macOS 26 or later. The current package does not support Intel Macs. The installer and disk image are signed with a Developer ID and notarized by Apple.

## Guides

- [Get started](https://speak.erzhiqian.cc/en/guides/getting-started/)
- [Speaking practice](https://speak.erzhiqian.cc/en/guides/speaking-practice/)
- [Export subtitles, blogs and video](https://speak.erzhiqian.cc/en/guides/export/)
- [Privacy and data flow](https://speak.erzhiqian.cc/en/privacy/)

Transcription, rendering and export run locally. Cloud AI features send relevant text and context to the selected provider; visual analysis passes sampled frames or photos to Claude Code or Codex, including when the global provider is the on-device model. Automatic AI review is on by default; check Settings → AI before importing private content.

## What's in this repository

- **Releases**: the PKG, DMG, checksums and release notes for every version.
- **`website/`**: the static pages of speak.erzhiqian.cc (Simplified Chinese, English, Japanese). See [`website/README.md`](website/README.md) for deployment (in Chinese).

The app's source code is not here.

## Contact

- X: [@itsuki_maer](https://x.com/itsuki_maer)
- Email: [speaklog@erzhiqian.cc](mailto:speaklog@erzhiqian.cc)

Questions and suggestions are also welcome as issues in this repository.
